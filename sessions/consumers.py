import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Session, RoomToken

User = get_user_model()

class SessionConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for WebRTC signaling and session updates"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'session_{self.session_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Verify user has access to this session
        has_access = await self.verify_session_access()
        if not has_access:
            await self.close()
            return
        
        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_mentor': self.user.is_mentor,
            }
        )
    
    async def disconnect(self, close_code):
        # Notify others that user left
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
        
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'webrtc_offer':
                await self.handle_webrtc_offer(data)
            elif message_type == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif message_type == 'ice_candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'ready_check':
                await self.handle_ready_check(data)
        except json.JSONDecodeError:
            pass
    
    async def handle_webrtc_offer(self, data):
        """Forward WebRTC offer to other participants"""
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'offer',
                'offer': data.get('offer'),
                'from_user': str(self.user.id),
                'to_user': data.get('to_user'),
            }
        )
    
    async def handle_webrtc_answer(self, data):
        """Forward WebRTC answer to other participants"""
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'answer',
                'answer': data.get('answer'),
                'from_user': str(self.user.id),
                'to_user': data.get('to_user'),
            }
        )
    
    async def handle_ice_candidate(self, data):
        """Forward ICE candidate to other participants"""
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'webrtc_signal',
                'signal_type': 'ice_candidate',
                'candidate': data.get('candidate'),
                'from_user': str(self.user.id),
                'to_user': data.get('to_user'),
            }
        )
    
    async def handle_chat_message(self, data):
        """Handle chat messages during session"""
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'chat_message',
                'message': data.get('message'),
                'username': self.user.username,
                'user_id': str(self.user.id),
                'timestamp': data.get('timestamp'),
            }
        )
    
    async def handle_ready_check(self, data):
        """Handle ready status updates"""
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'ready_status',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'is_ready': data.get('is_ready'),
                'is_mentor': self.user.is_mentor,
            }
        )
    
    # Group message handlers
    async def user_joined(self, event):
        """Send user joined notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_mentor': event['is_mentor'],
        }))
    
    async def user_left(self, event):
        """Send user left notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def webrtc_signal(self, event):
        """Forward WebRTC signaling messages"""
        # Only send to intended recipient or broadcast if no specific recipient
        to_user = event.get('to_user')
        if not to_user or to_user == str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'webrtc_signal',
                'signal_type': event['signal_type'],
                'from_user': event['from_user'],
                **{k: v for k, v in event.items() if k not in ['type', 'signal_type', 'from_user']}
            }))
    
    async def chat_message(self, event):
        """Send chat message to all participants"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
        }))
    
    async def ready_status(self, event):
        """Send ready status update"""
        await self.send(text_data=json.dumps({
            'type': 'ready_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_ready': event['is_ready'],
            'is_mentor': event['is_mentor'],
        }))
    
    @database_sync_to_async
    def verify_session_access(self):
        """Verify if user has access to this session"""
        try:
            session = Session.objects.get(id=self.session_id)
            
            # Mentor always has access
            if self.user == session.mentor:
                return True
            
            # Learner needs confirmed booking
            if self.user.is_learner:
                from .models import Booking
                booking = Booking.objects.filter(
                    learner=self.user,
                    session=session,
                    status='confirmed'
                ).exists()
                return booking
            
            return False
        except Session.DoesNotExist:
            return False

class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for dashboard real-time updates"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.dashboard_group_name = f'dashboard_{self.user.role}'
        
        # Join dashboard group
        await self.channel_layer.group_add(
            self.dashboard_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave dashboard group
        await self.channel_layer.group_discard(
            self.dashboard_group_name,
            self.channel_name
        )
    
    async def session_update(self, event):
        """Send session updates to dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'session_update',
            'session_id': event['session_id'],
            'status': event['status'],
            'participants': event.get('participants'),
        }))
    
    async def booking_update(self, event):
        """Send booking updates to dashboard"""
        await self.send(text_data=json.dumps({
            'type': 'booking_update',
            'booking_id': event['booking_id'],
            'session_id': event['session_id'],
            'status': event['status'],
        }))
