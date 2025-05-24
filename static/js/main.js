/**
 * PeerLearn Main JavaScript
 * Global utilities, components, and application initialization
 */

// Global PeerLearn namespace
window.PeerLearn = {
    
    // Application configuration
    config: {
        debug: window.location.hostname === 'localhost',
        wsProtocol: window.location.protocol === 'https:' ? 'wss:' : 'ws:',
        apiVersion: 'v1'
    },
    
    // Initialize the application
    init() {
        this.setupGlobalErrorHandling();
        this.initializeFeatherIcons();
        this.setupFormValidation();
        this.setupModalHandlers();
        this.setupTooltips();
        this.setupAccessibility();
        
        if (this.config.debug) {
            console.log('PeerLearn application initialized');
        }
    },
    
    // Set up global error handling
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            
            if (this.config.debug) {
                this.showNotification('An error occurred. Check console for details.', 'error');
            }
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            
            if (this.config.debug) {
                this.showNotification('Promise rejection. Check console for details.', 'error');
            }
        });
    },
    
    // Initialize Feather icons
    initializeFeatherIcons() {
        if (typeof feather !== 'undefined') {
            feather.replace();
            
            // Re-initialize icons when content changes
            const observer = new MutationObserver(() => {
                feather.replace();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    },
    
    // Set up form validation
    setupFormValidation() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM' && !form.noValidate) {
                const isValid = this.validateForm(form);
                if (!isValid) {
                    e.preventDefault();
                }
            }
        });
        
        // Real-time validation
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input, textarea, select')) {
                this.validateField(e.target);
            }
        }, true);
    },
    
    // Validate a form
    validateForm(form) {
        let isValid = true;
        const fields = form.querySelectorAll('input, textarea, select');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    },
    
    // Validate a single field
    validateField(field) {
        const value = field.value.trim();
        const rules = this.getValidationRules(field);
        let isValid = true;
        let errorMessage = '';
        
        // Required validation
        if (rules.required && !value) {
            isValid = false;
            errorMessage = `${this.getFieldLabel(field)} is required`;
        }
        
        // Email validation
        if (isValid && rules.email && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
        }
        
        // Min length validation
        if (isValid && rules.minLength && value.length < rules.minLength) {
            isValid = false;
            errorMessage = `${this.getFieldLabel(field)} must be at least ${rules.minLength} characters`;
        }
        
        // Password confirmation validation
        if (isValid && rules.confirmPassword) {
            const passwordField = document.querySelector(rules.confirmPassword);
            if (passwordField && value !== passwordField.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
        }
        
        this.showFieldValidation(field, isValid, errorMessage);
        return isValid;
    },
    
    // Get validation rules for a field
    getValidationRules(field) {
        const rules = {};
        
        if (field.required) rules.required = true;
        if (field.type === 'email') rules.email = true;
        if (field.minLength) rules.minLength = field.minLength;
        if (field.dataset.confirmPassword) rules.confirmPassword = field.dataset.confirmPassword;
        
        return rules;
    },
    
    // Get field label for error messages
    getFieldLabel(field) {
        const label = document.querySelector(`label[for="${field.id}"]`);
        return label ? label.textContent.replace('*', '').trim() : field.name || 'Field';
    },
    
    // Show field validation state
    showFieldValidation(field, isValid, errorMessage) {
        // Remove existing error
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Update field styling
        field.classList.remove('border-red-500', 'border-green-500');
        
        if (!isValid && errorMessage) {
            // Add error styling
            field.classList.add('border-red-500');
            
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error text-red-600 text-sm mt-1';
            errorDiv.textContent = errorMessage;
            field.parentNode.appendChild(errorDiv);
        } else if (field.value.trim()) {
            // Add success styling
            field.classList.add('border-green-500');
        }
    },
    
    // Set up modal handlers
    setupModalHandlers() {
        document.addEventListener('click', (e) => {
            // Close modal when clicking backdrop
            if (e.target.matches('.modal-backdrop')) {
                this.closeModal(e.target.closest('.modal'));
            }
            
            // Handle modal triggers
            if (e.target.matches('[data-modal-trigger]')) {
                e.preventDefault();
                const modalId = e.target.dataset.modalTrigger;
                const modal = document.getElementById(modalId);
                if (modal) {
                    this.openModal(modal);
                }
            }
            
            // Handle modal close buttons
            if (e.target.matches('[data-modal-close]')) {
                e.preventDefault();
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });
    },
    
    // Open a modal
    openModal(modal) {
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Focus first focusable element
        const focusable = modal.querySelector('input, button, [tabindex]:not([tabindex="-1"])');
        if (focusable) {
            focusable.focus();
        }
    },
    
    // Close a modal
    closeModal(modal) {
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    },
    
    // Set up tooltips
    setupTooltips() {
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('[data-tooltip]')) {
                this.showTooltip(e.target);
            }
        });
        
        document.addEventListener('mouseleave', (e) => {
            if (e.target.matches('[data-tooltip]')) {
                this.hideTooltip();
            }
        });
    },
    
    // Show tooltip
    showTooltip(element) {
        const text = element.dataset.tooltip;
        const position = element.dataset.tooltipPosition || 'top';
        
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.textContent = text;
        tooltip.id = 'active-tooltip';
        
        document.body.appendChild(tooltip);
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + 8;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - 8;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + 8;
                break;
        }
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    },
    
    // Hide tooltip
    hideTooltip() {
        const tooltip = document.getElementById('active-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    },
    
    // Set up accessibility features
    setupAccessibility() {
        // Keyboard navigation for custom components
        document.addEventListener('keydown', (e) => {
            // Tab navigation for custom tab components
            if (e.target.matches('[role="tab"]')) {
                this.handleTabKeyboard(e);
            }
            
            // Arrow navigation for dropdown menus
            if (e.target.matches('[role="menuitem"]')) {
                this.handleMenuKeyboard(e);
            }
        });
        
        // Focus management
        this.setupFocusManagement();
    },
    
    // Handle keyboard navigation for tabs
    handleTabKeyboard(e) {
        const tabList = e.target.closest('[role="tablist"]');
        if (!tabList) return;
        
        const tabs = Array.from(tabList.querySelectorAll('[role="tab"]'));
        const currentIndex = tabs.indexOf(e.target);
        
        let nextIndex;
        
        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
                break;
            case 'ArrowRight':
                e.preventDefault();
                nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'Home':
                e.preventDefault();
                nextIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                nextIndex = tabs.length - 1;
                break;
            default:
                return;
        }
        
        tabs[nextIndex].focus();
        tabs[nextIndex].click();
    },
    
    // Handle keyboard navigation for menus
    handleMenuKeyboard(e) {
        const menu = e.target.closest('[role="menu"]');
        if (!menu) return;
        
        const items = Array.from(menu.querySelectorAll('[role="menuitem"]'));
        const currentIndex = items.indexOf(e.target);
        
        let nextIndex;
        
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                break;
            case 'ArrowDown':
                e.preventDefault();
                nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'Home':
                e.preventDefault();
                nextIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                nextIndex = items.length - 1;
                break;
            default:
                return;
        }
        
        items[nextIndex].focus();
    },
    
    // Set up focus management
    setupFocusManagement() {
        // Skip links for accessibility
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 bg-blue-600 text-white p-2 z-50';
        document.body.insertBefore(skipLink, document.body.firstChild);
        
        // Focus indicators
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    },
    
    // Utility function to show notifications
    showNotification(message, type = 'info', duration = 5000) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification notification-' + type;
        
        const bgColors = {
            'success': 'bg-green-50 border-green-200',
            'error': 'bg-red-50 border-red-200',
            'warning': 'bg-yellow-50 border-yellow-200',
            'info': 'bg-blue-50 border-blue-200'
        };
        
        const iconColors = {
            'success': 'text-green-400',
            'error': 'text-red-400',
            'warning': 'text-yellow-400',
            'info': 'text-blue-400'
        };
        
        const icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'alert-triangle',
            'info': 'info'
        };
        
        notification.innerHTML = `
            <div class="fixed top-4 right-4 max-w-sm bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden z-50 transform transition-all duration-300 translate-x-full">
                <div class="p-4 ${bgColors[type] || bgColors.info}">
                    <div class="flex items-start">
                        <div class="flex-shrink-0">
                            <i data-feather="${icons[type] || icons.info}" class="h-5 w-5 ${iconColors[type] || iconColors.info}"></i>
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
            </div>
        `;
        
        document.body.appendChild(notification.firstElementChild);
        
        // Initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        const notificationElement = document.body.lastElementChild;
        
        // Animate in
        requestAnimationFrame(() => {
            notificationElement.classList.remove('translate-x-full');
        });
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notificationElement.parentNode) {
                    notificationElement.classList.add('translate-x-full');
                    setTimeout(() => {
                        if (notificationElement.parentNode) {
                            notificationElement.remove();
                        }
                    }, 300);
                }
            }, duration);
        }
    },
    
    // Utility function to format currency
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    // Utility function to format relative time
    formatRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    },
    
    // Utility function to debounce function calls
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Utility function to throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Get CSRF token for Django requests
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    },
    
    // API helper function
    async apiRequest(url, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        const config = {
            ...defaults,
            ...options,
            headers: {
                ...defaults.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        PeerLearn.init();
    });
} else {
    PeerLearn.init();
}

// Make PeerLearn globally available
window.PeerLearn = PeerLearn;
