/**
 * PeerLearn WebRTC Implementation
 * Handles peer-to-peer video/audio connections and signaling
 */

function webRTCRoom(sessionId, roomToken, isMentor) {
    return {
        // Connection state
        localStream: null,
        remoteStreams: new Map(),
        peerConnections: new Map(),
        dataChannels: new Map(),
        socket: null,
        
        // UI state
        participants: {},
        audioEnabled: true,
        videoEnabled: true,
        screenSharing: false,
        chatVisible: true,
        chatMessages: [],
        newMessage: '',
        connectionStatus: 'connecting',
        sessionDuration: '00:00',
        
        // Session info
        sessionId: sessionId,
        roomToken: roomToken,
        isMentor: isMentor,
        userId: null,
        username: null,
        
        // Timers
        sessionStartTime: null,
        durationTimer: null,
        
        // WebRTC Configuration
        rtcConfig: {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' },
                { urls: 'stun:stun3.l.google.com:19302' },
                { urls: 'stun:stun4.l.google.com:19302' }
            ],
            iceCandidatePoolSize: 10
        },
        
        async initRoom() {
            try {
                console.log('Initializing WebRTC room...');
                
                // Get user media
                await this.getUserMedia();
                
                // Connect to WebSocket
                this.connectWebSocket();
                
                // Start session timer
                this.startSessionTimer();
                
                // Initialize UI
                this.initializeUI();
                
                console.log('WebRTC room initialized successfully');
            } catch (error) {
                console.error('Error initializing room:', error);
                this.handleError('Failed to initialize room: ' + error.message);
            }
        },
        
        async getUserMedia() {
            try {
                const constraints = {
                    video: {
                        width: { ideal: 1280 },
                        height: { ideal: 720 },
                        frameRate: { ideal: 30 }
                    },
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                };
                
                this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
                
                // Display local video
                const localVideo = document.getElementById('localVideo');
                if (localVideo) {
                    localVideo.srcObject = this.localStream;
                }
                
                console.log('Got user media successfully');
            } catch (error) {
                console.error('Error getting user media:', error);
                throw new Error('Camera/microphone access denied. Please allow access and refresh the page.');
            }
        },
        
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/sessions/${this.sessionId}/`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.connectionStatus = 'connected';
                
                // Send initial ready status
                this.sendWebSocketMessage({
                    type: 'ready_check',
                    is_ready: true
                });
            };
            
            this.socket.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };
            
            this.socket.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                this.connectionStatus = 'disconnected';
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => {
                    if (this.connectionStatus === 'disconnected') {
                        console.log('Attempting to reconnect...');
                        this.connectWebSocket();
                    }
                }, 3000);
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.connectionStatus = 'error';
            };
        },
        
        async handleWebSocketMessage(data) {
            console.log('WebSocket message received:', data.type);
            
            try {
                switch (data.type) {
                    case 'user_joined':
                        await this.handleUserJoined(data);
                        break;
                    case 'user_left':
                        this.handleUserLeft(data);
                        break;
                    case 'webrtc_signal':
                        await this.handleWebRTCSignal(data);
                        break;
                    case 'chat_message':
                        this.handleChatMessage(data);
                        break;
                    case 'ready_status':
                        this.handleReadyStatus(data);
                        break;
                    default:
                        console.log('Unknown message type:', data.type);
                }
            } catch (error) {
                console.error('Error handling WebSocket message:', error);
            }
        },
        
        async handleUserJoined(data) {
            console.log('User joined:', data.username);
            
            // Add participant to UI
            this.participants[data.user_id] = {
                username: data.username,
                is_mentor: data.is_mentor,
                audioEnabled: true,
                videoEnabled: true
            };
            
            // Create peer connection for new user
            await this.createPeerConnection(data.user_id);
            
            // If we're not the new user, create an offer
            if (data.user_id !== this.userId) {
                await this.createOffer(data.user_id);
            }
        },
        
        handleUserLeft(data) {
            console.log('User left:', data.username);
            
            // Remove participant from UI
            delete this.participants[data.user_id];
            
            // Close peer connection
            if (this.peerConnections.has(data.user_id)) {
                this.peerConnections.get(data.user_id).close();
                this.peerConnections.delete(data.user_id);
            }
            
            // Remove remote video
            const remoteVideo = document.getElementById(`remoteVideo-${data.user_id}`);
            if (remoteVideo) {
                remoteVideo.srcObject = null;
            }
        },
        
        async handleWebRTCSignal(data) {
            const { signal_type, from_user } = data;
            
            console.log(`Received ${signal_type} from ${from_user}`);
            
            switch (signal_type) {
                case 'offer':
                    await this.handleOffer(data);
                    break;
                case 'answer':
                    await this.handleAnswer(data);
                    break;
                case 'ice_candidate':
                    await this.handleIceCandidate(data);
                    break;
            }
        },
        
        async createPeerConnection(userId) {
            const peerConnection = new RTCPeerConnection(this.rtcConfig);
            
            // Add local stream tracks
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => {
                    peerConnection.addTrack(track, this.localStream);
                });
            }
            
            // Handle remote stream
            peerConnection.ontrack = (event) => {
                console.log('Received remote track from:', userId);
                const [remoteStream] = event.streams;
                this.remoteStreams.set(userId, remoteStream);
                
                // Display remote video
                const remoteVideo = document.getElementById(`remoteVideo-${userId}`);
                if (remoteVideo) {
                    remoteVideo.srcObject = remoteStream;
                }
            };
            
            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendWebSocketMessage({
                        type: 'ice_candidate',
                        candidate: event.candidate,
                        to_user: userId
                    });
                }
            };
            
            // Handle connection state changes
            peerConnection.onconnectionstatechange = () => {
                console.log(`Connection state with ${userId}:`, peerConnection.connectionState);
                
                if (peerConnection.connectionState === 'failed') {
                    console.log('Connection failed, attempting to restart ICE');
                    peerConnection.restartIce();
                }
            };
            
            // Create data channel for chat
            const dataChannel = peerConnection.createDataChannel('chat', {
                ordered: true
            });
            
            dataChannel.onopen = () => {
                console.log('Data channel opened with:', userId);
                this.dataChannels.set(userId, dataChannel);
            };
            
            dataChannel.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleDataChannelMessage(message, userId);
            };
            
            // Handle incoming data channels
            peerConnection.ondatachannel = (event) => {
                const channel = event.channel;
                channel.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    this.handleDataChannelMessage(message, userId);
                };
            };
            
            this.peerConnections.set(userId, peerConnection);
            return peerConnection;
        },
        
        async createOffer(userId) {
            const peerConnection = this.peerConnections.get(userId);
            if (!peerConnection) return;
            
            try {
                const offer = await peerConnection.createOffer({
                    offerToReceiveAudio: true,
                    offerToReceiveVideo: true
                });
                
                await peerConnection.setLocalDescription(offer);
                
                this.sendWebSocketMessage({
                    type: 'webrtc_offer',
                    offer: offer,
                    to_user: userId
                });
                
                console.log('Offer sent to:', userId);
            } catch (error) {
                console.error('Error creating offer:', error);
            }
        },
        
        async handleOffer(data) {
            const { from_user, offer } = data;
            let peerConnection = this.peerConnections.get(from_user);
            
            if (!peerConnection) {
                peerConnection = await this.createPeerConnection(from_user);
            }
            
            try {
                await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
                
                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);
                
                this.sendWebSocketMessage({
                    type: 'webrtc_answer',
                    answer: answer,
                    to_user: from_user
                });
                
                console.log('Answer sent to:', from_user);
            } catch (error) {
                console.error('Error handling offer:', error);
            }
        },
        
        async handleAnswer(data) {
            const { from_user, answer } = data;
            const peerConnection = this.peerConnections.get(from_user);
            
            if (peerConnection) {
                try {
                    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
                    console.log('Answer processed from:', from_user);
                } catch (error) {
                    console.error('Error handling answer:', error);
                }
            }
        },
        
        async handleIceCandidate(data) {
            const { from_user, candidate } = data;
            const peerConnection = this.peerConnections.get(from_user);
            
            if (peerConnection) {
                try {
                    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
                    console.log('ICE candidate added from:', from_user);
                } catch (error) {
                    console.error('Error adding ICE candidate:', error);
                }
            }
        },
        
        handleChatMessage(data) {
            this.chatMessages.push({
                username: data.username,
                message: data.message,
                timestamp: data.timestamp || Date.now(),
                user_id: data.user_id
            });
            
            // Scroll to bottom of chat
            this.$nextTick(() => {
                const chatContainer = document.getElementById('chatMessages');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            });
        },
        
        handleDataChannelMessage(message, userId) {
            // Handle peer-to-peer messages if needed
            console.log('Data channel message from:', userId, message);
        },
        
        handleReadyStatus(data) {
            if (this.participants[data.user_id]) {
                this.participants[data.user_id].is_ready = data.is_ready;
            }
        },
        
        sendWebSocketMessage(message) {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify(message));
            } else {
                console.warn('WebSocket not ready, message not sent:', message);
            }
        },
        
        sendMessage() {
            if (!this.newMessage.trim()) return;
            
            const message = {
                type: 'chat_message',
                message: this.newMessage.trim(),
                timestamp: Date.now()
            };
            
            this.sendWebSocketMessage(message);
            this.newMessage = '';
        },
        
        async toggleAudio() {
            if (this.localStream) {
                const audioTrack = this.localStream.getAudioTracks()[0];
                if (audioTrack) {
                    audioTrack.enabled = !audioTrack.enabled;
                    this.audioEnabled = audioTrack.enabled;
                    
                    // Notify other participants
                    this.sendWebSocketMessage({
                        type: 'audio_toggle',
                        enabled: this.audioEnabled
                    });
                }
            }
        },
        
        async toggleVideo() {
            if (this.localStream) {
                const videoTrack = this.localStream.getVideoTracks()[0];
                if (videoTrack) {
                    videoTrack.enabled = !videoTrack.enabled;
                    this.videoEnabled = videoTrack.enabled;
                    
                    // Notify other participants
                    this.sendWebSocketMessage({
                        type: 'video_toggle',
                        enabled: this.videoEnabled
                    });
                }
            }
        },
        
        async toggleScreenShare() {
            try {
                if (!this.screenSharing) {
                    // Start screen sharing
                    const screenStream = await navigator.mediaDevices.getDisplayMedia({
                        video: true,
                        audio: true
                    });
                    
                    // Replace video track in all peer connections
                    const videoTrack = screenStream.getVideoTracks()[0];
                    
                    for (const [userId, peerConnection] of this.peerConnections) {
                        const sender = peerConnection.getSenders().find(s => 
                            s.track && s.track.kind === 'video'
                        );
                        
                        if (sender) {
                            await sender.replaceTrack(videoTrack);
                        }
                    }
                    
                    // Update local video
                    const localVideo = document.getElementById('localVideo');
                    if (localVideo) {
                        localVideo.srcObject = screenStream;
                    }
                    
                    this.screenSharing = true;
                    
                    // Handle screen share ending
                    videoTrack.onended = () => {
                        this.stopScreenShare();
                    };
                    
                } else {
                    this.stopScreenShare();
                }
            } catch (error) {
                console.error('Error toggling screen share:', error);
                this.handleError('Failed to share screen: ' + error.message);
            }
        },
        
        async stopScreenShare() {
            if (this.localStream) {
                const videoTrack = this.localStream.getVideoTracks()[0];
                
                // Replace screen share with camera in all peer connections
                for (const [userId, peerConnection] of this.peerConnections) {
                    const sender = peerConnection.getSenders().find(s => 
                        s.track && s.track.kind === 'video'
                    );
                    
                    if (sender && videoTrack) {
                        await sender.replaceTrack(videoTrack);
                    }
                }
                
                // Update local video
                const localVideo = document.getElementById('localVideo');
                if (localVideo) {
                    localVideo.srcObject = this.localStream;
                }
            }
            
            this.screenSharing = false;
        },
        
        async endSession() {
            if (!this.isMentor) return;
            
            if (confirm('Are you sure you want to end this session for all participants?')) {
                try {
                    const response = await fetch(`/sessions/${this.sessionId}/end/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': this.getCSRFToken(),
                            'Content-Type': 'application/json',
                        },
                    });
                    
                    if (response.ok) {
                        this.leaveRoom();
                    } else {
                        throw new Error('Failed to end session');
                    }
                } catch (error) {
                    console.error('Error ending session:', error);
                    this.handleError('Failed to end session: ' + error.message);
                }
            }
        },
        
        leaveRoom() {
            // Close all peer connections
            for (const [userId, peerConnection] of this.peerConnections) {
                peerConnection.close();
            }
            this.peerConnections.clear();
            
            // Close data channels
            for (const [userId, dataChannel] of this.dataChannels) {
                dataChannel.close();
            }
            this.dataChannels.clear();
            
            // Stop local stream
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => track.stop());
            }
            
            // Close WebSocket
            if (this.socket) {
                this.socket.close();
            }
            
            // Stop timers
            if (this.durationTimer) {
                clearInterval(this.durationTimer);
            }
            
            // Redirect to session detail page
            window.location.href = `/sessions/${this.sessionId}/`;
        },
        
        startSessionTimer() {
            this.sessionStartTime = Date.now();
            
            this.durationTimer = setInterval(() => {
                const elapsed = Date.now() - this.sessionStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                this.sessionDuration = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);
        },
        
        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        initializeUI() {
            // Initialize feather icons if available
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
            
            // Set up keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    switch (e.key) {
                        case 'm':
                            e.preventDefault();
                            this.toggleAudio();
                            break;
                        case 'e':
                            e.preventDefault();
                            this.toggleVideo();
                            break;
                        case 'Enter':
                            if (this.chatVisible && this.newMessage.trim()) {
                                e.preventDefault();
                                this.sendMessage();
                            }
                            break;
                    }
                }
            });
        },
        
        handleError(message) {
            console.error('WebRTC Error:', message);
            
            // Show error to user (you might want to implement a proper toast system)
            alert(message);
        },
        
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                   document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        },
        
        // Cleanup when component is destroyed
        cleanup() {
            this.leaveRoom();
        }
    };
}

// Auto-cleanup on page unload
window.addEventListener('beforeunload', () => {
    // This will be called by Alpine.js component cleanup if properly bound
    console.log('Page unloading, cleaning up WebRTC connections...');
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { webRTCRoom };
}
