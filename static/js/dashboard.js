/**
 * PeerLearn Dashboard JavaScript
 * Handles dashboard interactions, real-time updates, and UI state management
 */

// Global dashboard utilities
window.PeerLearnDashboard = {
    
    // WebSocket connection for real-time updates
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    
    // Initialize dashboard
    init() {
        this.setupGlobalEventListeners();
        this.connectDashboardWebSocket();
        this.initializeCountdowns();
        
        console.log('PeerLearn Dashboard initialized');
    },
    
    // Connect to dashboard WebSocket for real-time updates
    connectDashboardWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('Dashboard WebSocket connected');
            this.reconnectAttempts = 0;
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleDashboardUpdate(data);
        };
        
        this.socket.onclose = () => {
            console.log('Dashboard WebSocket disconnected');
            this.attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('Dashboard WebSocket error:', error);
        };
    },
    
    // Handle real-time dashboard updates
    handleDashboardUpdate(data) {
        switch (data.type) {
            case 'session_update':
                this.handleSessionUpdate(data);
                break;
            case 'booking_update':
                this.handleBookingUpdate(data);
                break;
            case 'notification':
                this.handleNotification(data);
                break;
            default:
                console.log('Unknown dashboard update:', data);
        }
    },
    
    // Handle session status updates
    handleSessionUpdate(data) {
        const sessionCards = document.querySelectorAll(`[data-session-id="${data.session_id}"]`);
        
        sessionCards.forEach(card => {
            // Update status badge
            const statusBadge = card.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.textContent = data.status.toUpperCase();
                statusBadge.className = `status-badge ${this.getStatusClass(data.status)}`;
            }
            
            // Update participant count if provided
            if (data.participants !== undefined) {
                const participantCount = card.querySelector('.participant-count');
                if (participantCount) {
                    participantCount.textContent = data.participants;
                }
            }
            
            // Update action buttons based on status
            this.updateSessionActions(card, data);
        });
        
        // Trigger refresh of dashboard data if Alpine.js components are present
        if (window.Alpine) {
            // Send custom event that Alpine components can listen to
            window.dispatchEvent(new CustomEvent('session-updated', {
                detail: data
            }));
        }
    },
    
    // Handle booking updates
    handleBookingUpdate(data) {
        // Similar to session updates but for booking-specific changes
        console.log('Booking updated:', data);
        
        // Refresh booking lists if needed
        const bookingLists = document.querySelectorAll('.booking-list');
        bookingLists.forEach(list => {
            // Trigger refresh
            if (list.alpine) {
                list.alpine.refreshBookings();
            }
        });
    },
    
    // Handle real-time notifications
    handleNotification(data) {
        this.showNotification(data.message, data.type || 'info');
    },
    
    // Update session action buttons based on status
    updateSessionActions(card, sessionData) {
        const actionsContainer = card.querySelector('.session-actions');
        if (!actionsContainer) return;
        
        // Clear existing actions
        actionsContainer.innerHTML = '';
        
        const { session_id, status, can_start } = sessionData;
        
        if (status === 'live') {
            actionsContainer.innerHTML = `
                <a href="/sessions/${session_id}/room/" 
                   class="btn btn-success">
                    <i data-feather="video" class="h-4 w-4 mr-1"></i>
                    Join Room
                </a>
            `;
        } else if (status === 'scheduled' && can_start) {
            actionsContainer.innerHTML = `
                <button onclick="PeerLearnDashboard.startSession('${session_id}')" 
                        class="btn btn-primary">
                    <i data-feather="play" class="h-4 w-4 mr-1"></i>
                    Start Session
                </button>
            `;
        }
        
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    },
    
    // Start a session (mentor action)
    async startSession(sessionId) {
        try {
            const response = await fetch(`/sessions/${sessionId}/start/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                // Navigate to room
                window.location.href = `/sessions/${sessionId}/room/`;
            } else {
                const error = await response.json();
                this.showNotification(error.error || 'Failed to start session', 'error');
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showNotification('Failed to start session', 'error');
        }
    },
    
    // Book a session (learner action)
    async bookSession(sessionId) {
        try {
            const response = await fetch(`/sessions/${sessionId}/book/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showNotification(data.message || 'Session booked successfully! Redirecting to My Sessions...', 'success');
                // Redirect to my sessions
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/sessions/my-sessions/';
                }, 1500);
            } else {
                const error = await response.text();
                this.showNotification(error || 'Failed to book session', 'error');
            }
        } catch (error) {
            console.error('Error booking session:', error);
            this.showNotification('Failed to book session', 'error');
        }
    },
    
    // Initialize countdown timers for upcoming sessions
    initializeCountdowns() {
        const countdownElements = document.querySelectorAll('[data-countdown]');
        
        countdownElements.forEach(element => {
            const targetTime = new Date(element.dataset.countdown).getTime();
            
            const updateCountdown = () => {
                const now = new Date().getTime();
                const timeLeft = targetTime - now;
                
                if (timeLeft > 0) {
                    const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                    
                    let countdownText = '';
                    if (days > 0) {
                        countdownText = `${days}d ${hours}h ${minutes}m`;
                    } else if (hours > 0) {
                        countdownText = `${hours}h ${minutes}m ${seconds}s`;
                    } else if (minutes > 0) {
                        countdownText = `${minutes}m ${seconds}s`;
                    } else {
                        countdownText = `${seconds}s`;
                    }
                    
                    element.textContent = `Starts in ${countdownText}`;
                } else {
                    element.textContent = 'Session starting now!';
                    element.classList.add('text-green-600', 'font-semibold');
                }
            };
            
            // Update immediately and then every second
            updateCountdown();
            setInterval(updateCountdown, 1000);
        });
    },
    
    // Show notification toast
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 max-w-sm bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden z-50 transform transition-all duration-300 translate-x-full`;
        
        const bgColor = {
            'success': 'bg-green-50 border-green-200',
            'error': 'bg-red-50 border-red-200',
            'warning': 'bg-yellow-50 border-yellow-200',
            'info': 'bg-blue-50 border-blue-200'
        }[type] || 'bg-blue-50 border-blue-200';
        
        const iconColor = {
            'success': 'text-green-400',
            'error': 'text-red-400',
            'warning': 'text-yellow-400',
            'info': 'text-blue-400'
        }[type] || 'text-blue-400';
        
        const iconName = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        }[type] || 'info';
        
        notification.innerHTML = `
            <div class="p-4 ${bgColor}">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i data-feather="${iconName}" class="h-5 w-5 ${iconColor}"></i>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button onclick="this.closest('.fixed').remove()" class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none">
                            <i data-feather="x" class="h-4 w-4"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.remove('translate-x-full');
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    },
    
    // Set up global event listeners
    setupGlobalEventListeners() {
        // Handle session card clicks
        document.addEventListener('click', (e) => {
            const sessionCard = e.target.closest('.session-card');
            if (sessionCard && !e.target.closest('button') && !e.target.closest('a')) {
                const sessionId = sessionCard.dataset.sessionId;
                if (sessionId) {
                    window.location.href = `/sessions/${sessionId}/`;
                }
            }
        });
        
        // Handle filter changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('.filter-select, .filter-input')) {
                this.applyFilters();
            }
        });
        
        // Handle search input with debouncing
        let searchTimeout;
        document.addEventListener('input', (e) => {
            if (e.target.matches('.search-input')) {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 300);
            }
        });
    },
    
    // Apply filters to session lists
    applyFilters() {
        const filterInputs = document.querySelectorAll('.filter-select, .filter-input, .search-input');
        const filters = {};
        
        filterInputs.forEach(input => {
            if (input.value) {
                filters[input.name || input.dataset.filter] = input.value;
            }
        });
        
        // Send filters to server or apply client-side filtering
        console.log('Applying filters:', filters);
        
        // If using Alpine.js components, trigger filter update
        if (window.Alpine) {
            window.dispatchEvent(new CustomEvent('filters-changed', {
                detail: filters
            }));
        }
    },
    
    // Attempt to reconnect WebSocket
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connectDashboardWebSocket();
            }, Math.pow(2, this.reconnectAttempts) * 1000); // Exponential backoff
        } else {
            console.error('Max reconnection attempts reached');
            this.showNotification('Connection lost. Please refresh the page.', 'error');
        }
    },
    
    // Utility function to get status CSS class
    getStatusClass(status) {
        const classes = {
            'scheduled': 'px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800',
            'live': 'px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800',
            'completed': 'px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800',
            'cancelled': 'px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800',
            'draft': 'px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800'
        };
        return classes[status] || classes['scheduled'];
    },
    
    // Utility function to format time
    formatTime(dateString) {
        return new Date(dateString).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Utility function to format date and time
    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString([], {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Get CSRF token for Django requests
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    },
    
    // Clean up WebSocket connection
    cleanup() {
        if (this.socket) {
            this.socket.close();
        }
    }
};

// Dashboard-specific Alpine.js data functions
window.dashboardData = {
    
    // Common session management functionality
    sessionManagement() {
        return {
            sessions: {
                today: [],
                upcoming: [],
                past: [],
                drafts: []
            },
            loading: false,
            error: null,
            
            async loadSessions() {
                this.loading = true;
                this.error = null;
                
                try {
                    const response = await fetch('/sessions/api/list/');
                    if (!response.ok) throw new Error('Failed to load sessions');
                    
                    const sessions = await response.json();
                    this.categorizeSessions(sessions);
                } catch (error) {
                    console.error('Error loading sessions:', error);
                    this.error = error.message;
                    PeerLearnDashboard.showNotification('Failed to load sessions', 'error');
                } finally {
                    this.loading = false;
                }
            },
            
            categorizeSessions(sessions) {
                const now = new Date();
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                const tomorrow = new Date(today);
                tomorrow.setDate(tomorrow.getDate() + 1);
                
                this.sessions.today = sessions.filter(session => {
                    const sessionDate = new Date(session.schedule);
                    return sessionDate >= today && sessionDate < tomorrow && session.status === 'scheduled';
                });
                
                this.sessions.upcoming = sessions.filter(session => {
                    const sessionDate = new Date(session.schedule);
                    return sessionDate >= tomorrow && session.status === 'scheduled';
                });
                
                this.sessions.past = sessions.filter(session => 
                    session.status === 'completed' || session.status === 'cancelled'
                );
                
                this.sessions.drafts = sessions.filter(session => 
                    session.status === 'draft'
                );
            },
            
            async refreshSessions() {
                await this.loadSessions();
            }
        };
    },
    
    // Booking management for learners
    bookingManagement() {
        return {
            bookings: {
                upcoming: [],
                past: []
            },
            loading: false,
            
            async loadBookings() {
                this.loading = true;
                
                try {
                    // This would be implemented with actual booking API
                    console.log('Loading bookings...');
                    // For now, keeping empty as the API endpoint would need to be created
                    this.bookings = { upcoming: [], past: [] };
                } catch (error) {
                    console.error('Error loading bookings:', error);
                    PeerLearnDashboard.showNotification('Failed to load bookings', 'error');
                } finally {
                    this.loading = false;
                }
            },
            
            async refreshBookings() {
                await this.loadBookings();
            }
        };
    },
    
    // Real-time statistics
    statistics() {
        return {
            stats: {
                totalSessions: 0,
                totalLearners: 0,
                upcomingSessions: 0,
                averageRating: 0.0
            },
            
            updateStats(sessions) {
                this.stats.totalSessions = sessions.length;
                this.stats.upcomingSessions = sessions.filter(s => 
                    s.status === 'scheduled' && new Date(s.schedule) > new Date()
                ).length;
                
                // Calculate other stats as needed
                // These would typically come from the backend API
            }
        };
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    PeerLearnDashboard.init();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    PeerLearnDashboard.cleanup();
});

// Handle page visibility changes to manage WebSocket connections
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, can pause some updates
        console.log('Page hidden, reducing activity');
    } else {
        // Page is visible, resume full activity
        console.log('Page visible, resuming full activity');
        if (!PeerLearnDashboard.socket || PeerLearnDashboard.socket.readyState === WebSocket.CLOSED) {
            PeerLearnDashboard.connectDashboardWebSocket();
        }
    }
});
