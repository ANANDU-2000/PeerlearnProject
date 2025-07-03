/**
 * Enhanced WebRTC Implementation for PeerLearn Platform
 * Handles camera access limitations and provides robust fallbacks
 */

class PeerLearnVideoManager {
    constructor() {
        this.localStream = null;
        this.peerConnections = new Map();
        this.socket = null;
        this.sessionId = null;
        this.userId = null;
        this.isInitialized = false;
        
        // Enhanced WebRTC configuration
        this.rtcConfig = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' }
            ],
            iceCandidatePoolSize: 10
        };
        
        // Video constraints with fallbacks
        this.videoConstraints = [
            // High quality attempt
            { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } },
            // Medium quality fallback
            { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 15 } },
            // Low quality fallback
            { width: { ideal: 320 }, height: { ideal: 240 }, frameRate: { ideal: 10 } }
        ];
    }

    /**
     * Initialize video session with enhanced error handling
     */
    async initializeSession(sessionId, userId) {
        try {
            this.sessionId = sessionId;
            this.userId = userId;
            
            console.log(`Initializing session ${sessionId} for user ${userId}`);
            
            // Step 1: Setup WebSocket connection
            await this.connectWebSocket();
            
            // Step 2: Get user media with fallbacks
            await this.setupUserMedia();
            
            // Step 3: Display local video
            this.displayLocalVideo();
            
            // Step 4: Mark as initialized
            this.isInitialized = true;
            
            console.log('Video session initialized successfully');
            return true;
            
        } catch (error) {
            console.error('Failed to initialize video session:', error);
            await this.handleInitializationError(error);
            return false;
        }
    }

    /**
     * Enhanced media access with progressive fallbacks
     */
    async setupUserMedia() {
        // Check if camera is already in use (common issue)
        if (await this.isCameraInUse()) {
            console.warn('Camera appears to be in use, trying alternatives...');
            return await this.handleCameraInUse();
        }

        // Try video constraints in order of preference
        for (let i = 0; i < this.videoConstraints.length; i++) {
            try {
                const constraints = {
                    video: this.videoConstraints[i],
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true,
                        sampleRate: 44100
                    }
                };
                
                console.log(`Attempting media access with constraints:`, constraints);
                this.localStream = await navigator.mediaDevices.getUserMedia(constraints);
                
                console.log('Successfully obtained media stream');
                return this.localStream;
                
            } catch (error) {
                console.warn(`Media attempt ${i + 1} failed:`, error.message);
                
                if (error.name === 'NotAllowedError') {
                    throw new Error('Camera/microphone permission denied. Please allow access and refresh.');
                }
                
                if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                    if (i === this.videoConstraints.length - 1) {
                        // Last attempt failed, try audio-only
                        return await this.setupAudioOnlyMode();
                    }
                }
                
                // Continue to next constraint
                continue;
            }
        }
        
        // All video attempts failed, try audio-only
        return await this.setupAudioOnlyMode();
    }

    /**
     * Check if camera is already in use (heuristic)
     */
    async isCameraInUse() {
        try {
            // Quick test to see if camera is available
            const testStream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 1, height: 1 }, 
                audio: false 
            });
            testStream.getTracks().forEach(track => track.stop());
            return false;
        } catch (error) {
            return error.name === 'NotReadableError' || error.name === 'TrackStartError';
        }
    }

    /**
     * Handle camera in use scenario
     */
    async handleCameraInUse() {
        console.log('Camera in use, providing alternatives...');
        
        // Show user notification
        this.showNotification(
            'Camera In Use', 
            'Your camera is being used by another tab/application. Using audio-only mode.',
            'warning'
        );
        
        // Try audio-only mode
        return await this.setupAudioOnlyMode();
    }

    /**
     * Setup audio-only mode as fallback
     */
    async setupAudioOnlyMode() {
        try {
            console.log('Setting up audio-only mode');
            
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: false,
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Create dummy video track for consistent handling
            this.createDummyVideoTrack();
            
            this.showNotification(
                'Audio-Only Mode', 
                'Connected with audio only. Video unavailable.',
                'info'
            );
            
            return this.localStream;
            
        } catch (error) {
            console.error('Audio-only setup failed:', error);
            return await this.setupDemoMode();
        }
    }

    /**
     * Create dummy video track for audio-only mode
     */
    createDummyVideoTrack() {
        // Create canvas for dummy video
        const canvas = document.createElement('canvas');
        canvas.width = 320;
        canvas.height = 240;
        const ctx = canvas.getContext('2d');
        
        // Draw placeholder
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ffffff';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Audio Only', canvas.width / 2, canvas.height / 2);
        
        // Create video track from canvas
        const dummyStream = canvas.captureStream(1);
        const videoTrack = dummyStream.getVideoTracks()[0];
        
        if (this.localStream) {
            this.localStream.addTrack(videoTrack);
        }
    }

    /**
     * Demo mode for testing without media access
     */
    async setupDemoMode() {
        console.log('Setting up demo mode');
        
        // Create canvas for demo video
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext('2d');
        
        // Animate demo content
        let frame = 0;
        const animate = () => {
            ctx.fillStyle = `hsl(${frame % 360}, 50%, 20%)`;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';
            ctx.font = '24px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Demo Mode', canvas.width / 2, canvas.height / 2 - 20);
            ctx.fillText(`Frame: ${frame}`, canvas.width / 2, canvas.height / 2 + 20);
            frame++;
            
            if (this.localStream) {
                requestAnimationFrame(animate);
            }
        };
        
        this.localStream = canvas.captureStream(15);
        
        // Start animation
        animate();
        
        this.showNotification(
            'Demo Mode', 
            'Running in demo mode for testing. No camera/microphone access.',
            'info'
        );
        
        return this.localStream;
    }

    /**
     * Display local video with error handling
     */
    displayLocalVideo() {
        const localVideo = document.getElementById('localVideo');
        if (localVideo && this.localStream) {
            localVideo.srcObject = this.localStream;
            localVideo.muted = true; // Prevent echo
            
            localVideo.onloadedmetadata = () => {
                localVideo.play().catch(error => {
                    console.warn('Local video autoplay failed:', error);
                });
            };
            
            // Update UI based on stream type
            this.updateVideoUI(localVideo);
        }
    }

    /**
     * Update UI based on video stream characteristics
     */
    updateVideoUI(videoElement) {
        const videoTrack = this.localStream.getVideoTracks()[0];
        const audioTrack = this.localStream.getAudioTracks()[0];
        
        // Update status indicators
        const videoStatus = document.getElementById('videoStatus');
        const audioStatus = document.getElementById('audioStatus');
        
        if (videoStatus) {
            videoStatus.textContent = videoTrack ? 'Video: On' : 'Video: Off';
            videoStatus.className = videoTrack ? 'status-on' : 'status-off';
        }
        
        if (audioStatus) {
            audioStatus.textContent = audioTrack ? 'Audio: On' : 'Audio: Off';
            audioStatus.className = audioTrack ? 'status-on' : 'status-off';
        }
        
        // Add video quality indicator
        if (videoTrack) {
            const settings = videoTrack.getSettings();
            const qualityIndicator = document.getElementById('qualityIndicator');
            if (qualityIndicator) {
                qualityIndicator.textContent = `${settings.width}x${settings.height}@${settings.frameRate}fps`;
            }
        }
    }

    /**
     * Enhanced WebSocket connection with reconnection
     */
    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/session/${this.sessionId}/`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.sendMessage({
                    type: 'user_joined',
                    userId: this.userId,
                    sessionId: this.sessionId
                });
                resolve();
            };
            
            this.socket.onmessage = (event) => {
                this.handleWebSocketMessage(JSON.parse(event.data));
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket disconnected');
                setTimeout(() => this.reconnectWebSocket(), 3000);
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
            
            // Timeout after 10 seconds
            setTimeout(() => {
                if (this.socket.readyState !== WebSocket.OPEN) {
                    reject(new Error('WebSocket connection timeout'));
                }
            }, 10000);
        });
    }

    /**
     * WebSocket reconnection logic
     */
    reconnectWebSocket() {
        if (this.isInitialized) {
            console.log('Attempting to reconnect WebSocket...');
            this.connectWebSocket().catch(error => {
                console.error('Reconnection failed:', error);
            });
        }
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        console.log('WebSocket message received:', data);
        
        switch (data.type) {
            case 'user_joined':
                this.handleUserJoined(data);
                break;
            case 'webrtc_offer':
                this.handleWebRTCOffer(data);
                break;
            case 'webrtc_answer':
                this.handleWebRTCAnswer(data);
                break;
            case 'ice_candidate':
                this.handleIceCandidate(data);
                break;
            case 'user_left':
                this.handleUserLeft(data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    /**
     * Handle new user joining
     */
    async handleUserJoined(data) {
        if (data.userId !== this.userId && !this.peerConnections.has(data.userId)) {
            console.log('New user joined:', data.userId);
            await this.createPeerConnection(data.userId, true);
        }
    }

    /**
     * Create peer connection with enhanced error handling
     */
    async createPeerConnection(userId, isInitiator = false) {
        try {
            console.log(`Creating peer connection with user ${userId}, initiator: ${isInitiator}`);
            
            const peerConnection = new RTCPeerConnection(this.rtcConfig);
            
            // Add local stream tracks
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => {
                    peerConnection.addTrack(track, this.localStream);
                });
            }
            
            // Handle remote stream
            peerConnection.ontrack = (event) => {
                console.log('Remote track received from user:', userId);
                this.handleRemoteStream(userId, event.streams[0]);
            };
            
            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendMessage({
                        type: 'ice_candidate',
                        candidate: event.candidate,
                        toUserId: userId,
                        fromUserId: this.userId
                    });
                }
            };
            
            // Handle connection state changes
            peerConnection.onconnectionstatechange = () => {
                console.log(`Connection state with ${userId}:`, peerConnection.connectionState);
                this.updateConnectionStatus(userId, peerConnection.connectionState);
            };
            
            this.peerConnections.set(userId, peerConnection);
            
            // If initiator, create offer
            if (isInitiator) {
                await this.createOffer(userId);
            }
            
        } catch (error) {
            console.error('Failed to create peer connection:', error);
        }
    }

    /**
     * Create WebRTC offer
     */
    async createOffer(userId) {
        try {
            const peerConnection = this.peerConnections.get(userId);
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            
            this.sendMessage({
                type: 'webrtc_offer',
                offer: offer,
                toUserId: userId,
                fromUserId: this.userId
            });
            
        } catch (error) {
            console.error('Failed to create offer:', error);
        }
    }

    /**
     * Handle WebRTC offer
     */
    async handleWebRTCOffer(data) {
        try {
            const peerConnection = this.peerConnections.get(data.fromUserId) || 
                                 await this.createPeerConnection(data.fromUserId, false);
            
            await peerConnection.setRemoteDescription(data.offer);
            const answer = await peerConnection.createAnswer();
            await peerConnection.setLocalDescription(answer);
            
            this.sendMessage({
                type: 'webrtc_answer',
                answer: answer,
                toUserId: data.fromUserId,
                fromUserId: this.userId
            });
            
        } catch (error) {
            console.error('Failed to handle WebRTC offer:', error);
        }
    }

    /**
     * Handle WebRTC answer
     */
    async handleWebRTCAnswer(data) {
        try {
            const peerConnection = this.peerConnections.get(data.fromUserId);
            if (peerConnection) {
                await peerConnection.setRemoteDescription(data.answer);
            }
        } catch (error) {
            console.error('Failed to handle WebRTC answer:', error);
        }
    }

    /**
     * Handle ICE candidate
     */
    async handleIceCandidate(data) {
        try {
            const peerConnection = this.peerConnections.get(data.fromUserId);
            if (peerConnection) {
                await peerConnection.addIceCandidate(data.candidate);
            }
        } catch (error) {
            console.error('Failed to handle ICE candidate:', error);
        }
    }

    /**
     * Handle remote stream
     */
    handleRemoteStream(userId, stream) {
        console.log('Displaying remote stream for user:', userId);
        
        // Create or update remote video element
        let remoteVideo = document.getElementById(`remoteVideo_${userId}`);
        if (!remoteVideo) {
            remoteVideo = this.createRemoteVideoElement(userId);
        }
        
        remoteVideo.srcObject = stream;
        remoteVideo.onloadedmetadata = () => {
            remoteVideo.play().catch(error => {
                console.warn('Remote video autoplay failed:', error);
            });
        };
        
        // Update UI to show connection established
        this.updateConnectionStatus(userId, 'connected');
    }

    /**
     * Create remote video element
     */
    createRemoteVideoElement(userId) {
        const remoteVideosContainer = document.getElementById('remoteVideos');
        if (!remoteVideosContainer) {
            console.error('Remote videos container not found');
            return null;
        }
        
        const videoContainer = document.createElement('div');
        videoContainer.className = 'remote-video-container';
        videoContainer.id = `container_${userId}`;
        
        const video = document.createElement('video');
        video.id = `remoteVideo_${userId}`;
        video.className = 'remote-video';
        video.autoplay = true;
        video.playsInline = true;
        
        const userLabel = document.createElement('div');
        userLabel.className = 'user-label';
        userLabel.textContent = `User ${userId}`;
        
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'connection-status';
        statusIndicator.id = `status_${userId}`;
        statusIndicator.textContent = 'Connecting...';
        
        videoContainer.appendChild(video);
        videoContainer.appendChild(userLabel);
        videoContainer.appendChild(statusIndicator);
        remoteVideosContainer.appendChild(videoContainer);
        
        return video;
    }

    /**
     * Update connection status display
     */
    updateConnectionStatus(userId, status) {
        const statusElement = document.getElementById(`status_${userId}`);
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `connection-status status-${status.toLowerCase()}`;
        }
    }

    /**
     * Send message via WebSocket
     */
    sendMessage(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not ready, message not sent:', data);
        }
    }

    /**
     * Show notification to user
     */
    showNotification(title, message, type = 'info') {
        // Create notification element if it doesn't exist
        let notificationContainer = document.getElementById('notifications');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notifications';
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <strong>${title}</strong><br>
            ${message}
        `;
        
        notificationContainer.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    /**
     * Toggle local video
     */
    toggleVideo() {
        const videoTrack = this.localStream?.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            this.updateVideoUI();
        }
    }

    /**
     * Toggle local audio
     */
    toggleAudio() {
        const audioTrack = this.localStream?.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            this.updateVideoUI();
        }
    }

    /**
     * Handle initialization errors
     */
    async handleInitializationError(error) {
        console.error('Initialization error:', error);
        
        let message = 'Failed to initialize video session.';
        let solution = 'Please refresh the page and try again.';
        
        if (error.message.includes('permission')) {
            message = 'Camera/microphone access denied.';
            solution = 'Please allow camera access and refresh the page.';
        } else if (error.message.includes('NotReadableError')) {
            message = 'Camera is being used by another application.';
            solution = 'Close other applications using the camera or use audio-only mode.';
        }
        
        this.showNotification('Connection Error', `${message} ${solution}`, 'error');
        
        // Try to continue with limited functionality
        await this.setupDemoMode();
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        console.log('Cleaning up video session...');
        
        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        // Close peer connections
        this.peerConnections.forEach((pc, userId) => {
            pc.close();
        });
        this.peerConnections.clear();
        
        // Close WebSocket
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        
        this.isInitialized = false;
    }
}

// Global instance
let videoManager = null;

/**
 * Initialize video session (called from templates)
 */
async function initializeVideoSession(sessionId, userId) {
    console.log('Initializing PeerLearn video session...');
    
    if (videoManager) {
        videoManager.cleanup();
    }
    
    videoManager = new PeerLearnVideoManager();
    const success = await videoManager.initializeSession(sessionId, userId);
    
    if (success) {
        console.log('Video session ready!');
        // Setup UI controls
        setupVideoControls();
    } else {
        console.error('Failed to initialize video session');
    }
    
    return success;
}

/**
 * Setup video control buttons
 */
function setupVideoControls() {
    const toggleVideoBtn = document.getElementById('toggleVideoBtn');
    const toggleAudioBtn = document.getElementById('toggleAudioBtn');
    
    if (toggleVideoBtn) {
        toggleVideoBtn.onclick = () => {
            videoManager.toggleVideo();
            toggleVideoBtn.textContent = toggleVideoBtn.textContent.includes('Off') ? 
                'Turn Video Off' : 'Turn Video On';
        };
    }
    
    if (toggleAudioBtn) {
        toggleAudioBtn.onclick = () => {
            videoManager.toggleAudio();
            toggleAudioBtn.textContent = toggleAudioBtn.textContent.includes('Off') ? 
                'Mute Audio' : 'Unmute Audio';
        };
    }
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (videoManager) {
        videoManager.cleanup();
    }
});

// Export for global access
window.PeerLearnVideo = {
    initialize: initializeVideoSession,
    manager: () => videoManager
};
