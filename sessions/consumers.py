import json
import uuid
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from django.core.cache import cache
from django.db.models import Q
from .models import Session, RoomToken, SessionParticipant

User = get_user_model()
logger = logging.getLogger(__name__)

class SessionConsumer(AsyncWebsocketConsumer):
    """Enhanced WebSocket consumer for WebRTC signaling and session updates with Zoom-like features"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'session_{self.session_id}'
        self.user = self.scope['user']
        self.user_id = str(self.user.id)
        self.connection_id = str(uuid.uuid4())
        
        logger.info(f"User {self.user_id} ({self.user.username}) attempting to connect to session {self.session_id}")
        
        if not self.user.is_authenticated:
            logger.warning(f"Unauthenticated user attempted to connect to session {self.session_id}")
            await self.close(code=4001)
            return
        
        # Verify user has access to this session
        has_access = await self.verify_session_access()
        if not has_access:
            logger.warning(f"User {self.user_id} denied access to session {self.session_id}")
            await self.close(code=4003)
            return
        
        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user_id} ({self.user.username}) successfully connected to session {self.session_id}")
        
        # Mark user as active participant
        await self.mark_user_joined()
        
        # Send current session state
        session_data = await self.send_session_state()
        await self.send(text_data=json.dumps({
            'type': 'session_state',
            'data': session_data,
            'timestamp': timezone.now().isoformat(),
        }))
        
        # Get current participants for logging
        participants = await self.get_active_participants()
        logger.info(f"Current participants in session {self.session_id}: {[p['username'] for p in participants]}")
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_mentor': getattr(self.user, 'is_mentor', False),
                'connection_id': self.connection_id,
                'join_time': timezone.now().isoformat(),
            }
        )
        
        # Start connection monitoring
        asyncio.create_task(self.monitor_connection())
    
    async def disconnect(self, close_code):
        logger.info(f"User {self.user_id} disconnecting from session {self.session_id} with code {close_code}")
        
        # Mark user as left
        await self.mark_user_left()
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_left',
                'user_id': self.user_id,
                'username': self.user.username,
                'connection_id': self.connection_id,
                'leave_time': timezone.now().isoformat(),
                'reason': self._get_disconnect_reason(close_code),
            }
        )
        
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )
        
        # Clean up cache entries
        cache.delete(f'user_connection_{self.user_id}_{self.session_id}')
        
        logger.info(f"User {self.user_id} disconnected from session {self.session_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.debug(f"Received {message_type} from user {self.user_id} in session {self.session_id}")
            
            # Update last activity
            await self.update_last_activity()
            
            # Route message to appropriate handler
            message_handlers = {
                'webrtc_offer': self.handle_webrtc_offer,
                'webrtc_answer': self.handle_webrtc_answer,
                'ice_candidate': self.handle_ice_candidate,
                'chat_message': self.handle_chat_message,
                'ready_check': self.handle_ready_check,
                'network_quality': self.handle_network_quality,
                'audio_level': self.handle_audio_level,
                'live_assurance': self.handle_live_assurance,
                'user_status': self.handle_user_status,
                'screen_share': self.handle_screen_share,
                'recording_status': self.handle_recording_status,
                'user_presence': self.handle_user_presence,
                'pong': self.handle_pong,
                'connection_test': self.handle_connection_test,
                'peer_discovery': self.handle_peer_discovery,
                'bandwidth_test': self.handle_bandwidth_test,
                'get_session_state': self.handle_get_session_state,
                'connection_status_update': self.handle_connection_status_update,
            }
            
            handler = message_handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                logger.warning(f"Unknown message type {message_type} from user {self.user_id}")
                await self.send_error("Unknown message type")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from user {self.user_id}: {text_data}")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message from user {self.user_id}: {str(e)}")
            await self.send_error("Message processing error")

    async def handle_webrtc_offer(self, data):
        """Forward WebRTC offer to specific peer or all participants"""
        target_user = data.get('to_user')
        
        # Validate offer data
        if not data.get('offer'):
            await self.send_error("Invalid offer data")
            return
        
        # Store offer in cache for reliability
        cache_key = f'webrtc_offer_{self.user_id}_{target_user or "broadcast"}_{self.session_id}'
        cache.set(cache_key, data.get('offer'), timeout=300)  # 5 minutes
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'offer',
                'offer': data.get('offer'),
                'from_user': self.user_id,
                'to_user': target_user,
                'connection_id': self.connection_id,
                'timestamp': timezone.now().isoformat(),
            }
        )
        
        logger.info(f"WebRTC offer sent from {self.user_id} to {target_user or 'all'} in session {self.session_id}")

    async def handle_webrtc_answer(self, data):
        """Forward WebRTC answer to specific peer"""
        target_user = data.get('to_user')
        
        if not data.get('answer') or not target_user:
            await self.send_error("Invalid answer data")
            return
        
        # Store answer in cache
        cache_key = f'webrtc_answer_{self.user_id}_{target_user}_{self.session_id}'
        cache.set(cache_key, data.get('answer'), timeout=300)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'answer',
                'answer': data.get('answer'),
                'from_user': self.user_id,
                'to_user': target_user,
                'connection_id': self.connection_id,
                'timestamp': timezone.now().isoformat(),
            }
        )
        
        logger.info(f"WebRTC answer sent from {self.user_id} to {target_user} in session {self.session_id}")

    async def handle_ice_candidate(self, data):
        """Forward ICE candidate to specific peer"""
        target_user = data.get('to_user')
        candidate = data.get('candidate')
        
        if not candidate:
            await self.send_error("Invalid ICE candidate")
            return
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'ice_candidate',
                'candidate': candidate,
                'from_user': self.user_id,
                'to_user': target_user,
                'connection_id': self.connection_id,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_chat_message(self, data):
        """Handle chat messages during session with enhanced features"""
        message = data.get('message', '').strip()
        message_type = data.get('message_type', 'text')
        
        if not message:
            return
        
        # Validate message length
        if len(message) > 1000:
            await self.send_error("Message too long")
            return
        
        message_id = str(uuid.uuid4())
        
        # Store message in cache for message history
        cache_key = f'chat_message_{self.session_id}_{message_id}'
        cache.set(cache_key, {
            'message': message,
            'user_id': self.user_id,
            'username': self.user.username,
            'message_type': message_type,
            'timestamp': timezone.now().isoformat()
        }, timeout=3600)  # 1 hour
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'chat_message',
                'message_id': message_id,
                'message': message,
                'username': self.user.username,
                'user_id': self.user_id,
                'message_type': message_type,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_ready_check(self, data):
        """Handle ready status updates with validation"""
        is_ready = data.get('is_ready', False)
        
        # Update participant ready status
        await self.update_participant_ready_status(is_ready)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'ready_status',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_ready': is_ready,
                'is_mentor': self.user.is_mentor,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_network_quality(self, data):
        """Handle network quality updates with metrics"""
        quality = data.get('quality', 'High')
        packet_loss = data.get('packet_loss', 0.0)
        latency = data.get('latency', 0.0)
        bandwidth = data.get('bandwidth', 0.0)
        
        # Update network metrics in database
        await self.update_network_metrics(quality, packet_loss, latency, bandwidth)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'network_quality_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'quality': quality,
                'packet_loss': packet_loss,
                'latency': latency,
                'bandwidth': bandwidth,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_connection_test(self, data):
        """Handle connection test requests"""
        test_id = data.get('test_id')
        await self.send(text_data=json.dumps({
            'type': 'connection_test_response',
            'test_id': test_id,
            'timestamp': timezone.now().isoformat(),
            'server_time': timezone.now().isoformat(),
        }))

    async def handle_peer_discovery(self, data):
        """Handle peer discovery requests"""
        active_peers = await self.get_active_participants()
        await self.send(text_data=json.dumps({
            'type': 'peer_discovery_response',
            'peers': active_peers,
            'timestamp': timezone.now().isoformat(),
        }))

    async def handle_bandwidth_test(self, data):
        """Handle bandwidth test data"""
        test_data = data.get('test_data', '')
        test_size = len(test_data.encode('utf-8'))
        
        await self.send(text_data=json.dumps({
            'type': 'bandwidth_test_response',
            'received_size': test_size,
            'timestamp': timezone.now().isoformat(),
        }))

    async def handle_live_assurance(self, data):
        """Handle live assurance pings from frontend"""
        user_id = str(self.user.id)
        username = self.user.username
        
        # Update last activity
        await self.update_last_activity()
        
        # Broadcast live assurance to other participants
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'live_assurance_ping',
                'user_id': user_id,
                'username': username,
                'timestamp': timezone.now().isoformat(),
                'is_mentor': self.user.is_mentor,
                'connection_status': 'active'
            }
        )
        
        # Send response back to sender
        await self.send(text_data=json.dumps({
            'type': 'live_assurance_response',
            'user_id': user_id,
            'timestamp': timezone.now().isoformat(),
            'status': 'active'
        }))

    async def handle_user_status(self, data):
        """Handle user status updates (muted, video off, etc.)"""
        status_type = data.get('status_type')
        status_value = data.get('status_value', False)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_status_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'status_type': status_type,
                'status_value': status_value,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_screen_share(self, data):
        """Handle screen sharing status updates"""
        is_sharing = data.get('is_sharing', False)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'screen_share_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_sharing': is_sharing,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_recording_status(self, data):
        """Handle recording status updates"""
        is_recording = data.get('is_recording', False)
        
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'recording_status_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_recording': is_recording,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_user_presence(self, data):
        """Handle user presence updates"""
        user_role = data.get('user_role')
        is_ready = data.get('is_ready', False)
        
        # Send user joined notification to other participants
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_mentor': self.user.is_mentor,
                'join_time': timezone.now().isoformat(),
            }
        )

    async def handle_pong(self, data):
        """Handle pong responses to ping"""
        # Calculate latency if timestamp provided
        if 'timestamp' in data:
            try:
                # Use timezone.now() for both times to ensure consistency
                current_time = timezone.now()
                # Simple latency acknowledgment logging
                logger.debug(f"Pong received from user {self.user_id} at {current_time.isoformat()}")
            except Exception as e:
                logger.warning(f"Error processing pong from user {self.user_id}: {e}")
                pass

    async def handle_audio_level(self, data):
        """Handle audio level updates from participants"""
        level = data.get('level', 0)
        quality = data.get('quality', 'Silent')
        
        # Broadcast audio level to other participants
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'audio_level_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'level': level,
                'quality': quality,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def handle_get_session_state(self, data):
        """Handle request for current session state"""
        session_data = await self.send_session_state()
        await self.send(text_data=json.dumps({
            'type': 'session_state',
            'data': session_data,
            'timestamp': timezone.now().isoformat(),
        }))

    async def handle_connection_status_update(self, data):
        """Handle connection status updates from clients"""
        status = data.get('status', 'unknown')
        
        # Broadcast connection status to other participants
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'connection_status_update',
                'user_id': self.user_id,
                'username': self.user.username,
                'status': status,
                'timestamp': timezone.now().isoformat(),
            }
        )

    async def send_error(self, error_message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message,
            'timestamp': timezone.now().isoformat(),
        }))

    async def monitor_connection(self):
        """Monitor connection quality and send periodic updates"""
        while True:
            try:
                # Update connection status in cache
                cache.set(f'user_connection_{self.user_id}_{self.session_id}', {
                    'last_seen': timezone.now().isoformat(),
                    'connection_id': self.connection_id,
                    'channel_name': self.channel_name
                }, timeout=300)
                
                # Send periodic ping
                await self.send(text_data=json.dumps({
                    'type': 'ping',
                    'timestamp': timezone.now().isoformat(),
                }))
                
                await asyncio.sleep(30)  # Ping every 30 seconds
                
            except Exception as e:
                logger.error(f"Connection monitoring error for user {self.user_id}: {e}")
                break

    def _get_disconnect_reason(self, close_code: int) -> str:
        """Get human-readable disconnect reason"""
        reasons = {
            1000: "Normal closure",
            1001: "Going away",
            1002: "Protocol error",
            1003: "Unsupported data",
            1006: "Abnormal closure",
            4001: "Unauthorized",
            4003: "Forbidden",
        }
        return reasons.get(close_code, f"Unknown ({close_code})")

    @database_sync_to_async
    def verify_session_access(self):
        """Verify if user has access to this session with enhanced checks"""
        try:
            session = Session.objects.get(id=self.session_id)
            
            # Check if user is mentor
            if session.mentor == self.user:
                return True
            
            # Check if user has a valid booking
            from .models import Booking
            valid_statuses = ['confirmed', 'booked', 'attended']
            
            booking = Booking.objects.filter(
                session=session, 
                learner=self.user,
                status__in=valid_statuses
            ).first()
            
            if booking:
                return True
            
            # Allow access if session is live and user has any booking history
            if session.status == 'live':
                has_any_booking = Booking.objects.filter(
                    session=session, 
                    learner=self.user
                ).exists()
                return has_any_booking
            
            return False
            
        except Session.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_user_joined(self):
        """Mark user as joined to session with enhanced tracking"""
        try:
            session = Session.objects.get(id=self.session_id)
            
            # Remove any existing disconnected participants for this user first
            SessionParticipant.objects.filter(
                session=session,
                user=self.user,
                connection_status='disconnected'
            ).delete()
            
            participant, created = SessionParticipant.objects.get_or_create(
                session=session,
                user=self.user,
                defaults={
                    'is_mentor': self.user.is_mentor,
                    'connection_status': 'connected',
                    'joined_at': timezone.now()
                }
            )
            
            if not created:
                # Update existing participant record
                participant.joined_at = timezone.now()
                participant.left_at = None
                participant.connection_status = 'connected'
                if participant.connection_status == 'disconnected':
                    participant.reconnection_count += 1
                participant.save()
                logger.info(f"User {self.user_id} reconnected to session {self.session_id}")
            else:
                logger.info(f"User {self.user_id} joined session {self.session_id} for the first time")
                
            # Note: current_participants is a property that auto-calculates
            logger.info(f"Session {self.session_id} now has {session.current_participants} active participants")
                
        except Session.DoesNotExist:
            logger.error(f"Session {self.session_id} not found when marking user joined")

    @database_sync_to_async
    def update_network_metrics(self, quality: str, packet_loss: float, latency: float, bandwidth: float):
        """Update network quality metrics"""
        try:
            session = Session.objects.get(id=self.session_id)
            participant = SessionParticipant.objects.get(session=session, user=self.user)
            
            participant.network_quality = quality
            participant.packet_loss = packet_loss
            participant.latency = latency
            participant.bandwidth = bandwidth
            participant.save()
            
        except (Session.DoesNotExist, SessionParticipant.DoesNotExist):
            logger.error(f"Could not update network metrics for user {self.user_id} in session {self.session_id}")

    @database_sync_to_async
    def get_active_participants(self):
        """Get list of active participants"""
        try:
            session = Session.objects.get(id=self.session_id)
            participants = SessionParticipant.objects.filter(
                session=session,
                left_at__isnull=True,
                connection_status='connected'
            ).select_related('user')
            
            return [
                {
                    'user_id': str(p.user.id),
                    'username': p.user.username,
                    'is_mentor': p.is_mentor,
                    'connection_status': p.connection_status,
                    'network_quality': p.network_quality,
                }
                for p in participants
            ]
            
        except Session.DoesNotExist:
            return []

    @database_sync_to_async
    def mark_user_left(self):
        """Mark user as left from session"""
        try:
            session = Session.objects.get(id=self.session_id)
            participant = SessionParticipant.objects.filter(
                session=session,
                user=self.user
            ).first()
            
            if participant:
                participant.left_at = timezone.now()
                participant.connection_status = 'disconnected'
                participant.save()
                
            # Note: current_participants property auto-calculates
            logger.info(f"User {self.user_id} left session {self.session_id}. Active participants: {session.current_participants}")
                
        except Session.DoesNotExist:
            logger.error(f"Session {self.session_id} not found when marking user left")

    @database_sync_to_async
    def update_participant_ready_status(self, is_ready: bool):
        """Update participant ready status"""
        try:
            session = Session.objects.get(id=self.session_id)
            participant = SessionParticipant.objects.get(session=session, user=self.user)
            participant.is_ready = is_ready
            participant.save()
        except (Session.DoesNotExist, SessionParticipant.DoesNotExist):
            logger.error(f"Could not update ready status for user {self.user_id} in session {self.session_id}")

    @database_sync_to_async
    def send_session_state(self):
        """Send current session state to user"""
        try:
            session = Session.objects.get(id=self.session_id)
            participants = SessionParticipant.objects.filter(
                session=session,
                left_at__isnull=True
            ).select_related('user')
            
            session_data = {
                'session_id': str(session.id),
                'title': session.title,
                'status': session.status,
                'participants': [
                    {
                        'user_id': str(p.user.id),
                        'username': p.user.username,
                        'is_mentor': p.is_mentor,
                        'is_ready': getattr(p, 'is_ready', False),
                        'connection_status': p.connection_status,
                        'network_quality': p.network_quality,
                    }
                    for p in participants if p.user != self.user
                ]
            }
            
            return session_data
            
        except Session.DoesNotExist:
            return {}

    @database_sync_to_async
    def update_last_activity(self):
        """Update user's last activity timestamp"""
        try:
            session = Session.objects.get(id=self.session_id)
            participant = SessionParticipant.objects.filter(
                session=session,
                user=self.user
            ).first()
            
            if participant:
                participant.last_activity = timezone.now()
                participant.save()
                
        except Session.DoesNotExist:
            pass

    # Group message handlers
    async def user_joined(self, event):
        """Send user joined notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_mentor': event.get('is_mentor', False),
            'join_time': event.get('join_time', timezone.now().isoformat()),
        }))
    
    async def user_left(self, event):
        """Send user left notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
            'leave_time': event['leave_time'],
        }))
    
    async def webrtc_signal(self, event):
        """Forward WebRTC signaling messages"""
        # Only send to intended recipient or broadcast if no specific recipient
        to_user = event.get('to_user')
        if not to_user or to_user == self.user_id:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_signal',
                'signal_type': event['signal_type'],
                'from_user': event['from_user'],
                'timestamp': event['timestamp'],
                **{k: v for k, v in event.items() if k not in ['type', 'signal_type', 'from_user', 'timestamp']}
            }))
    
    async def chat_message(self, event):
        """Send chat message to all participants"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message_type': event['message_type'],
        }))
    
    async def ready_status(self, event):
        """Send ready status update"""
        await self.send(text_data=json.dumps({
            'type': 'ready_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_ready': event['is_ready'],
            'is_mentor': event['is_mentor'],
            'timestamp': event['timestamp'],
        }))
    
    async def network_quality_update(self, event):
        """Send network quality update"""
        await self.send(text_data=json.dumps({
            'type': 'network_quality_update',
            'user_id': event['user_id'],
            'username': event['username'],
            'quality': event['quality'],
            'timestamp': event['timestamp'],
        }))
    
    async def live_assurance_ping(self, event):
        """Send live assurance ping"""
        await self.send(text_data=json.dumps({
            'type': 'live_assurance_ping',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))
    
    async def user_status_update(self, event):
        """Send user status update"""
        await self.send(text_data=json.dumps({
            'type': 'user_status_update',
            'user_id': event['user_id'],
            'username': event['username'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }))
    
    async def screen_share_update(self, event):
        """Send screen share update"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share_update',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_sharing': event['is_sharing'],
            'timestamp': event['timestamp'],
        }))
    
    async def recording_status_update(self, event):
        """Send recording status update"""
        await self.send(text_data=json.dumps({
            'type': 'recording_status_update',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_recording': event['is_recording'],
            'timestamp': event['timestamp'],
        }))
    
    async def session_state_update(self, event):
        """Send session state update"""
        await self.send(text_data=json.dumps({
            'type': 'session_state_update',
            'session_state': event['session_state'],
            'timestamp': event['timestamp'],
        }))

    async def audio_level_update(self, event):
        """Send audio level update"""
        await self.send(text_data=json.dumps({
            'type': 'audio_level',
            'user_id': event['user_id'],
            'username': event['username'],
            'level': event['level'],
            'quality': event['quality'],
            'timestamp': event['timestamp'],
        }))

    async def mentor_ready(self, event):
        """Handle mentor ready status - FIXED: Added missing handler"""
        await self.send(text_data=json.dumps({
            'type': 'mentor_ready',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_ready': event.get('is_ready', True),
            'timestamp': event['timestamp'],
        }))

    async def session_started(self, event):
        """Handle session started notification"""
        await self.send(text_data=json.dumps({
            'type': 'session_started',
            'session_id': event['session_id'],
            'message': event.get('message', 'Session has started!'),
            'timestamp': event['timestamp'],
        }))

    async def connection_status_update(self, event):
        """Handle connection status updates"""
        await self.send(text_data=json.dumps({
            'type': 'connection_status_update',
            'user_id': event['user_id'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }))

class DashboardConsumer(AsyncWebsocketConsumer):
    """Enhanced dashboard consumer for real-time updates"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        self.dashboard_group_name = f'dashboard_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.dashboard_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard state
        await self.send_dashboard_state()
        
        logger.info(f"User {self.user.id} connected to dashboard")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.dashboard_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.id} disconnected from dashboard")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_notification_read':
                await self.mark_notification_read(data.get('notification_id'))
            elif message_type == 'get_dashboard_update':
                await self.send_dashboard_state()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def send_dashboard_state(self):
        """Send current dashboard state"""
        dashboard_data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps({
            'type': 'dashboard_state',
            'data': dashboard_data,
            'timestamp': timezone.now().isoformat(),
        }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """Get dashboard data for the user"""
        try:
            from .models import Notification
            
            # Get unread notifications
            unread_notifications = Notification.objects.filter(
                user=self.user,
                read=False
            ).count()
            
            # Get upcoming sessions
            upcoming_sessions = Session.objects.filter(
                Q(mentor=self.user) | Q(bookings__learner=self.user),
                schedule__gte=timezone.now(),
                status='scheduled'
            ).distinct().count()
            
            return {
                'unread_notifications': unread_notifications,
                'upcoming_sessions': upcoming_sessions,
                'user_role': self.user.role,
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    # Group message handlers
    async def session_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def booking_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def notification(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            from .models import Notification
            Notification.objects.filter(
                id=notification_id,
                user=self.user
            ).update(read=True)
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
