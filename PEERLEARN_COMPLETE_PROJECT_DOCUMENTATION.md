# PEERLEARN PLATFORM
## Complete Project Documentation & Technical Report

---

**Submitted by:** Development Team  
**Project Title:** PeerLearn - Advanced Peer-to-Peer Learning Platform  
**Version:** 3.0 - Production Ready  
**Date:** May 27, 2025  
**Technology Stack:** Django 5.2.1, WebRTC, Alpine.js, Tailwind CSS  

---

# TABLE OF CONTENTS

1. [INTRODUCTION](#1-introduction)
2. [SYSTEM OVERVIEW](#2-system-overview)
3. [SYSTEM ANALYSIS](#3-system-analysis)
4. [EXISTING SYSTEM](#4-existing-system)
5. [REQUIREMENT ANALYSIS](#5-requirement-analysis)
6. [PROPOSED SYSTEM](#6-proposed-system)
7. [FEASIBILITY STUDY](#7-feasibility-study)
8. [SYSTEM SPECIFICATION](#8-system-specification)
9. [HARDWARE SPECIFICATION](#9-hardware-specification)
10. [SOFTWARE SPECIFICATION](#10-software-specification)
11. [SYSTEM DESIGN](#11-system-design)
12. [INPUT DESIGN](#12-input-design)
13. [OUTPUT DESIGN](#13-output-design)
14. [DATABASE DESIGN](#14-database-design)
15. [NORMALIZATION](#15-normalization)
16. [DATA FLOW DIAGRAM](#16-data-flow-diagram)
17. [UNIFIED MODELLING LANGUAGE DESIGN](#17-unified-modelling-language-design)
18. [CODE DESIGN](#18-code-design)
19. [SYSTEM TESTING](#19-system-testing)
20. [SYSTEM IMPLEMENTATION AND MAINTENANCE](#20-system-implementation-and-maintenance)
21. [CONCLUSION](#21-conclusion)
22. [FUTURE ENHANCEMENT](#22-future-enhancement)
23. [APPENDIX](#23-appendix)
24. [BIBLIOGRAPHY](#24-bibliography)

---

# 1. INTRODUCTION

## 1.1 Project Background

PeerLearn represents a revolutionary approach to digital education through peer-to-peer mentorship. In today's rapidly evolving technological landscape, traditional educational models often fall short of providing personalized, real-time learning experiences. PeerLearn bridges this gap by creating a sophisticated platform where knowledge seekers can connect with experienced mentors through advanced video communication technology.

The platform leverages cutting-edge technologies including WebRTC for real-time video communication, machine learning algorithms for intelligent matching, and secure payment processing to create a seamless educational ecosystem. Built on Django 5.2.1 with modern frontend technologies, PeerLearn delivers enterprise-grade performance with user-friendly interfaces.

## 1.2 Project Objectives

### Primary Objectives:
- **Real-time Video Learning:** Implement WebRTC technology for high-quality, peer-to-peer video sessions
- **Intelligent Matching:** Deploy ML algorithms to match learners with optimal mentors based on skills and preferences
- **Secure Transactions:** Integrate Razorpay payment gateway for secure financial transactions in INR
- **Scalable Architecture:** Build a robust, scalable system capable of handling thousands of concurrent users
- **Enhanced User Experience:** Create intuitive, responsive interfaces using Alpine.js and Tailwind CSS

### Secondary Objectives:
- **Real-time Notifications:** Implement WebSocket connections for instant communication
- **Advanced Analytics:** Provide comprehensive dashboards for mentors and learners
- **Gift System:** Enable appreciation through secure in-session donations
- **Mobile Responsiveness:** Ensure seamless experience across all devices
- **Security Compliance:** Implement enterprise-grade security measures

## 1.3 Project Scope

PeerLearn encompasses a complete educational ecosystem with the following components:

### Core Features:
1. **User Management System**
   - Enhanced registration with ML-powered skill suggestions
   - Role-based authentication (Mentor/Learner/Admin)
   - Profile management with image uploads
   - Real-time email validation

2. **Session Management**
   - Advanced session creation with pricing in INR
   - WebRTC-based video rooms
   - Real-time chat during sessions
   - Session recording capabilities

3. **Payment Processing**
   - Razorpay integration for secure transactions
   - Gift/donation system during live sessions
   - Automated earnings calculation for mentors
   - Comprehensive payment history

4. **Recommendation Engine**
   - ML-based mentor-learner matching
   - Content-based filtering algorithms
   - Collaborative filtering for similar users
   - Trending session recommendations

## 1.4 Technology Innovation

PeerLearn incorporates several cutting-edge technologies:

### WebRTC Implementation:
- **Peer-to-Peer Communication:** Direct browser-to-browser video/audio streaming
- **Low Latency:** Real-time communication with minimal delay
- **Adaptive Quality:** Automatic quality adjustment based on network conditions
- **Screen Sharing:** Advanced screen sharing capabilities for technical sessions

### Machine Learning Integration:
- **Skill Matching:** Intelligent algorithms to match complementary skills
- **Recommendation System:** Personalized session recommendations
- **Popularity Metrics:** Dynamic trending calculations
- **User Behavior Analysis:** Learning pattern recognition

### Real-time Features:
- **WebSocket Connections:** Instant messaging and notifications
- **Live Updates:** Real-time dashboard updates
- **Session Status:** Live session state management
- **Notification System:** Instant alerts and reminders

---

# 2. SYSTEM OVERVIEW

## 2.1 System Architecture

PeerLearn follows a modern, microservices-inspired architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Web Interface (Alpine.js + Tailwind CSS)                  │
│  ├── Landing Page                                          │
│  ├── Registration System                                   │
│  ├── Dashboard Interfaces                                  │
│  ├── WebRTC Video Rooms                                   │
│  └── Payment Interfaces                                    │
├─────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Django Web Framework (5.2.1)                             │
│  ├── Authentication & Authorization                        │
│  ├── Session Management                                    │
│  ├── Payment Processing                                    │
│  ├── Recommendation Engine                                 │
│  └── API Endpoints                                         │
├─────────────────────────────────────────────────────────────┤
│                    COMMUNICATION LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  Real-time Communication                                   │
│  ├── WebRTC (Peer-to-Peer Video)                          │
│  ├── WebSocket (Django Channels)                          │
│  ├── REST APIs                                             │
│  └── Razorpay Integration                                  │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Database Management                                        │
│  ├── SQLite3 (Development)                                │
│  ├── PostgreSQL (Production)                              │
│  ├── Redis (Caching & Sessions)                           │
│  └── File Storage (Media)                                  │
└─────────────────────────────────────────────────────────────┘
```

## 2.2 System Components

### 2.2.1 Frontend Components

**Alpine.js Framework:**
- Reactive data binding for dynamic interfaces
- Component-based architecture
- Real-time form validation
- Interactive dashboard elements

**Tailwind CSS Styling:**
- Mobile-first responsive design
- Custom color scheme (Blue #0056d3 & White)
- Glass morphism effects
- Smooth animations and transitions

**WebRTC Implementation:**
- Direct peer-to-peer video streaming
- Audio/video controls
- Screen sharing capabilities
- Connection quality monitoring

### 2.2.2 Backend Components

**Django Framework:**
- Model-View-Template (MVT) architecture
- ORM for database operations
- Built-in security features
- Scalable application structure

**Django Channels:**
- WebSocket support for real-time features
- Asynchronous task handling
- Channel layers for message routing
- Consumer classes for WebSocket connections

**Authentication System:**
- JWT-based token authentication
- Role-based access control
- Password security validation
- Session management

### 2.2.3 Database Components

**Core Models:**
- User management with extended profiles
- Session management with UUID primary keys
- Booking system with payment integration
- Recommendation metrics and analytics

**Relationship Management:**
- Foreign key relationships
- Many-to-many associations
- Optimized query performance
- Data integrity constraints

## 2.3 Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───▶│   Django    │───▶│  Database   │
│ Interface   │    │ Application │    │   Layer     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   WebRTC    │    │  WebSocket  │    │    Redis    │
│ Video/Audio │    │   Channels  │    │   Caching   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Payment   │    │Notification │    │    ML       │
│  Processing │    │   System    │    │ Algorithms  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 2.4 Technology Stack Integration

### Frontend Technologies:
- **Alpine.js 3.13.3:** Reactive JavaScript framework
- **Tailwind CSS 3.3.6:** Utility-first CSS framework
- **WebRTC APIs:** Real-time communication
- **Fetch API:** Asynchronous HTTP requests

### Backend Technologies:
- **Django 5.2.1:** Python web framework
- **Django REST Framework:** API development
- **Django Channels 4.0.0:** WebSocket support
- **Daphne 4.2.0:** ASGI server

### Database Technologies:
- **SQLite3:** Development database
- **PostgreSQL:** Production database
- **Redis 5.0.1:** Caching and sessions
- **File System:** Media storage

### External Integrations:
- **Razorpay:** Payment processing (INR)
- **WebRTC:** Peer-to-peer communication
- **Machine Learning:** scikit-learn algorithms

---

# 3. SYSTEM ANALYSIS

## 3.1 Current Educational Landscape

### 3.1.1 Traditional Learning Limitations

The traditional educational model faces several critical challenges in the digital age:

**Scalability Issues:**
- Limited mentor-to-learner ratios
- Geographic constraints
- Time zone limitations
- Resource allocation inefficiencies

**Quality Concerns:**
- Inconsistent teaching standards
- Lack of personalization
- Limited real-time feedback
- Outdated curriculum delivery

**Accessibility Problems:**
- High costs of quality education
- Limited availability of expert mentors
- Technology barriers for remote learning
- Language and cultural barriers

### 3.1.2 Digital Learning Evolution

The shift toward digital education has revealed both opportunities and gaps:

**Opportunities:**
- Global reach and accessibility
- Cost-effective delivery models
- Personalized learning paths
- Real-time performance tracking

**Existing Gaps:**
- Lack of human connection
- Limited interactive features
- Poor mentor-learner matching
- Inadequate payment systems for peer learning

## 3.2 Market Analysis

### 3.2.1 Competitive Landscape

**Major Competitors:**
1. **Coursera:** Large-scale course delivery
2. **Udemy:** Marketplace model
3. **MasterClass:** Celebrity instructor model
4. **Zoom:** Video communication platform

**Market Gaps Identified:**
- Peer-to-peer learning focus
- Real-time video mentorship
- Intelligent matching algorithms
- Micro-payment systems for short sessions

### 3.2.2 Target Audience Analysis

**Primary Users:**
- **Learners:** Age 18-45, seeking skill development
- **Mentors:** Experienced professionals willing to teach
- **Organizations:** Companies seeking training solutions

**User Behavior Patterns:**
- Preference for flexible scheduling
- Demand for personalized learning
- Expectation of high-quality video communication
- Need for transparent pricing and payments

## 3.3 Technical Analysis

### 3.3.1 Technology Requirements

**Real-time Communication:**
- Low-latency video streaming
- High-quality audio transmission
- Screen sharing capabilities
- Mobile device compatibility

**Scalability Requirements:**
- Support for 10,000+ concurrent users
- Global content delivery
- Database optimization
- Load balancing capabilities

**Security Requirements:**
- End-to-end encryption for video calls
- Secure payment processing
- User data protection
- GDPR compliance

### 3.3.2 Performance Metrics

**Key Performance Indicators:**
- Video call quality (>95% success rate)
- Payment processing speed (<3 seconds)
- User registration conversion (>80%)
- Session booking completion (>90%)

**Technical Metrics:**
- Server response time (<200ms)
- Database query optimization (<50ms)
- WebSocket connection stability (>99%)
- File upload performance (<10 seconds)

---

# 4. EXISTING SYSTEM

## 4.1 Current Market Solutions

### 4.1.1 Traditional Online Learning Platforms

**Coursera:**
- **Strengths:** Large course catalog, university partnerships
- **Weaknesses:** No real-time mentorship, limited interaction
- **Technology:** Video streaming, basic forums
- **Pricing:** Subscription-based model

**Udemy:**
- **Strengths:** Marketplace approach, diverse content
- **Weaknesses:** No live interaction, quality inconsistency
- **Technology:** Video hosting, basic messaging
- **Pricing:** One-time course purchases

**MasterClass:**
- **Strengths:** High-quality content, celebrity instructors
- **Weaknesses:** No personalization, limited topics
- **Technology:** Professional video production
- **Pricing:** Subscription model

### 4.1.2 Video Communication Platforms

**Zoom:**
- **Strengths:** Reliable video quality, feature-rich
- **Weaknesses:** Not education-focused, no payment integration
- **Technology:** Proprietary video protocols
- **Pricing:** Tiered subscription model

**Google Meet:**
- **Strengths:** Integration with Google services
- **Weaknesses:** Limited educational features
- **Technology:** WebRTC-based
- **Pricing:** Freemium model

### 4.1.3 Peer-to-Peer Learning Attempts

**Existing Attempts:**
- Basic tutoring platforms
- Simple video calling websites
- Marketplace-style learning platforms

**Common Limitations:**
- Poor video quality
- Lack of intelligent matching
- Limited payment options
- No real-time features
- Poor mobile experience

## 4.2 Technology Gap Analysis

### 4.2.1 Video Communication Gaps

**Current Limitations:**
- Dependence on third-party video services
- No integrated payment during calls
- Limited screen sharing capabilities
- Poor mobile optimization

**Missing Features:**
- Peer-to-peer direct connections
- In-session gift/payment systems
- Advanced video controls
- Quality adaptation algorithms

### 4.2.2 Matching System Gaps

**Current Approach:**
- Manual mentor selection
- Basic filter systems
- Limited recommendation engines
- No machine learning integration

**Identified Needs:**
- Intelligent skill matching
- Behavioral pattern analysis
- Real-time availability matching
- Personalized recommendations

### 4.2.3 Payment System Gaps

**Current Solutions:**
- Monthly subscriptions
- Course-based payments
- No micro-payment support
- Limited regional payment methods

**Required Improvements:**
- Session-based payments
- Regional currency support (INR)
- Instant payment processing
- In-session tipping/gifts

---

# 5. REQUIREMENT ANALYSIS

## 5.1 Functional Requirements

### 5.1.1 User Management Requirements

**Registration System:**
- Multi-step registration wizard
- Email validation with real-time verification
- Password strength indicators
- Profile image upload capabilities
- Skill suggestion system with ML integration
- Role selection (Mentor/Learner)

**Authentication Requirements:**
- Secure login with JWT tokens
- Password reset functionality
- Session management
- Role-based access control
- Remember me functionality
- Social media login integration (future)

**Profile Management:**
- Comprehensive user profiles
- Skill and expertise listings
- Availability scheduling
- Earnings tracking for mentors
- Learning progress for learners
- Profile verification system

### 5.1.2 Session Management Requirements

**Session Creation:**
- Intuitive session creation interface
- Pricing configuration in INR
- Category and skill tagging
- Schedule management
- Session description and thumbnails
- Participant limit settings

**Session Booking:**
- Real-time availability checking
- Secure payment processing
- Booking confirmation system
- Calendar integration
- Reminder notifications
- Cancellation policies

**Session Delivery:**
- WebRTC video communication
- Real-time chat functionality
- Screen sharing capabilities
- Session recording options
- Breakout room functionality
- Session quality monitoring

### 5.1.3 Payment System Requirements

**Core Payment Features:**
- Razorpay integration for INR transactions
- Secure payment processing
- Multiple payment methods support
- Automatic payment verification
- Refund processing capabilities
- Transaction history tracking

**Advanced Payment Features:**
- In-session gift/donation system
- Automatic mentor earnings calculation
- Payout request processing
- Payment analytics and reporting
- Tax calculation support
- Multi-currency support (future)

### 5.1.4 Recommendation System Requirements

**Intelligent Matching:**
- ML-based mentor-learner matching
- Skill compatibility analysis
- Learning style preferences
- Schedule compatibility
- Price range matching
- Geographic considerations

**Content Recommendations:**
- Personalized session recommendations
- Trending session identification
- Similar user preferences
- Historical learning patterns
- Popular mentor suggestions
- Category-based recommendations

## 5.2 Non-Functional Requirements

### 5.2.1 Performance Requirements

**Response Time:**
- Page load time: <2 seconds
- API response time: <200ms
- Database query time: <50ms
- WebRTC connection time: <3 seconds
- Payment processing: <5 seconds

**Throughput:**
- Concurrent users: 10,000+
- Simultaneous video sessions: 1,000+
- Database transactions: 10,000/second
- API requests: 100,000/hour
- File uploads: 1,000/minute

**Scalability:**
- Horizontal scaling capability
- Load balancing support
- Auto-scaling based on demand
- CDN integration for global reach
- Database partitioning support

### 5.2.2 Security Requirements

**Data Security:**
- Encryption at rest and in transit
- PCI DSS compliance for payments
- GDPR compliance for user data
- Regular security audits
- Penetration testing

**Authentication Security:**
- Multi-factor authentication
- Password policy enforcement
- Session timeout management
- Brute force protection
- Account lockout mechanisms

**Communication Security:**
- End-to-end encryption for video calls
- Secure WebSocket connections
- API authentication and authorization
- Rate limiting implementation
- DDoS protection

### 5.2.3 Usability Requirements

**User Experience:**
- Intuitive navigation design
- Mobile-responsive interface
- Accessibility compliance (WCAG 2.1)
- Multi-language support
- Consistent design patterns

**Learning Curve:**
- Minimal onboarding time
- Contextual help system
- Interactive tutorials
- Clear error messages
- Progressive disclosure

### 5.2.4 Reliability Requirements

**Availability:**
- System uptime: 99.9%
- Planned maintenance windows
- Disaster recovery procedures
- Backup and restore capabilities
- Failover mechanisms

**Error Handling:**
- Graceful error recovery
- User-friendly error messages
- Automatic retry mechanisms
- Logging and monitoring
- Alert systems for critical issues

## 5.3 System Constraints

### 5.3.1 Technical Constraints

**Browser Compatibility:**
- Chrome 90+, Firefox 88+, Safari 14+
- WebRTC support requirement
- JavaScript enabled
- Local storage availability
- Camera/microphone permissions

**Network Requirements:**
- Minimum 2 Mbps for video calls
- Stable internet connection
- Low latency for real-time features
- HTTPS requirement for WebRTC
- WebSocket support

**Device Constraints:**
- Minimum screen resolution: 1024x768
- Camera and microphone access
- Modern web browser requirement
- Sufficient processing power for video
- Adequate memory for real-time features

### 5.3.2 Business Constraints

**Regulatory Compliance:**
- Payment regulations (RBI guidelines)
- Data protection laws (GDPR, CCPA)
- Educational content guidelines
- Tax compliance requirements
- Accessibility standards

**Budget Constraints:**
- Development cost optimization
- Infrastructure cost management
- Third-party service costs
- Maintenance and support costs
- Marketing and user acquisition costs

---

# 6. PROPOSED SYSTEM

## 6.1 System Overview

PeerLearn represents a next-generation peer-to-peer learning platform that addresses all identified gaps in current educational technology. The proposed system integrates cutting-edge technologies to create a seamless, intelligent, and secure learning environment.

### 6.1.1 Core Innovation

**Intelligent Matching Engine:**
- Machine learning algorithms analyze user profiles, skills, and learning patterns
- Real-time compatibility scoring between mentors and learners
- Dynamic pricing suggestions based on demand and expertise levels
- Behavioral pattern recognition for improved matching accuracy

**Advanced WebRTC Implementation:**
- Direct peer-to-peer video communication without external servers
- Adaptive bitrate streaming for optimal quality
- Advanced audio processing with noise cancellation
- Screen sharing with annotation capabilities

**Integrated Payment Ecosystem:**
- Seamless Razorpay integration for INR transactions
- In-session micro-payments and tipping system
- Automatic earnings distribution to mentors
- Comprehensive financial analytics and reporting

## 6.2 System Architecture

### 6.2.1 Microservices Architecture

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   User Service  │  │ Session Service │  │ Payment Service │
│                 │  │                 │  │                 │
│ • Registration  │  │ • Session Mgmt  │  │ • Razorpay API  │
│ • Authentication│  │ • WebRTC Setup  │  │ • Transactions  │
│ • Profile Mgmt  │  │ • Video Rooms   │  │ • Gift System   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ML/AI Service  │  │ Notification    │  │ Analytics       │
│                 │  │ Service         │  │ Service         │
│ • Recommendations│  │                 │  │                 │
│ • Skill Matching│  │ • WebSocket     │  │ • User Metrics  │
│ • Trend Analysis│  │ • Email Alerts  │  │ • Performance   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.2.2 Technology Stack

**Frontend Layer:**
- **Alpine.js 3.13.3:** Reactive JavaScript framework for dynamic interfaces
- **Tailwind CSS 3.3.6:** Utility-first CSS for responsive design
- **WebRTC APIs:** Direct browser-to-browser communication
- **Progressive Web App (PWA):** Mobile app-like experience

**Backend Layer:**
- **Django 5.2.1:** Python web framework with MVT architecture
- **Django REST Framework:** RESTful API development
- **Django Channels:** WebSocket support for real-time features
- **Celery:** Asynchronous task processing

**Database Layer:**
- **PostgreSQL:** Primary relational database
- **Redis:** Caching and session storage
- **File System/S3:** Media file storage
- **Elasticsearch:** Search and analytics (future)

**Infrastructure Layer:**
- **Docker:** Containerization for deployment
- **Nginx:** Reverse proxy and load balancer
- **Gunicorn/Daphne:** ASGI/WSGI servers
- **AWS/DigitalOcean:** Cloud hosting platform

## 6.3 Key Features and Innovations

### 6.3.1 Enhanced Registration System

**Smart Skill Suggestions:**
```python
class SkillSuggestionEngine:
    def get_suggestions(self, user_input, domain):
        # ML-powered skill matching
        popular_skills = self.get_popular_skills(domain)
        trending_skills = self.get_trending_skills()
        matched_skills = self.match_skills(user_input)
        
        return self.rank_suggestions(
            popular_skills, 
            trending_skills, 
            matched_skills
        )
```

**Real-time Validation:**
- Email availability checking
- Password strength indicators
- Profile completeness scoring
- Skill relevance verification

### 6.3.2 Advanced WebRTC Implementation

**Peer-to-Peer Video System:**
```javascript
class WebRTCManager {
    constructor() {
        this.peerConnection = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        });
        this.setupEventHandlers();
    }
    
    async startSession(sessionId) {
        await this.getUserMedia();
        await this.createOffer();
        this.connectWebSocket(sessionId);
    }
}
```

**Features:**
- HD video quality (1080p)
- Adaptive bitrate streaming
- Noise cancellation
- Screen sharing with annotations
- Recording capabilities
- Mobile optimization

### 6.3.3 Intelligent Recommendation Engine

**Machine Learning Algorithms:**
```python
class RecommendationEngine:
    def __init__(self):
        self.content_filter = ContentBasedFilter()
        self.collaborative_filter = CollaborativeFilter()
        self.popularity_filter = PopularityBasedFilter()
    
    def get_recommendations(self, user):
        content_recs = self.content_filter.recommend(user)
        collab_recs = self.collaborative_filter.recommend(user)
        popular_recs = self.popularity_filter.recommend()
        
        return self.ensemble_recommendations(
            content_recs, collab_recs, popular_recs
        )
```

**Recommendation Types:**
- Content-based filtering (skill matching)
- Collaborative filtering (similar users)
- Popularity-based recommendations
- Hybrid ensemble methods

### 6.3.4 Secure Payment System

**Razorpay Integration:**
```python
class PaymentProcessor:
    def __init__(self):
        self.razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, 
                  settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, session_id, user_id):
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': 'INR',
            'notes': {
                'session_id': session_id,
                'user_id': user_id
            }
        }
        return self.razorpay_client.order.create(data=order_data)
```

**Payment Features:**
- Session-based payments
- In-session gifting system
- Automatic mentor earnings
- Secure transaction processing
- Comprehensive payment history

## 6.4 System Benefits

### 6.4.1 For Learners

**Enhanced Learning Experience:**
- Personalized mentor matching
- High-quality video sessions
- Flexible scheduling
- Affordable pricing
- Progress tracking

**Advanced Features:**
- Real-time skill suggestions
- Session recording access
- Multiple payment options
- Mobile-friendly interface
- 24/7 platform availability

### 6.4.2 For Mentors

**Monetization Opportunities:**
- Flexible pricing control
- Multiple income streams
- Gift/tip earning potential
- Automated payment processing
- Comprehensive analytics

**Teaching Tools:**
- Advanced video features
- Screen sharing capabilities
- Session management tools
- Student progress tracking
- Professional dashboard

### 6.4.3 For Platform

**Business Advantages:**
- Scalable revenue model
- Low operational costs
- Global market reach
- Data-driven insights
- Network effects

**Technical Benefits:**
- Modern architecture
- High performance
- Security compliance
- Easy maintenance
- Future-ready design

---

# 7. FEASIBILITY STUDY

## 7.1 Technical Feasibility

### 7.1.1 Technology Assessment

**Frontend Technologies:**
- **Alpine.js:** Mature framework with excellent browser support
- **Tailwind CSS:** Production-ready utility framework
- **WebRTC:** Well-supported by modern browsers (95%+ compatibility)
- **PWA Technologies:** Native app-like experience possible

**Backend Technologies:**
- **Django 5.2.1:** Stable, secure, and well-documented framework
- **PostgreSQL:** Enterprise-grade database with excellent performance
- **Redis:** Proven solution for caching and real-time features
- **Docker:** Industry-standard containerization

**Integration Capabilities:**
- **Razorpay API:** Comprehensive documentation and SDKs
- **WebSocket Support:** Mature implementation through Django Channels
- **Machine Learning:** scikit-learn provides robust algorithms
- **Cloud Deployment:** Multiple hosting options available

### 7.1.2 Scalability Analysis

**Performance Projections:**
```
User Load Scenarios:
├── Phase 1: 1,000 users, 100 concurrent sessions
├── Phase 2: 10,000 users, 1,000 concurrent sessions  
├── Phase 3: 100,000 users, 10,000 concurrent sessions
└── Phase 4: 1,000,000 users, 100,000 concurrent sessions
```

**Infrastructure Requirements:**
- **Phase 1:** Single server deployment (4 CPU, 8GB RAM)
- **Phase 2:** Load balanced setup (2 servers, 8 CPU, 16GB RAM each)
- **Phase 3:** Microservices architecture (10+ servers, auto-scaling)
- **Phase 4:** Multi-region deployment with CDN

**Database Scaling:**
- Read replicas for improved performance
- Database sharding for large datasets
- Caching layers for frequently accessed data
- Archive strategies for historical data

### 7.1.3 Security Assessment

**Data Protection:**
- End-to-end encryption for video calls
- HTTPS enforcement for all communications
- JWT token-based authentication
- SQL injection prevention through ORM
- XSS protection with template escaping

**Payment Security:**
- PCI DSS compliance through Razorpay
- Secure webhook signature verification
- Encrypted payment data storage
- Fraud detection mechanisms
- Regular security audits

**Privacy Compliance:**
- GDPR compliance for European users
- Data minimization principles
- User consent mechanisms
- Right to data deletion
- Transparent privacy policies

## 7.2 Economic Feasibility

### 7.2.1 Development Cost Analysis

**Initial Development Costs:**
```
Development Phase Costs:
├── Core Platform Development: $50,000
├── WebRTC Implementation: $15,000
├── Payment Integration: $10,000
├── ML/AI Features: $20,000
├── Testing & QA: $15,000
├── UI/UX Design: $10,000
└── Total Development: $120,000
```

**Technology Costs (Annual):**
```
Technology Stack Costs:
├── Cloud Hosting (AWS/DigitalOcean): $12,000
├── Database Management: $3,000
├── CDN Services: $2,000
├── Monitoring & Analytics: $2,000
├── Third-party APIs: $3,000
└── Total Annual Tech Costs: $22,000
```

**Operational Costs (Annual):**
```
Operational Expenses:
├── Customer Support: $30,000
├── Marketing & Acquisition: $50,000
├── Legal & Compliance: $10,000
├── Insurance: $5,000
├── Administration: $15,000
└── Total Annual Operations: $110,000
```

### 7.2.2 Revenue Model Analysis

**Primary Revenue Streams:**
1. **Commission on Sessions:** 10-15% commission on paid sessions
2. **Subscription Plans:** Premium features for mentors and learners
3. **Gift Transaction Fees:** Small percentage on in-session gifts
4. **Featured Listings:** Promoted mentor profiles
5. **Corporate Training:** B2B enterprise solutions

**Revenue Projections:**
```
Year 1: 1,000 users, $50,000 revenue
Year 2: 10,000 users, $500,000 revenue
Year 3: 50,000 users, $2,500,000 revenue
Year 4: 200,000 users, $10,000,000 revenue
Year 5: 500,000 users, $25,000,000 revenue
```

**Break-even Analysis:**
- Break-even point: Month 18 with 5,000 active users
- Customer acquisition cost: $50 per user
- Customer lifetime value: $200 per user
- Monthly recurring revenue target: $100,000 by Year 2

### 7.2.3 Market Opportunity

**Total Addressable Market (TAM):**
- Global online education market: $350 billion
- Peer-to-peer learning segment: $15 billion
- Video-based learning: $8 billion

**Serviceable Addressable Market (SAM):**
- English-speaking markets: $3 billion
- Technology-focused learning: $1 billion
- Professional skill development: $500 million

**Serviceable Obtainable Market (SOM):**
- Realistic market capture: $50 million
- Target market share: 0.1% of SAM
- Geographic focus: India, US, Europe

## 7.3 Operational Feasibility

### 7.3.1 Team Requirements

**Development Team:**
```
Core Development Team:
├── Backend Developers (2): Django, Python, APIs
├── Frontend Developers (2): Alpine.js, WebRTC, CSS
├── DevOps Engineer (1): Docker, AWS, CI/CD
├── UI/UX Designer (1): User experience design
├── QA Engineer (1): Testing and quality assurance
└── Project Manager (1): Coordination and planning
```

**Specialized Roles:**
- **ML Engineer:** Recommendation engine development
- **Security Consultant:** Security audits and compliance
- **Payment Specialist:** Razorpay integration expert
- **Mobile Developer:** Future mobile app development

**Support Team:**
- **Customer Success:** User onboarding and support
- **Content Moderator:** Quality control and safety
- **Marketing Specialist:** User acquisition and retention
- **Legal Advisor:** Compliance and regulatory issues

### 7.3.2 Infrastructure Planning

**Development Environment:**
- Local development with Docker containers
- Staging environment for testing
- Continuous integration/deployment pipeline
- Code review and quality assurance processes

**Production Environment:**
- Multi-environment setup (dev, staging, production)
- Automated deployment processes
- Monitoring and alerting systems
- Backup and disaster recovery procedures

**Growth Planning:**
- Horizontal scaling capabilities
- Load balancing implementation
- Database optimization strategies
- CDN integration for global performance

### 7.3.3 Risk Assessment

**Technical Risks:**
- **WebRTC Compatibility:** Mitigation through fallback options
- **Scalability Challenges:** Addressed with microservices architecture
- **Security Vulnerabilities:** Regular audits and updates
- **Third-party Dependencies:** Multiple vendor relationships

**Business Risks:**
- **Market Competition:** Differentiation through unique features
- **User Acquisition:** Comprehensive marketing strategy
- **Regulatory Changes:** Legal compliance monitoring
- **Economic Downturns:** Flexible pricing models

**Operational Risks:**
- **Team Scaling:** Structured hiring processes
- **Quality Control:** Automated testing and review processes
- **Customer Support:** Scalable support systems
- **Data Management:** Robust backup and recovery procedures

## 7.4 Schedule Feasibility

### 7.4.1 Development Timeline

**Phase 1: Foundation (Months 1-3)**
```
Month 1:
├── Project setup and team onboarding
├── Core Django application structure
├── Database design and implementation
└── Basic authentication system

Month 2:
├── User registration and profile management
├── Session management system
├── Basic UI/UX implementation
└── Payment integration (basic)

Month 3:
├── WebRTC implementation
├── Real-time features (WebSocket)
├── Basic recommendation engine
└── Testing and bug fixes
```

**Phase 2: Core Features (Months 4-6)**
```
Month 4:
├── Advanced WebRTC features
├── Enhanced UI/UX with animations
├── ML-powered recommendations
└── Comprehensive testing

Month 5:
├── Payment system completion
├── Gift/donation features
├── Analytics and dashboards
└── Performance optimization

Month 6:
├── Security implementation
├── Mobile responsiveness
├── User acceptance testing
└── Production deployment preparation
```

**Phase 3: Launch Preparation (Months 7-8)**
```
Month 7:
├── Security audits and compliance
├── Performance testing and optimization
├── User documentation and help system
└── Marketing material preparation

Month 8:
├── Beta testing with selected users
├── Bug fixes and final optimizations
├── Production deployment
└── Soft launch and monitoring
```

**Phase 4: Growth and Optimization (Months 9-12)**
```
Months 9-12:
├── User feedback integration
├── Feature enhancements
├── Scaling and performance improvements
└── Advanced features development
```

### 7.4.2 Resource Allocation

**Development Resources:**
- 40% Backend development (Django, APIs, Database)
- 30% Frontend development (Alpine.js, WebRTC, UI)
- 15% DevOps and infrastructure
- 10% Testing and quality assurance
- 5% Project management and coordination

**Budget Allocation:**
- 60% Development team salaries
- 20% Infrastructure and technology costs
- 10% Marketing and user acquisition
- 5% Legal and compliance
- 5% Contingency and miscellaneous

---

# 8. SYSTEM SPECIFICATION

## 8.1 Functional Specifications

### 8.1.1 User Management Module

**User Registration System:**
```python
class UserRegistrationSpecification:
    """
    Enhanced multi-step registration with ML-powered features
    """
    
    FIELDS_REQUIRED = [
        'username', 'email', 'password', 'role', 
        'first_name', 'last_name', 'skills'
    ]
    
    VALIDATION_RULES = {
        'email': 'Real-time availability check via API',
        'password': 'Minimum 8 characters, complexity requirements',
        'username': 'Unique, alphanumeric with underscores',
        'skills': 'ML-powered suggestions based on domain'
    }
    
    FEATURES = {
        'step_wizard': 'Multi-step form with progress indicator',
        'image_upload': 'Profile picture with preview',
        'skill_suggestions': 'Real-time ML-based recommendations',
        'email_verification': 'Real-time validation API'
    }
```

**Authentication Specifications:**
- JWT token-based authentication
- Session timeout: 24 hours for regular users, 1 hour for admin
- Password policy: Minimum 8 characters, mixed case, numbers, symbols
- Account lockout: 5 failed attempts, 15-minute cooldown
- Two-factor authentication support (future enhancement)

**Profile Management:**
```python
class ProfileSpecification:
    USER_ROLES = ['mentor', 'learner', 'admin']
    
    MENTOR_FIELDS = [
        'expertise_areas', 'hourly_rate', 'availability_schedule',
        'teaching_experience', 'certifications', 'languages'
    ]
    
    LEARNER_FIELDS = [
        'learning_goals', 'skill_level', 'preferred_schedule',
        'budget_range', 'learning_style', 'interests'
    ]
    
    COMMON_FIELDS = [
        'profile_image', 'bio', 'location', 'timezone',
        'social_links', 'verification_status'
    ]
```

### 8.1.2 Session Management Module

**Session Creation Specifications:**
```python
class SessionSpecification:
    """
    Comprehensive session management with pricing and scheduling
    """
    
    REQUIRED_FIELDS = {
        'title': 'max_length=200',
        'description': 'TextField with rich text support',
        'price': 'DecimalField, INR currency',
        'schedule': 'DateTimeField with timezone support',
        'duration': 'IntegerField in minutes',
        'max_participants': 'IntegerField, default=10'
    }
    
    OPTIONAL_FIELDS = {
        'thumbnail': 'ImageField with auto-resize',
        'category': 'ChoiceField from predefined categories',
        'skills': 'TextField, comma-separated for ML matching',
        'prerequisites': 'TextField for required knowledge',
        'materials': 'FileField for downloadable resources'
    }
    
    STATUS_CHOICES = [
        'draft', 'scheduled', 'live', 'completed', 'cancelled'
    ]
```

**Booking System Specifications:**
```python
class BookingSpecification:
    """
    Secure booking system with payment integration
    """
    
    BOOKING_PROCESS = [
        'session_selection',
        'payment_processing',
        'confirmation',
        'calendar_integration',
        'reminder_notifications'
    ]
    
    PAYMENT_INTEGRATION = {
        'gateway': 'Razorpay',
        'currency': 'INR',
        'methods': ['UPI', 'Cards', 'Net Banking', 'Wallets'],
        'security': 'PCI DSS compliant'
    }
    
    BOOKING_STATES = [
        'pending_payment', 'confirmed', 'completed', 
        'cancelled', 'refunded', 'no_show'
    ]
```

### 8.1.3 WebRTC Video System

**Video Communication Specifications:**
```javascript
class WebRTCSpecification {
    constructor() {
        this.configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ],
            iceCandidatePoolSize: 10
        };
        
        this.mediaConstraints = {
            video: {
                width: { min: 640, ideal: 1280, max: 1920 },
                height: { min: 480, ideal: 720, max: 1080 },
                frameRate: { min: 15, ideal: 30, max: 60 }
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        };
    }
}
```

**Features Specifications:**
- **Video Quality:** Adaptive bitrate (240p to 1080p)
- **Audio Processing:** Echo cancellation, noise suppression
- **Screen Sharing:** Full screen or application window
- **Recording:** Server-side recording with cloud storage
- **Mobile Support:** Responsive design for mobile browsers
- **Connection Quality:** Real-time monitoring and adaptation

### 8.1.4 Payment System Module

**Razorpay Integration Specifications:**
```python
class PaymentSystemSpecification:
    """
    Comprehensive payment processing with Razorpay
    """
    
    RAZORPAY_CONFIG = {
        'api_version': '2023-08-01',
        'currency': 'INR',
        'webhook_secret': 'environment_variable',
        'auto_capture': True,
        'payment_methods': [
            'card', 'netbanking', 'wallet', 'upi', 'bank_transfer'
        ]
    }
    
    PAYMENT_FLOWS = {
        'session_booking': 'Full payment before session',
        'gift_payments': 'Real-time micro-transactions',
        'mentor_payouts': 'Automated earnings distribution',
        'refund_processing': 'Automated refund handling'
    }
    
    SECURITY_FEATURES = [
        'signature_verification',
        'webhook_authentication',
        'payment_encryption',
        'fraud_detection'
    ]
```

### 8.1.5 Recommendation Engine

**Machine Learning Specifications:**
```python
class RecommendationEngineSpecification:
    """
    Advanced ML-based recommendation system
    """
    
    ALGORITHMS = {
        'content_based': 'TF-IDF vectorization for skill matching',
        'collaborative': 'Matrix factorization for user similarity',
        'popularity': 'Weighted popularity based on metrics',
        'hybrid': 'Ensemble method combining all approaches'
    }
    
    FEATURES = {
        'skill_matching': 'Cosine similarity on skill vectors',
        'behavior_analysis': 'User interaction pattern analysis',
        'session_popularity': 'Real-time popularity metrics',
        'temporal_patterns': 'Time-based recommendation adjustments'
    }
    
    PERFORMANCE_METRICS = {
        'precision': 'Relevant recommendations / Total recommendations',
        'recall': 'Relevant recommendations / Total relevant items',
        'diversity': 'Variety in recommended content',
        'novelty': 'Introduction of new content to users'
    }
```

## 8.2 Performance Specifications

### 8.2.1 Response Time Requirements

**Page Load Performance:**
```
Performance Benchmarks:
├── Landing Page: < 1.5 seconds
├── Dashboard Load: < 2.0 seconds
├── Session List: < 1.8 seconds
├── Profile Pages: < 1.5 seconds
├── Payment Pages: < 2.5 seconds
└── Video Room Entry: < 3.0 seconds
```

**API Response Times:**
```
API Performance Targets:
├── Authentication: < 200ms
├── Session Search: < 300ms
├── Payment Processing: < 500ms
├── Recommendation Generation: < 400ms
├── Real-time Notifications: < 100ms
└── File Uploads: < 2 seconds per MB
```

**Database Performance:**
```
Database Query Targets:
├── Simple Queries: < 10ms
├── Complex Joins: < 50ms
├── Search Operations: < 100ms
├── Analytics Queries: < 200ms
├── Bulk Operations: < 500ms
└── Report Generation: < 1 second
```

### 8.2.2 Scalability Specifications

**Concurrent User Support:**
```
Scalability Targets:
├── Phase 1: 1,000 concurrent users
├── Phase 2: 10,000 concurrent users
├── Phase 3: 50,000 concurrent users
├── Phase 4: 200,000 concurrent users
└── Ultimate: 1,000,000 concurrent users
```

**Video Session Capacity:**
```
Video Session Limits:
├── Simultaneous Sessions: 10,000+
├── WebRTC Connections: 50,000+
├── Video Quality: Adaptive (240p-1080p)
├── Audio Quality: 48kHz stereo
└── Screen Share: 1080p @ 30fps
```

### 8.2.3 Availability Specifications

**System Uptime Requirements:**
- **Target Uptime:** 99.9% (8.77 hours downtime per year)
- **Planned Maintenance:** Maximum 4 hours per month
- **Disaster Recovery:** RTO < 1 hour, RPO < 15 minutes
- **Backup Frequency:** Real-time for critical data, daily for all data

**Monitoring and Alerting:**
- **Health Checks:** Every 30 seconds
- **Performance Monitoring:** Real-time metrics
- **Error Tracking:** Immediate alerts for critical issues
- **Capacity Planning:** Proactive scaling based on usage patterns

---

# 9. HARDWARE SPECIFICATION

## 9.1 Development Environment Requirements

### 9.1.1 Developer Workstation Specifications

**Minimum Requirements:**
```
Development Machine Specs:
├── Processor: Intel i5 or AMD Ryzen 5 (4 cores, 2.5GHz+)
├── Memory: 16GB RAM (32GB recommended)
├── Storage: 512GB SSD (1TB recommended)
├── Graphics: Integrated graphics (dedicated GPU for testing)
├── Network: Gigabit Ethernet or 802.11ac WiFi
└── OS: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
```

**Recommended Development Setup:**
```
Optimal Development Environment:
├── Processor: Intel i7/i9 or AMD Ryzen 7/9 (8+ cores)
├── Memory: 32GB RAM (64GB for ML development)
├── Storage: 1TB NVMe SSD + 2TB HDD
├── Graphics: NVIDIA GTX 1660 or better (for ML/AI work)
├── Display: Dual 27" monitors (4K recommended)
├── Webcam: 1080p camera for WebRTC testing
├── Audio: Professional headset for video call testing
└── Network: Stable high-speed internet (100+ Mbps)
```

**Development Tools Hardware:**
- **Testing Devices:** Various smartphones and tablets
- **Network Testing:** Multiple internet connections for testing
- **Load Testing:** Access to cloud instances for stress testing
- **Backup Solutions:** External storage for code and data backup

### 9.1.2 Development Infrastructure

**Local Development Server:**
```
Local Server Specifications:
├── Processor: Intel Xeon or AMD EPYC (16+ cores)
├── Memory: 64GB RAM
├── Storage: 2TB NVMe SSD (RAID 1)
├── Network: 10Gbps Ethernet
├── OS: Ubuntu Server 22.04 LTS
└── Virtualization: Docker and Kubernetes support
```

**Testing Environment:**
- **Physical Devices:** iOS and Android devices for mobile testing
- **Network Simulation:** Tools for testing different connection speeds
- **Load Testing Hardware:** Distributed testing nodes
- **Security Testing:** Dedicated penetration testing environment

## 9.2 Production Environment Specifications

### 9.2.1 Cloud Infrastructure Requirements

**Phase 1 Deployment (1,000 users):**
```
Initial Production Setup:
├── Web Servers: 2x AWS EC2 t3.large
│   ├── vCPUs: 2 per instance
│   ├── Memory: 8GB per instance
│   ├── Storage: 100GB SSD per instance
│   └── Network: Up to 5 Gbps
├── Database Server: 1x AWS RDS db.t3.medium
│   ├── vCPUs: 2
│   ├── Memory: 4GB
│   ├── Storage: 500GB SSD
│   └── Backup: Automated daily backups
├── Redis Cache: 1x AWS ElastiCache cache.t3.micro
│   ├── Memory: 0.5GB
│   └── Network: High performance
└── Load Balancer: AWS Application Load Balancer
```

**Phase 2 Scaling (10,000 users):**
```
Scaled Production Environment:
├── Web Servers: 4x AWS EC2 c5.xlarge
│   ├── vCPUs: 4 per instance
│   ├── Memory: 8GB per instance
│   ├── Storage: 200GB SSD per instance
│   └── Auto Scaling: 2-8 instances
├── Database: AWS RDS db.m5.large (Multi-AZ)
│   ├── vCPUs: 2
│   ├── Memory: 8GB
│   ├── Storage: 1TB SSD
│   └── Read Replicas: 2 instances
├── Redis Cluster: AWS ElastiCache cache.m5.large
│   ├── Memory: 6.38GB
│   └── Cluster Mode: Enabled
└── CDN: AWS CloudFront global distribution
```

**Phase 3 Enterprise Scale (100,000+ users):**
```
Enterprise Production Architecture:
├── Microservices: Kubernetes cluster
│   ├── Node Count: 20+ nodes
│   ├── Instance Type: c5.2xlarge
│   ├── Auto Scaling: Dynamic based on load
│   └── Multi-Region: US, Europe, Asia
├── Database Cluster: AWS Aurora PostgreSQL
│   ├── Multi-Master: 3 writer nodes
│   ├── Read Replicas: 10+ reader nodes
│   ├── Storage: Auto-scaling up to 128TB
│   └── Global Database: Cross-region replication
├── Cache Layer: Redis Cluster
│   ├── Node Type: cache.r5.2xlarge
│   ├── Cluster Size: 6+ nodes
│   └── Memory: 50GB+ total
├── Search: Elasticsearch cluster
│   ├── Node Count: 6+ nodes
│   ├── Instance Type: m5.large
│   └── Storage: 1TB SSD per node
└── Media Storage: AWS S3 + CloudFront
    ├── Storage Class: Intelligent Tiering
    ├── CDN: Global edge locations
    └── Bandwidth: Unlimited
```

### 9.2.2 Network Infrastructure

**Bandwidth Requirements:**
```
Network Capacity Planning:
├── Video Streaming: 50Mbps per concurrent session
├── API Traffic: 1Mbps per 1000 users
├── Static Content: CDN-cached, minimal origin load
├── Database Replication: 10Mbps between regions
├── Backup Traffic: 100Mbps during backup windows
└── Total Capacity: 10Gbps+ for peak loads
```

**Security Infrastructure:**
- **DDoS Protection:** AWS Shield Advanced
- **WAF:** Web Application Firewall with custom rules
- **VPN:** Site-to-site VPN for administrative access
- **Monitoring:** Distributed monitoring across regions

### 9.2.3 Storage Requirements

**Database Storage:**
```
Database Storage Planning:
├── User Data: 1KB per user profile
├── Session Data: 5KB per session record
├── Chat Messages: 0.1KB per message
├── Payment Records: 2KB per transaction
├── Analytics Data: 10KB per user per month
├── Backup Storage: 2x primary storage
└── Growth Rate: 20% monthly storage increase
```

**Media Storage:**
```
Media File Storage:
├── Profile Images: 500KB average per user
├── Session Thumbnails: 200KB per session
├── Video Recordings: 100MB per hour (optional)
├── Document Uploads: 5MB average per file
├── CDN Cache: 50% of total media storage
└── Backup: Full media backup monthly
```

## 9.3 Client Device Requirements

### 9.3.1 Minimum Client Specifications

**Desktop/Laptop Requirements:**
```
Minimum Client Hardware:
├── Processor: Dual-core 2.0GHz
├── Memory: 4GB RAM
├── Storage: 1GB free space
├── Graphics: Hardware-accelerated video decoding
├── Camera: 720p webcam (for mentors)
├── Microphone: Built-in or external microphone
├── Speakers/Headphones: Audio output device
└── Network: 5Mbps download, 2Mbps upload
```

**Mobile Device Requirements:**
```
Mobile Hardware Specifications:
├── iOS: iPhone 8 or newer, iOS 14+
├── Android: Android 8.0+, 3GB RAM minimum
├── Camera: Front-facing camera for video calls
├── Microphone: Built-in microphone
├── Storage: 500MB free space
├── Network: 3Mbps download, 1Mbps upload
└── Browser: Safari 14+, Chrome 90+, Firefox 88+
```

### 9.3.2 Recommended Client Specifications

**Optimal User Experience:**
```
Recommended Client Setup:
├── Processor: Quad-core 2.5GHz+
├── Memory: 8GB RAM
├── Storage: 5GB free space
├── Graphics: Dedicated GPU or modern integrated
├── Camera: 1080p webcam with autofocus
├── Audio: Noise-cancelling headset
├── Display: 1920x1080 minimum resolution
└── Network: 25Mbps download, 10Mbps upload
```

**Professional Mentor Setup:**
```
Professional Hardware Recommendations:
├── Processor: Intel i7 or AMD Ryzen 7
├── Memory: 16GB RAM
├── Storage: SSD with 10GB free space
├── Camera: 4K webcam with good low-light performance
├── Audio: Professional microphone and headphones
├── Lighting: Ring light or professional lighting setup
├── Display: Dual monitors (27" or larger)
├── Network: Fiber internet (100+ Mbps)
└── Backup: UPS for power backup during sessions
```

## 9.4 Monitoring and Management Hardware

### 9.4.1 Monitoring Infrastructure

**System Monitoring:**
```
Monitoring Hardware Requirements:
├── Monitoring Servers: 2x dedicated instances
│   ├── Instance Type: t3.medium
│   ├── Memory: 4GB RAM
│   ├── Storage: 200GB SSD
│   └── Purpose: Metrics collection and alerting
├── Log Aggregation: Elasticsearch cluster
│   ├── Instance Count: 3 nodes
│   ├── Instance Type: m5.large
│   ├── Memory: 8GB per node
│   └── Storage: 500GB SSD per node
└── Analytics: Dedicated analytics server
    ├── Instance Type: c5.xlarge
    ├── Memory: 8GB RAM
    ├── vCPUs: 4
    └── Storage: 1TB SSD
```

### 9.4.2 Backup and Recovery

**Backup Infrastructure:**
```
Backup Hardware Specifications:
├── Primary Backup: AWS S3 storage
│   ├── Storage Class: Standard-IA
│   ├── Replication: Cross-region
│   └── Retention: 7 years
├── Secondary Backup: AWS Glacier
│   ├── Storage Class: Deep Archive
│   ├── Retrieval Time: 12 hours
│   └── Cost: Ultra-low cost storage
├── Database Backups: Automated snapshots
│   ├── Frequency: Every 6 hours
│   ├── Retention: 30 days
│   └── Cross-region: Yes
└── Disaster Recovery: Hot standby environment
    ├── Infrastructure: 50% of production capacity
    ├── RTO: < 1 hour
    └── RPO: < 15 minutes
```

---

# 10. SOFTWARE SPECIFICATION

## 10.1 Operating System Requirements

### 10.1.1 Development Environment

**Local Development OS:**
```
Supported Development Platforms:
├── Windows 10/11 Professional
│   ├── WSL2 (Windows Subsystem for Linux)
│   ├── Docker Desktop for Windows
│   ├── Git for Windows
│   └── Visual Studio Code
├── macOS 10.15 Catalina or newer
│   ├── Homebrew package manager
│   ├── Docker Desktop for Mac
│   ├── Xcode Command Line Tools
│   └── Terminal with Zsh/Bash
└── Ubuntu 20.04 LTS or newer
    ├── Native Docker support
    ├── Built-in package managers
    ├── Native terminal environment
    └── Direct deployment compatibility
```

**Development Tools:**
```
Essential Development Software:
├── Python 3.11+ with pip package manager
├── Node.js 18+ with npm/yarn
├── PostgreSQL 15+ for database development
├── Redis 7+ for caching and sessions
├── Git 2.30+ for version control
├── Docker 20+ for containerization
├── Visual Studio Code with Python extension
└── Postman for API testing
```

### 10.1.2 Production Environment

**Server Operating System:**
```
Production OS Specifications:
├── Ubuntu Server 22.04 LTS
│   ├── Long-term support until 2027
│   ├── Regular security updates
│   ├── Container optimization
│   └── Cloud-native features
├── Alternative: CentOS 8 / RHEL 8
│   ├── Enterprise-grade stability
│   ├── Commercial support available
│   ├── Security-focused distribution
│   └── Container platform ready
└── Container Runtime: Docker CE 24+
    ├── Containerd runtime
    ├── Docker Compose 2.0+
    ├── Kubernetes support
    └── Security scanning tools
```

## 10.2 Programming Languages and Frameworks

### 10.2.1 Backend Technology Stack

**Python and Django Framework:**
```python
# Core Backend Technologies
BACKEND_STACK = {
    'language': 'Python 3.11.8',
    'framework': 'Django 5.2.1',
    'rest_api': 'Django REST Framework 3.14.0',
    'async_support': 'Django Channels 4.0.0',
    'database_orm': 'Django ORM with PostgreSQL',
    'authentication': 'JWT + Django built-in auth',
    'validation': 'Django Forms + DRF Serializers',
    'middleware': 'Custom + Django built-in middleware'
}

# Key Django Components
DJANGO_COMPONENTS = {
    'models': 'Database layer with ORM',
    'views': 'API views and class-based views',
    'templates': 'Jinja2-style template engine',
    'forms': 'Form handling and validation',
    'admin': 'Administrative interface',
    'signals': 'Event-driven programming',
    'management': 'Custom management commands',
    'testing': 'Built-in testing framework'
}
```

**Django Extensions and Packages:**
```python
# Essential Django Packages
DJANGO_PACKAGES = {
    'channels': '4.0.0',           # WebSocket support
    'channels-redis': '4.1.0',    # Redis channel layer
    'daphne': '4.2.0',            # ASGI server
    'django-cors-headers': '4.3.1', # CORS handling
    'django-environ': '0.11.2',   # Environment variables
    'django-extensions': '3.2.3', # Development utilities
    'django-debug-toolbar': '4.2.0', # Development debugging
    'django-ratelimit': '4.1.0',  # Rate limiting
    'django-storages': '1.14.2',  # File storage backends
}
```

### 10.2.2 Frontend Technology Stack

**JavaScript and Alpine.js:**
```javascript
// Frontend Technology Specifications
const FRONTEND_STACK = {
    framework: 'Alpine.js 3.13.3',
    styling: 'Tailwind CSS 3.3.6',
    webrtc: 'Native WebRTC APIs',
    http_client: 'Fetch API',
    websockets: 'Native WebSocket API',
    forms: 'HTML5 + Alpine.js reactivity',
    animations: 'CSS transitions + Alpine.js',
    responsive: 'Mobile-first responsive design'
};

// Alpine.js Component Structure
class ComponentSpecification {
    constructor() {
        this.data = {
            // Reactive data properties
        };
        this.methods = {
            // Component methods
        };
        this.computed = {
            // Computed properties
        };
        this.lifecycle = {
            // Lifecycle hooks
        };
    }
}
```

**CSS Framework and Styling:**
```css
/* Tailwind CSS Configuration */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom Component Classes */
.btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200;
}

.card {
    @apply bg-white rounded-lg shadow-md p-6 border border-gray-200;
}

.glass-effect {
    @apply bg-white bg-opacity-20 backdrop-blur-lg rounded-lg border border-white border-opacity-20;
}
```

### 10.2.3 Database Technology

**PostgreSQL Database System:**
```sql
-- Database Specifications
-- PostgreSQL 15+ with the following extensions:
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Performance optimization settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET random_page_cost = 1.1;
```

**Redis Configuration:**
```redis
# Redis Configuration for Sessions and Caching
# Version: Redis 7.0+

# Memory Configuration
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence Configuration
save 900 1
save 300 10
save 60 10000

# Network Configuration
timeout 300
tcp-keepalive 300

# Security Configuration
requirepass strong_password_here
```

## 10.3 Third-Party Integrations

### 10.3.1 Payment Processing

**Razorpay Integration:**
```python
# Razorpay SDK Configuration
RAZORPAY_CONFIGURATION = {
    'version': 'razorpay==1.3.0',
    'api_version': '2023-08-01',
    'supported_methods': [
        'card', 'netbanking', 'wallet', 'upi', 
        'bank_transfer', 'emandate', 'nach'
    ],
    'webhook_events': [
        'payment.captured', 'payment.failed',
        'order.paid', 'subscription.charged',
        'refund.created', 'settlement.processed'
    ],
    'security_features': [
        'webhook_signature_verification',
        'payment_signature_verification',
        'amount_validation',
        'currency_validation'
    ]
}

# Payment Processing Implementation
import razorpay

class RazorpayIntegration:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, 
                  settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency='INR'):
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': currency,
            'payment_capture': 1
        }
        return self.client.order.create(data=order_data)
```

### 10.3.2 Machine Learning Libraries

**scikit-learn Integration:**
```python
# Machine Learning Technology Stack
ML_STACK = {
    'core_library': 'scikit-learn==1.3.2',
    'data_processing': 'pandas==1.5.3',
    'numerical_computing': 'numpy==1.25.2',
    'scientific_computing': 'scipy==1.11.4',
    'text_processing': 'nltk==3.8.1',
    'feature_extraction': 'TfidfVectorizer',
    'similarity_metrics': 'cosine_similarity',
    'clustering': 'KMeans, DBSCAN',
    'recommendation': 'NearestNeighbors'
}

# Recommendation Engine Implementation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

class MLRecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.similarity_model = NearestNeighbors(
            n_neighbors=10,
            metric='cosine'
        )
```

### 10.3.3 Real-time Communication

**WebRTC Implementation:**
```javascript
// WebRTC Technology Specifications
const WEBRTC_CONFIG = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' }
    ],
    iceCandidatePoolSize: 10,
    bundlePolicy: 'balanced',
    rtcpMuxPolicy: 'require'
};

// Media Constraints
const MEDIA_CONSTRAINTS = {
    video: {
        width: { min: 640, ideal: 1280, max: 1920 },
        height: { min: 480, ideal: 720, max: 1080 },
        frameRate: { min: 15, ideal: 30, max: 60 },
        facingMode: 'user'
    },
    audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,
        channelCount: 2
    }
};

// WebRTC Implementation Class
class PeerLearnWebRTC {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.peerConnection = new RTCPeerConnection(WEBRTC_CONFIG);
        this.localStream = null;
        this.remoteStream = null;
        this.dataChannel = null;
        this.setupEventHandlers();
    }
    
    async initializeMedia() {
        try {
            this.localStream = await navigator.mediaDevices
                .getUserMedia(MEDIA_CONSTRAINTS);
            this.addStreamToPeerConnection();
        } catch (error) {
            console.error('Failed to get user media:', error);
            throw error;
        }
    }
}
```

**WebSocket Implementation:**
```python
# Django Channels WebSocket Consumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'session_{self.session_id}'
        
        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        # Handle different message types
        if message_type == 'webrtc_offer':
            await self.handle_webrtc_offer(data)
        elif message_type == 'webrtc_answer':
            await self.handle_webrtc_answer(data)
        elif message_type == 'ice_candidate':
            await self.handle_ice_candidate(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
```

## 10.4 Development and Deployment Tools

### 10.4.1 Version Control and Collaboration

**Git Configuration:**
```bash
# Git Configuration for Team Development
git config --global user.name "Developer Name"
git config --global user.email "developer@peerlearn.com"
git config --global init.defaultBranch main
git config --global pull.rebase false

# Branching Strategy
# main - Production ready code
# develop - Development integration branch
# feature/* - Feature development branches
# hotfix/* - Production hotfix branches
# release/* - Release preparation branches
```

**GitHub/GitLab Workflow:**
```yaml
# .github/workflows/ci-cd.yml
name: PeerLearn CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
        python -m pytest
    
    - name: Run security checks
      run: |
        bandit -r .
        safety check
```

### 10.4.2 Containerization and Deployment

**Docker Configuration:**
```dockerfile
# Dockerfile for PeerLearn Application
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE peerlearn.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "peerlearn.asgi:application"]
```

**Docker Compose for Development:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/peerlearn
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=peerlearn
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 10.4.3 Monitoring and Logging

**Application Monitoring:**
```python
# Sentry Configuration for Error Tracking
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.channels import ChannelsIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
            signals_spans=True,
        ),
        ChannelsIntegration(transaction_style='url'),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment=os.getenv('ENVIRONMENT', 'development'),
)
```

**Logging Configuration:**
```python
# Django Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/peerlearn/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'peerlearn': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

# 11. SYSTEM DESIGN

## 11.1 Architectural Design

### 11.1.1 Overall System Architecture

PeerLearn follows a modern, scalable architecture pattern combining the best practices of monolithic and microservices approaches. The system is designed with clear separation of concerns, high cohesion, and loose coupling.

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Web App   │  │   Mobile    │  │    Admin    │             │
│  │ Alpine.js + │  │   Browser   │  │  Dashboard  │             │
│  │ Tailwind    │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    PRESENTATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   WebRTC    │  │  WebSocket  │  │    HTTP     │             │
│  │  P2P Video  │  │ Real-time   │  │   REST API  │             │
│  │             │  │ Messages    │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Django   │  │   Django    │  │    ML/AI    │             │
│  │   Web App   │  │  Channels   │  │  Services   │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                     BUSINESS LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    User     │  │   Session   │  │   Payment   │             │
│  │ Management  │  │ Management  │  │ Processing  │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                      DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ PostgreSQL  │  │    Redis    │  │    File     │             │
│  │  Database   │  │   Cache     │  │   Storage   │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 11.1.2 Component Architecture

**Core Components Overview:**
```python
class SystemArchitecture:
    """
    PeerLearn System Architecture Components
    """
    
    CORE_COMPONENTS = {
        'user_management': {
            'registration': 'Enhanced multi-step registration',
            'authentication': 'JWT-based auth with role management',
            'profiles': 'Rich user profiles with skills',
            'verification': 'Identity and skill verification'
        },
        
        'session_management': {
            'creation': 'Advanced session creation with pricing',
            'booking': 'Secure booking with payment integration',
            'delivery': 'WebRTC-based video sessions',
            'recording': 'Optional session recording'
        },
        
        'communication': {
            'webrtc': 'Peer-to-peer video/audio',
            'websocket': 'Real-time messaging',
            'notifications': 'Multi-channel notifications',
            'chat': 'In-session text chat'
        },
        
        'payment_system': {
            'razorpay': 'INR payment processing',
            'gifts': 'In-session micro-payments',
            'earnings': 'Mentor earnings management',
            'analytics': 'Financial reporting'
        },
        
        'recommendation_engine': {
            'content_based': 'Skill-based matching',
            'collaborative': 'User behavior analysis',
            'popularity': 'Trending session identification',
            'ml_algorithms': 'Advanced ML recommendations'
        }
    }
```

### 11.1.3 Data Flow Architecture

**Request Processing Flow:**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│  Load       │───▶│   Django    │
│  Request    │    │ Balancer    │    │ Application │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Static CDN  │    │  SSL/TLS    │    │  Database   │
│   Assets    │    │Termination  │    │   Layer     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Cache     │    │ WebSocket   │    │    Redis    │
│   Layer     │    │  Channels   │    │   Storage   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 11.2 Database Design Architecture

### 11.2.1 Database Schema Design

**Entity Relationship Architecture:**
```sql
-- Core Database Schema Design
-- Users and Authentication
CREATE TABLE users_customuser (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('mentor', 'learner', 'admin')),
    profile_image VARCHAR(100),
    bio TEXT,
    skills TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Sessions
CREATE TABLE sessions_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID NOT NULL REFERENCES users_customuser(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    thumbnail VARCHAR(100),
    category VARCHAR(50),
    skills TEXT,
    price DECIMAL(8,2),
    schedule TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER NOT NULL,
    max_participants INTEGER DEFAULT 10,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bookings
CREATE TABLE sessions_booking (
    id SERIAL PRIMARY KEY,
    learner_id UUID NOT NULL REFERENCES users_customuser(id),
    session_id UUID NOT NULL REFERENCES sessions_session(id),
    status VARCHAR(20) DEFAULT 'pending',
    payment_id VARCHAR(100),
    amount_paid DECIMAL(8,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(learner_id, session_id)
);

-- Recommendations
CREATE TABLE recommendations_popularitymetric (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL REFERENCES sessions_session(id),
    view_count INTEGER DEFAULT 0,
    booking_count INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0.0,
    rating_average DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 11.2.2 Indexing Strategy

**Performance Optimization Indexes:**
```sql
-- Optimize user queries
CREATE INDEX idx_users_role ON users_customuser(role);
CREATE INDEX idx_users_email ON users_customuser(email);
CREATE INDEX idx_users_username ON users_customuser(username);
CREATE INDEX idx_users_created_at ON users_customuser(created_at);

-- Optimize session queries
CREATE INDEX idx_sessions_mentor ON sessions_session(mentor_id);
CREATE INDEX idx_sessions_status ON sessions_session(status);
CREATE INDEX idx_sessions_schedule ON sessions_session(schedule);
CREATE INDEX idx_sessions_category ON sessions_session(category);
CREATE INDEX idx_sessions_price ON sessions_session(price);

-- Optimize booking queries
CREATE INDEX idx_bookings_learner ON sessions_booking(learner_id);
CREATE INDEX idx_bookings_session ON sessions_booking(session_id);
CREATE INDEX idx_bookings_status ON sessions_booking(status);
CREATE INDEX idx_bookings_created_at ON sessions_booking(created_at);

-- Full-text search indexes
CREATE INDEX idx_sessions_title_search ON sessions_session 
    USING gin(to_tsvector('english', title));
CREATE INDEX idx_sessions_description_search ON sessions_session 
    USING gin(to_tsvector('english', description));
CREATE INDEX idx_users_skills_search ON users_customuser 
    USING gin(to_tsvector('english', skills));
```

### 11.2.3 Data Partitioning Strategy

**Horizontal Partitioning for Scale:**
```sql
-- Partition sessions by date for better performance
CREATE TABLE sessions_session_2024 PARTITION OF sessions_session
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE sessions_session_2025 PARTITION OF sessions_session
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Partition bookings by date
CREATE TABLE sessions_booking_2024 PARTITION OF sessions_booking
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE sessions_booking_2025 PARTITION OF sessions_booking
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

## 11.3 API Design Architecture

### 11.3.1 RESTful API Design

**API Endpoint Structure:**
```python
class APIArchitecture:
    """
    PeerLearn API Design Patterns
    """
    
    API_ENDPOINTS = {
        'authentication': {
            'POST /api/auth/register/': 'User registration',
            'POST /api/auth/login/': 'User login',
            'POST /api/auth/logout/': 'User logout',
            'POST /api/auth/refresh/': 'Token refresh',
            'POST /api/auth/verify-email/': 'Email verification'
        },
        
        'user_management': {
            'GET /api/users/profile/': 'Get user profile',
            'PUT /api/users/profile/': 'Update user profile',
            'POST /api/users/upload-avatar/': 'Upload profile image',
            'GET /api/users/skills/': 'Get user skills',
            'PUT /api/users/skills/': 'Update user skills'
        },
        
        'session_management': {
            'GET /api/sessions/': 'List sessions with filters',
            'POST /api/sessions/': 'Create new session',
            'GET /api/sessions/{id}/': 'Get session details',
            'PUT /api/sessions/{id}/': 'Update session',
            'DELETE /api/sessions/{id}/': 'Delete session',
            'POST /api/sessions/{id}/book/': 'Book session'
        },
        
        'payment_processing': {
            'POST /api/payments/create-order/': 'Create payment order',
            'POST /api/payments/verify/': 'Verify payment',
            'GET /api/payments/history/': 'Payment history',
            'POST /api/payments/gift/': 'Send gift payment',
            'GET /api/payments/earnings/': 'Mentor earnings'
        },
        
        'recommendations': {
            'GET /api/recommendations/': 'Get personalized recommendations',
            'GET /api/recommendations/trending/': 'Get trending sessions',
            'POST /api/recommendations/feedback/': 'Recommendation feedback',
            'GET /api/recommendations/similar/': 'Similar sessions'
        }
    }
```

**API Response Format:**
```python
class APIResponseFormat:
    """
    Standardized API response format
    """
    
    SUCCESS_RESPONSE = {
        'success': True,
        'data': {},
        'message': 'Operation completed successfully',
        'timestamp': '2025-05-27T16:48:54Z',
        'request_id': 'req_123456789'
    }
    
    ERROR_RESPONSE = {
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid input data',
            'details': {
                'field': 'email',
                'error': 'Email already exists'
            }
        },
        'timestamp': '2025-05-27T16:48:54Z',
        'request_id': 'req_123456789'
    }
    
    PAGINATION_RESPONSE = {
        'success': True,
        'data': [],
        'pagination': {
            'page': 1,
            'per_page': 20,
            'total': 150,
            'pages': 8,
            'has_next': True,
            'has_prev': False
        }
    }
```

### 11.3.2 WebSocket Architecture

**Real-time Communication Design:**
```python
# WebSocket Consumer Architecture
class WebSocketArchitecture:
    """
    WebSocket communication patterns for real-time features
    """
    
    CONSUMER_TYPES = {
        'session_consumer': {
            'purpose': 'Handle video session communications',
            'events': [
                'webrtc_offer', 'webrtc_answer', 'ice_candidate',
                'chat_message', 'session_start', 'session_end',
                'user_join', 'user_leave', 'screen_share'
            ]
        },
        
        'notification_consumer': {
            'purpose': 'Handle real-time notifications',
            'events': [
                'booking_created', 'session_reminder',
                'payment_received', 'message_received',
                'status_update', 'system_notification'
            ]
        },
        
        'dashboard_consumer': {
            'purpose': 'Handle dashboard real-time updates',
            'events': [
                'earnings_update', 'new_booking',
                'session_analytics', 'user_activity',
                'system_metrics'
            ]
        }
    }

# WebSocket Message Format
WEBSOCKET_MESSAGE_FORMAT = {
    'type': 'message_type',
    'data': {},
    'timestamp': '2025-05-27T16:48:54Z',
    'sender_id': 'user_uuid',
    'session_id': 'session_uuid'
}
```

## 11.4 Security Architecture

### 11.4.1 Authentication and Authorization

**Security Layer Design:**
```python
class SecurityArchitecture:
    """
    Multi-layered security design for PeerLearn
    """
    
    AUTHENTICATION_LAYERS = {
        'layer_1_jwt': {
            'purpose': 'Stateless token-based authentication',
            'implementation': 'JSON Web Tokens (JWT)',
            'expiry': '24 hours for access, 30 days for refresh',
            'algorithm': 'HS256',
            'claims': ['user_id', 'role', 'permissions', 'issued_at']
        },
        
        'layer_2_session': {
            'purpose': 'Server-side session management',
            'implementation': 'Django sessions with Redis backend',
            'security': 'HttpOnly, Secure, SameSite cookies',
            'timeout': '24 hours inactivity timeout'
        },
        
        'layer_3_csrf': {
            'purpose': 'Cross-Site Request Forgery protection',
            'implementation': 'Django CSRF middleware',
            'token_rotation': 'Per-request token rotation',
            'validation': 'Header and form token validation'
        }
    }
    
    AUTHORIZATION_MODEL = {
        'role_based': {
            'roles': ['mentor', 'learner', 'admin'],
            'permissions': 'Role-specific permissions',
            'inheritance': 'Hierarchical permission model'
        },
        
        'resource_based': {
            'ownership': 'Resource ownership validation',
            'context': 'Contextual permission checking',
            'dynamic': 'Runtime permission evaluation'
        }
    }
```

### 11.4.2 Data Protection

**Encryption and Privacy Design:**
```python
class DataProtectionArchitecture:
    """
    Data protection and privacy implementation
    """
    
    ENCRYPTION_LAYERS = {
        'transport_layer': {
            'protocol': 'TLS 1.3',
            'cipher_suites': 'ECDHE-RSA-AES256-GCM-SHA384',
            'certificate': 'Let\'s Encrypt SSL certificate',
            'hsts': 'HTTP Strict Transport Security enabled'
        },
        
        'application_layer': {
            'passwords': 'bcrypt with salt rounds=12',
            'sensitive_data': 'AES-256-GCM encryption',
            'tokens': 'HMAC-SHA256 signing',
            'files': 'At-rest encryption for uploads'
        },
        
        'database_layer': {
            'connection': 'SSL/TLS encrypted connections',
            'storage': 'Transparent Data Encryption (TDE)',
            'backups': 'Encrypted backup storage',
            'logs': 'Sensitive data redaction'
        }
    }
    
    PRIVACY_FEATURES = {
        'data_minimization': 'Collect only necessary data',
        'consent_management': 'Granular consent controls',
        'data_retention': 'Automated data lifecycle management',
        'right_to_deletion': 'User data deletion capabilities',
        'anonymization': 'Personal data anonymization'
    }
```

### 11.4.3 Payment Security

**Financial Security Architecture:**
```python
class PaymentSecurityArchitecture:
    """
    Payment processing security implementation
    """
    
    RAZORPAY_SECURITY = {
        'pci_compliance': 'PCI DSS Level 1 certified',
        'webhook_verification': 'HMAC-SHA256 signature verification',
        'payment_verification': 'Dual verification system',
        'fraud_detection': 'Real-time fraud monitoring',
        'data_isolation': 'No card data storage on servers'
    }
    
    TRANSACTION_SECURITY = {
        'amount_validation': 'Server-side amount verification',
        'duplicate_prevention': 'Idempotency key usage',
        'timeout_handling': 'Payment timeout mechanisms',
        'refund_security': 'Secure refund processing',
        'audit_logging': 'Comprehensive transaction logs'
    }
```

## 11.5 Performance Architecture

### 11.5.1 Caching Strategy

**Multi-level Caching Design:**
```python
class CachingArchitecture:
    """
    Comprehensive caching strategy for optimal performance
    """
    
    CACHING_LAYERS = {
        'browser_cache': {
            'static_assets': 'CSS, JS, images cached for 1 year',
            'html_pages': 'No cache for dynamic content',
            'api_responses': 'Short-term cache for read-only data'
        },
        
        'cdn_cache': {
            'global_distribution': 'CloudFront edge locations',
            'static_content': 'All static assets cached globally',
            'dynamic_content': 'API responses cached by region',
            'invalidation': 'Automated cache invalidation'
        },
        
        'application_cache': {
            'redis_cache': 'Session data and temporary storage',
            'database_cache': 'Frequently accessed query results',
            'template_cache': 'Rendered template fragments',
            'view_cache': 'Complete view response caching'
        },
        
        'database_cache': {
            'query_cache': 'PostgreSQL query result caching',
            'connection_pool': 'Database connection pooling',
            'read_replicas': 'Read-only query distribution',
            'materialized_views': 'Pre-computed complex queries'
        }
    }
```

### 11.5.2 Scalability Architecture

**Horizontal Scaling Design:**
```python
class ScalabilityArchitecture:
    """
    Scalable architecture for growth handling
    """
    
    SCALING_STRATEGIES = {
        'application_scaling': {
            'load_balancing': 'Multiple Django instances',
            'auto_scaling': 'CPU and memory-based scaling',
            'health_checks': 'Application health monitoring',
            'rolling_deployments': 'Zero-downtime updates'
        },
        
        'database_scaling': {
            'read_replicas': 'Multiple read-only database instances',
            'connection_pooling': 'Efficient connection management',
            'query_optimization': 'Index optimization and query tuning',
            'partitioning': 'Table partitioning for large datasets'
        },
        
        'storage_scaling': {
            'cdn_integration': 'Global content delivery network',
            'object_storage': 'S3-compatible storage for files',
            'image_optimization': 'Automatic image compression',
            'lazy_loading': 'On-demand content loading'
        }
    }
```

# 12. INPUT DESIGN

## 12.1 User Interface Input Design

### 12.1.1 Registration Form Design

**Enhanced Multi-Step Registration:**
```html
<!-- Registration Wizard Step 1: Basic Information -->
<div class="registration-step" x-show="currentStep === 1">
    <div class="space-y-6">
        <!-- Username Input -->
        <div class="form-group">
            <label for="username" class="block text-sm font-medium text-gray-700">
                Username
            </label>
            <input 
                type="text" 
                id="username"
                x-model="formData.username"
                @input="validateUsername()"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Enter your username"
                required
            >
            <div x-show="usernameValidation.show" class="mt-2">
                <p x-text="usernameValidation.message" 
                   :class="usernameValidation.valid ? 'text-green-600' : 'text-red-600'">
                </p>
            </div>
        </div>

        <!-- Email Input with Real-time Validation -->
        <div class="form-group">
            <label for="email" class="block text-sm font-medium text-gray-700">
                Email Address
            </label>
            <input 
                type="email" 
                id="email"
                x-model="formData.email"
                @input="validateEmail()"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="Enter your email address"
                required
            >
            <div x-show="emailValidation.show" class="mt-2">
                <p x-text="emailValidation.message" 
                   :class="emailValidation.valid ? 'text-green-600' : 'text-red-600'">
                </p>
            </div>
        </div>

        <!-- Password Input with Strength Indicator -->
        <div class="form-group">
            <label for="password" class="block text-sm font-medium text-gray-700">
                Password
            </label>
            <div class="relative">
                <input 
                    :type="showPassword ? 'text' : 'password'"
                    id="password"
                    x-model="formData.password"
                    @input="checkPasswordStrength()"
                    class="mt-1 block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md"
                    placeholder="Create a strong password"
                    required
                >
                <button 
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                    <svg x-show="!showPassword" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg x-show="showPassword" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L6.757 6.757M9.878 9.878l4.242 4.242m0 0L8.1 8.1m5.778 5.778L8.1 8.1" />
                    </svg>
                </button>
            </div>
            
            <!-- Password Strength Indicator -->
            <div class="mt-2">
                <div class="flex space-x-1">
                    <div :class="passwordStrength >= 1 ? 'bg-red-500' : 'bg-gray-200'" class="h-2 w-1/4 rounded"></div>
                    <div :class="passwordStrength >= 2 ? 'bg-yellow-500' : 'bg-gray-200'" class="h-2 w-1/4 rounded"></div>
                    <div :class="passwordStrength >= 3 ? 'bg-blue-500' : 'bg-gray-200'" class="h-2 w-1/4 rounded"></div>
                    <div :class="passwordStrength >= 4 ? 'bg-green-500' : 'bg-gray-200'" class="h-2 w-1/4 rounded"></div>
                </div>
                <p class="text-sm text-gray-600 mt-1" x-text="passwordStrengthText"></p>
            </div>
        </div>
    </div>
</div>

<!-- Registration Wizard Step 2: Role and Skills -->
<div class="registration-step" x-show="currentStep === 2">
    <div class="space-y-6">
        <!-- Role Selection -->
        <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-3">
                I want to join as a:
            </label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label class="relative cursor-pointer">
                    <input type="radio" x-model="formData.role" value="mentor" class="sr-only">
                    <div :class="formData.role === 'mentor' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                         class="border-2 rounded-lg p-6 text-center transition-all duration-200">
                        <div class="text-4xl mb-4">👨‍🏫</div>
                        <h3 class="text-lg font-semibold text-gray-900">Mentor</h3>
                        <p class="text-gray-600 mt-2">Share your knowledge and earn money</p>
                    </div>
                </label>
                
                <label class="relative cursor-pointer">
                    <input type="radio" x-model="formData.role" value="learner" class="sr-only">
                    <div :class="formData.role === 'learner' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                         class="border-2 rounded-lg p-6 text-center transition-all duration-200">
                        <div class="text-4xl mb-4">👨‍🎓</div>
                        <h3 class="text-lg font-semibold text-gray-900">Learner</h3>
                        <p class="text-gray-600 mt-2">Learn new skills from experts</p>
                    </div>
                </label>
            </div>
        </div>

        <!-- Skill Selection with ML Suggestions -->
        <div class="form-group">
            <label for="skills" class="block text-sm font-medium text-gray-700">
                <span x-text="formData.role === 'mentor' ? 'Skills you can teach:' : 'Skills you want to learn:'"></span>
            </label>
            <div class="relative">
                <input 
                    type="text" 
                    id="skills"
                    x-model="skillInput"
                    @input="getSkillSuggestions()"
                    @keydown.enter.prevent="addSkill(skillInput)"
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Type a skill and press Enter"
                >
                
                <!-- Skill Suggestions Dropdown -->
                <div x-show="skillSuggestions.length > 0" class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
                    <template x-for="suggestion in skillSuggestions" :key="suggestion.id">
                        <div @click="addSkill(suggestion.name)" 
                             class="px-3 py-2 cursor-pointer hover:bg-blue-50 border-b border-gray-100 last:border-b-0">
                            <span x-text="suggestion.name" class="font-medium"></span>
                            <span x-text="'(' + suggestion.category + ')'" class="text-gray-500 text-sm ml-2"></span>
                        </div>
                    </template>
                </div>
            </div>
            
            <!-- Selected Skills -->
            <div x-show="selectedSkills.length > 0" class="mt-3">
                <div class="flex flex-wrap gap-2">
                    <template x-for="skill in selectedSkills" :key="skill">
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                            <span x-text="skill"></span>
                            <button @click="removeSkill(skill)" class="ml-2 text-blue-600 hover:text-blue-800">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                                </svg>
                            </button>
                        </span>
                    </template>
                </div>
            </div>
        </div>
    </div>
</div>
```

### 12.1.2 Session Creation Input Design

**Advanced Session Creation Form:**
```html
<!-- Session Creation Form -->
<div class="session-creation-form bg-white rounded-lg shadow-lg p-8">
    <div class="space-y-8">
        <!-- Session Basic Information -->
        <div class="section">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Session Details</h3>
            
            <!-- Session Title -->
            <div class="form-group">
                <label for="session-title" class="block text-sm font-medium text-gray-700">
                    Session Title *
                </label>
                <input 
                    type="text" 
                    id="session-title"
                    x-model="sessionData.title"
                    @input="updateSlug()"
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Advanced React Hooks for Beginners"
                    maxlength="200"
                    required
                >
                <div class="mt-1 flex justify-between">
                    <span class="text-sm text-gray-500">Make it descriptive and engaging</span>
                    <span class="text-sm text-gray-500" x-text="sessionData.title.length + '/200'"></span>
                </div>
            </div>

            <!-- Session Description -->
            <div class="form-group">
                <label for="session-description" class="block text-sm font-medium text-gray-700">
                    Description *
                </label>
                <textarea 
                    id="session-description"
                    x-model="sessionData.description"
                    rows="4"
                    class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Describe what students will learn, prerequisites, and what makes this session valuable..."
                    required
                ></textarea>
                <p class="mt-1 text-sm text-gray-500">Include learning objectives, prerequisites, and session structure</p>
            </div>

            <!-- Session Thumbnail Upload -->
            <div class="form-group">
                <label class="block text-sm font-medium text-gray-700">
                    Session Thumbnail
                </label>
                <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-blue-400 transition-colors duration-200">
                    <div class="space-y-1 text-center">
                        <template x-if="!sessionData.thumbnail">
                            <div>
                                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                                <div class="flex text-sm text-gray-600">
                                    <label for="thumbnail-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                                        <span>Upload a thumbnail</span>
                                        <input id="thumbnail-upload" name="thumbnail-upload" type="file" class="sr-only" @change="handleThumbnailUpload($event)">
                                    </label>
                                    <p class="pl-1">or drag and drop</p>
                                </div>
                                <p class="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                            </div>
                        </template>
                        
                        <template x-if="sessionData.thumbnail">
                            <div class="relative">
                                <img :src="sessionData.thumbnailPreview" class="mx-auto h-32 w-48 object-cover rounded-lg">
                                <button @click="removeThumbnail()" class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600">
                                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                                    </svg>
                                </button>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>

        <!-- Session Pricing and Type -->
        <div class="section">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Session Type & Pricing</h3>
            
            <!-- Session Type Selection -->
            <div class="form-group">
                <label class="block text-sm font-medium text-gray-700 mb-3">
                    Session Type
                </label>
                <div class="space-y-3">
                    <label class="flex items-center">
                        <input type="radio" x-model="sessionData.type" value="free" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300">
                        <span class="ml-3 text-sm text-gray-700">
                            <span class="font-medium">Free Session</span>
                            <span class="text-gray-500 block">Great for building your reputation and attracting students</span>
                        </span>
                    </label>
                    
                    <label class="flex items-center">
                        <input type="radio" x-model="sessionData.type" value="paid" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300">
                        <span class="ml-3 text-sm text-gray-700">
                            <span class="font-medium">Paid Session</span>
                            <span class="text-gray-500 block">Set your price and earn from your expertise</span>
                        </span>
                    </label>
                </div>
            </div>

            <!-- Session Price (shown only for paid sessions) -->
            <div x-show="sessionData.type === 'paid'" class="form-group">
                <label for="session-price" class="block text-sm font-medium text-gray-700">
                    Session Price (₹ INR) *
                </label>
                <div class="mt-1 relative rounded-md shadow-sm">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">₹</span>
                    </div>
                    <input 
                        type="number" 
                        id="session-price"
                        x-model="sessionData.price"
                        class="block w-full pl-7 pr-12 border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        placeholder="500"
                        min="50"
                        max="10000"
                        step="50"
                    >
                    <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <span class="text-gray-500 sm:text-sm">INR</span>
                    </div>
                </div>
                <div class="mt-2 flex justify-between">
                    <span class="text-sm text-gray-500">Suggested: ₹199-₹999 per session</span>
                    <span x-show="sessionData.price" class="text-sm text-gray-500">
                        You'll earn: ₹<span x-text="Math.round(sessionData.price * 0.85)"></span> (after 15% platform fee)
                    </span>
                </div>
            </div>
        </div>

        <!-- Session Scheduling -->
        <div class="section">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Schedule & Duration</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Date Selection -->
                <div class="form-group">
                    <label for="session-date" class="block text-sm font-medium text-gray-700">
                        Session Date *
                    </label>
                    <input 
                        type="date" 
                        id="session-date"
                        x-model="sessionData.date"
                        :min="new Date().toISOString().split('T')[0]"
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        required
                    >
                </div>

                <!-- Time Selection -->
                <div class="form-group">
                    <label for="session-time" class="block text-sm font-medium text-gray-700">
                        Session Time *
                    </label>
                    <input 
                        type="time" 
                        id="session-time"
                        x-model="sessionData.time"
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        required
                    >
                </div>

                <!-- Duration Selection -->
                <div class="form-group">
                    <label for="session-duration" class="block text-sm font-medium text-gray-700">
                        Duration *
                    </label>
                    <select 
                        id="session-duration"
                        x-model="sessionData.duration"
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        required
                    >
                        <option value="">Select duration</option>
                        <option value="30">30 minutes</option>
                        <option value="45">45 minutes</option>
                        <option value="60">1 hour</option>
                        <option value="90">1.5 hours</option>
                        <option value="120">2 hours</option>
                        <option value="180">3 hours</option>
                    </select>
                </div>

                <!-- Max Participants -->
                <div class="form-group">
                    <label for="max-participants" class="block text-sm font-medium text-gray-700">
                        Maximum Participants
                    </label>
                    <select 
                        id="max-participants"
                        x-model="sessionData.maxParticipants"
                        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="1">1-on-1 Session</option>
                        <option value="5">Up to 5 participants</option>
                        <option value="10">Up to 10 participants</option>
                        <option value="20">Up to 20 participants</option>
                        <option value="50">Up to 50 participants</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
</div>
```

## 12.2 Payment Input Design

### 12.2.1 Razorpay Payment Interface

**Secure Payment Input Form:**
```html
<!-- Payment Processing Interface -->
<div class="payment-interface bg-white rounded-lg shadow-lg p-8">
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900">Complete Your Payment</h2>
        <p class="text-gray-600 mt-2">Secure payment powered by Razorpay</p>
    </div>

    <!-- Session Summary -->
    <div class="session-summary bg-gray-50 rounded-lg p-6 mb-6">
        <div class="flex items-start space-x-4">
            <img :src="session.thumbnail || '/static/images/default-session.jpg'" 
                 class="w-20 h-20 object-cover rounded-lg">
            <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900" x-text="session.title"></h3>
                <p class="text-gray-600" x-text="session.mentor_name"></p>
                <div class="flex items-center mt-2 text-sm text-gray-500">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    <span x-text="formatDate(session.schedule)"></span>
                    <span class="mx-2">•</span>
                    <span x-text="session.duration + ' minutes'"></span>
                </div>
            </div>
            <div class="text-right">
                <div class="text-2xl font-bold text-gray-900">₹<span x-text="session.price"></span></div>
                <div class="text-sm text-gray-500">INR</div>
            </div>
        </div>
    </div>

    <!-- Payment Method Selection -->
    <div class="payment-methods mb-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Select Payment Method</h3>
        
        <div class="space-y-3">
            <!-- UPI Payment -->
            <label class="payment-method-option">
                <input type="radio" x-model="paymentMethod" value="upi" class="sr-only">
                <div :class="paymentMethod === 'upi' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                     class="border-2 rounded-lg p-4 cursor-pointer transition-all duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <img src="/static/images/upi-logo.png" alt="UPI" class="w-8 h-8 mr-3">
                            <div>
                                <div class="font-medium text-gray-900">UPI</div>
                                <div class="text-sm text-gray-500">Pay using any UPI app</div>
                            </div>
                        </div>
                        <div class="text-green-600 font-medium">Instant</div>
                    </div>
                </div>
            </label>

            <!-- Credit/Debit Card -->
            <label class="payment-method-option">
                <input type="radio" x-model="paymentMethod" value="card" class="sr-only">
                <div :class="paymentMethod === 'card' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                     class="border-2 rounded-lg p-4 cursor-pointer transition-all duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="flex space-x-1 mr-3">
                                <img src="/static/images/visa-logo.png" alt="Visa" class="w-6 h-4">
                                <img src="/static/images/mastercard-logo.png" alt="Mastercard" class="w-6 h-4">
                                <img src="/static/images/rupay-logo.png" alt="RuPay" class="w-6 h-4">
                            </div>
                            <div>
                                <div class="font-medium text-gray-900">Credit/Debit Card</div>
                                <div class="text-sm text-gray-500">Visa, Mastercard, RuPay</div>
                            </div>
                        </div>
                        <div class="text-blue-600 font-medium">Secure</div>
                    </div>
                </div>
            </label>

            <!-- Net Banking -->
            <label class="payment-method-option">
                <input type="radio" x-model="paymentMethod" value="netbanking" class="sr-only">
                <div :class="paymentMethod === 'netbanking' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                     class="border-2 rounded-lg p-4 cursor-pointer transition-all duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <svg class="w-8 h-8 mr-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                            </svg>
                            <div>
                                <div class="font-medium text-gray-900">Net Banking</div>
                                <div class="text-sm text-gray-500">All major banks supported</div>
                            </div>
                        </div>
                        <div class="text-gray-600 font-medium">Reliable</div>
                    </div>
                </div>
            </label>

            <!-- Wallet -->
            <label class="payment-method-option">
                <input type="radio" x-model="paymentMethod" value="wallet" class="sr-only">
                <div :class="paymentMethod === 'wallet' ? 'border-blue-500 bg-blue-50' : 'border-gray-300'" 
                     class="border-2 rounded-lg p-4 cursor-pointer transition-all duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="flex space-x-1 mr-3">
                                <img src="/static/images/paytm-logo.png" alt="Paytm" class="w-6 h-6">
                                <img src="/static/images/phonepe-logo.png" alt="PhonePe" class="w-6 h-6">
                                <img src="/static/images/googlepay-logo.png" alt="Google Pay" class="w-6 h-6">
                            </div>
                            <div>
                                <div class="font-medium text-gray-900">Wallet</div>
                                <div class="text-sm text-gray-500">Paytm, PhonePe, Google Pay</div>
                            </div>
                        </div>
                        <div class="text-purple-600 font-medium">Quick</div>
                    </div>
                </div>
            </label>
        </div>
    </div>

    <!-- Payment Summary -->
    <div class="payment-summary bg-gray-50 rounded-lg p-4 mb-6">
        <div class="space-y-2">
            <div class="flex justify-between">
                <span class="text-gray-600">Session Price</span>
                <span class="text-gray-900">₹<span x-text="session.price"></span></span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Platform Fee</span>
                <span class="text-gray-900">₹0</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-600">Payment Gateway Fee</span>
                <span class="text-gray-900">₹<span x-text="calculateGatewayFee(session.price)"></span></span>
            </div>
            <hr class="my-2">
            <div class="flex justify-between text-lg font-semibold">
                <span class="text-gray-900">Total Amount</span>
                <span class="text-gray-900">₹<span x-text="calculateTotal(session.price)"></span></span>
            </div>
        </div>
    </div>

    <!-- Security Information -->
    <div class="security-info bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div class="flex items-start">
            <svg class="w-5 h-5 text-green-600 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
            <div>
                <h4 class="text-sm font-medium text-green-800">Your payment is secure</h4>
                <p class="text-sm text-green-700 mt-1">
                    256-bit SSL encryption and PCI DSS compliant. We never store your card details.
                </p>
            </div>
        </div>
    </div>

    <!-- Payment Action Button -->
    <button 
        @click="processPayment()"
        :disabled="!paymentMethod || isProcessing"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
    >
        <template x-if="!isProcessing">
            <span>Pay ₹<span x-text="calculateTotal(session.price)"></span> Securely</span>
        </template>
        <template x-if="isProcessing">
            <span class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing Payment...
            </span>
        </template>
    </button>

    <!-- Terms and Conditions -->
    <p class="text-center text-sm text-gray-500 mt-4">
        By proceeding, you agree to our 
        <a href="/terms" class="text-blue-600 hover:text-blue-800">Terms of Service</a> 
        and 
        <a href="/privacy" class="text-blue-600 hover:text-blue-800">Privacy Policy</a>
    </p>
</div>
```

## 12.3 Search and Filter Input Design

### 12.3.1 Advanced Search Interface

**Intelligent Search with Filters:**
```html
<!-- Advanced Search Interface -->
<div class="search-interface bg-white rounded-lg shadow-lg p-6">
    <!-- Main Search Bar -->
    <div class="relative mb-6">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
        </div>
        <input 
            type="text" 
            x-model="searchQuery"
            @input="performSearch()"
            @keydown.enter="performSearch()"
            class="block w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-lg"
            placeholder="Search for sessions, skills, or mentors..."
        >
        
        <!-- Search Suggestions -->
        <div x-show="searchSuggestions.length > 0" class="absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
            <div class="py-2">
                <template x-for="suggestion in searchSuggestions" :key="suggestion.id">
                    <div @click="selectSuggestion(suggestion)" 
                         class="px-4 py-2 cursor-pointer hover:bg-gray-50 flex items-center">
                        <svg class="w-4 h-4 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                        <span x-text="suggestion.title" class="font-medium"></span>
                        <span x-text="'in ' + suggestion.category" class="text-gray-500 text-sm ml-2"></span>
                    </div>
                </template>
            </div>
        </div>
    </div>

    <!-- Filter Options -->
    <div class="filters-section">
        <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
            <button @click="clearAllFilters()" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                Clear All
            </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Category Filter -->
            <div class="filter-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select x-model="filters.category" @change="applyFilters()" 
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    <option value="">All Categories</option>
                    <option value="programming">Programming & Development</option>
                    <option value="data-science">Data Science & Analytics</option>
                    <option value="web-development">Web Development</option>
                    <option value="mobile-development">Mobile Development</option>
                    <option value="ai-ml">AI & Machine Learning</option>
                    <option value="design">UI/UX Design</option>
                    <option value="business">Business & Marketing</option>
                    <option value="language">Language Learning</option>
                    <option value="music">Music & Arts</option>
                    <option value="fitness">Health & Fitness</option>
                </select>
            </div>

            <!-- Price Range Filter -->
            <div class="filter-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
                <select x-model="filters.priceRange" @change="applyFilters()" 
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    <option value="">Any Price</option>
                    <option value="free">Free Sessions</option>
                    <option value="0-500">Under ₹500</option>
                    <option value="500-1000">₹500 - ₹1000</option>
                    <option value="1000-2000">₹1000 - ₹2000</option>
                    <option value="2000+">Above ₹2000</option>
                </select>
            </div>

            <!-- Duration Filter -->
            <div class="filter-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                <select x-model="filters.duration" @change="applyFilters()" 
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    <option value="">Any Duration</option>
                    <option value="30">30 minutes</option>
                    <option value="60">1 hour</option>
                    <option value="120">2 hours</option>
                    <option value="180+">3+ hours</option>
                </select>
            </div>

            <!-- Schedule Filter -->
            <div class="filter-group">
                <label class="block text-sm font-medium text-gray-700 mb-2">When</label>
                <select x-model="filters.schedule" @change="applyFilters()" 
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    <option value="">Anytime</option>
                    <option value="today">Today</option>
                    <option value="tomorrow">Tomorrow</option>
                    <option value="this-week">This Week</option>
                    <option value="next-week">Next Week</option>
                    <option value="this-month">This Month</option>
                </select>
            </div>
        </div>

        <!-- Advanced Filters Toggle -->
        <div class="mt-6">
            <button @click="showAdvancedFilters = !showAdvancedFilters" 
                    class="text-blue-600 hover:text-blue-800 font-medium flex items-center">
                <span x-text="showAdvancedFilters ? 'Hide' : 'Show'"></span>
                <span class="ml-1">Advanced Filters</span>
                <svg :class="showAdvancedFilters ? 'rotate-180' : ''" 
                     class="w-4 h-4 ml-1 transform transition-transform duration-200" 
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
            </button>
        </div>

        <!-- Advanced Filters Section -->
        <div x-show="showAdvancedFilters" x-transition class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Rating Filter -->
                <div class="filter-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Rating</label>
                    <select x-model="filters.rating" @change="applyFilters()" 
                            class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                        <option value="">Any Rating</option>
                        <option value="4.5">4.5+ Stars</option>
                        <option value="4.0">4.0+ Stars</option>
                        <option value="3.5">3.5+ Stars</option>
                        <option value="3.0">3.0+ Stars</option>
                    </select>
                </div>

                <!-- Language Filter -->
                <div class="filter-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Language</label>
                    <select x-model="filters.language" @change="applyFilters()" 
                            class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                        <option value="">Any Language</option>
                        <option value="english">English</option>
                        <option value="hindi">Hindi</option>
                        <option value="tamil">Tamil</option>
                        <option value="telugu">Telugu</option>
                        <option value="bengali">Bengali</option>
                        <option value="marathi">Marathi</option>
                    </select>
                </div>

                <!-- Session Type Filter -->
                <div class="filter-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Session Type</label>
                    <select x-model="filters.sessionType" @change="applyFilters()" 
                            class="block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                        <option value="">Any Type</option>
                        <option value="1-on-1">1-on-1 Sessions</option>
                        <option value="group">Group Sessions</option>
                        <option value="workshop">Workshops</option>
                        <option value="masterclass">Masterclasses</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Active Filters Display -->
        <div x-show="activeFilters.length > 0" class="mt-4">
            <div class="flex flex-wrap gap-2">
                <span class="text-sm font-medium text-gray-700 mr-2">Active filters:</span>
                <template x-for="filter in activeFilters" :key="filter.key">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                        <span x-text="filter.label"></span>
                        <button @click="removeFilter(filter.key)" class="ml-2 text-blue-600 hover:text-blue-800">
                            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </span>
                </template>
            </div>
        </div>
    </div>

    <!-- Sort Options -->
    <div class="sort-section mt-6 pt-6 border-t border-gray-200">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <span class="text-sm font-medium text-gray-700">Sort by:</span>
                <select x-model="sortBy" @change="applySorting()" 
                        class="px-3 py-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                    <option value="relevance">Relevance</option>
                    <option value="price-low">Price: Low to High</option>
                    <option value="price-high">Price: High to Low</option>
                    <option value="rating">Highest Rated</option>
                    <option value="popularity">Most Popular</option>
                    <option value="newest">Newest First</option>
                    <option value="date">Soonest First</option>
                </select>
            </div>
            
            <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-500" x-text="searchResults.length + ' sessions found'"></span>
                
                <!-- View Toggle -->
                <div class="flex items-center border border-gray-300 rounded-md">
                    <button @click="viewMode = 'grid'" 
                            :class="viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600'"
                            class="p-2 rounded-l-md">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                        </svg>
                    </button>
                    <button @click="viewMode = 'list'" 
                            :class="viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600'"
                            class="p-2 rounded-r-md">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```

# 13. OUTPUT DESIGN

## 13.1 Dashboard Output Design

### 13.1.1 Mentor Dashboard Layout

**Comprehensive Mentor Analytics Display:**
```html
<!-- Mentor Dashboard Output Design -->
<div class="mentor-dashboard-layout">
    <!-- Dashboard Header -->
    <div class="dashboard-header bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 rounded-lg mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold">Welcome back, {{ mentor_name }}!</h1>
                <p class="text-blue-100 mt-2">Here's how your mentoring journey is going</p>
            </div>
            <div class="text-right">
                <div class="text-2xl font-bold">₹{{ total_earnings|floatformat:0 }}</div>
                <div class="text-blue-100">Total Earnings</div>
            </div>
        </div>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Total Sessions Card -->
        <div class="metric-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Total Sessions</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ session_stats.total }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                                <svg class="self-center flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                                </svg>
                                <span class="sr-only">Increased by</span>
                                +{{ session_stats.growth_percent }}%
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Active Students Card -->
        <div class="metric-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Active Students</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ student_stats.active }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-semibold text-blue-600">
                                +{{ student_stats.new_this_month }} this month
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Average Rating Card -->
        <div class="metric-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Average Rating</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ rating_stats.average|floatformat:1 }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-medium text-gray-500">
                                / 5.0 ({{ rating_stats.total_reviews }} reviews)
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Monthly Revenue Card -->
        <div class="metric-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">This Month</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">₹{{ earnings_stats.this_month|floatformat:0 }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                                +{{ earnings_stats.growth_percent|floatformat:1 }}%
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts and Analytics Section -->
    <div class="analytics-section grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Earnings Chart -->
        <div class="chart-container bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Earnings Trend</h3>
                <select class="text-sm border border-gray-300 rounded-md px-3 py-1">
                    <option value="6months">Last 6 months</option>
                    <option value="1year">Last year</option>
                    <option value="all">All time</option>
                </select>
            </div>
            <div class="chart-area h-64">
                <canvas id="earningsChart" class="w-full h-full"></canvas>
            </div>
        </div>

        <!-- Session Performance Chart -->
        <div class="chart-container bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Session Performance</h3>
                <div class="flex space-x-2">
                    <button class="text-sm bg-blue-100 text-blue-600 px-3 py-1 rounded-md">Completed</button>
                    <button class="text-sm text-gray-600 px-3 py-1 rounded-md hover:bg-gray-100">Cancelled</button>
                </div>
            </div>
            <div class="chart-area h-64">
                <canvas id="sessionChart" class="w-full h-full"></canvas>
            </div>
        </div>
    </div>

    <!-- Recent Activities and Upcoming Sessions -->
    <div class="activities-section grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Recent Bookings -->
        <div class="recent-bookings bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Recent Bookings</h3>
                <a href="/mentor/bookings/" class="text-blue-600 hover:text-blue-800 text-sm font-medium">View All</a>
            </div>
            
            <div class="space-y-4">
                {% for booking in recent_bookings %}
                <div class="booking-item flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <img src="{{ booking.learner.profile_image.url }}" 
                             alt="{{ booking.learner.get_full_name }}"
                             class="w-10 h-10 rounded-full object-cover">
                        <div>
                            <div class="font-medium text-gray-900">{{ booking.learner.get_full_name }}</div>
                            <div class="text-sm text-gray-500">{{ booking.session.title|truncatechars:30 }}</div>
                            <div class="text-xs text-gray-400">{{ booking.created_at|timesince }} ago</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="font-medium text-gray-900">₹{{ booking.amount_paid|floatformat:0 }}</div>
                        <div class="text-sm text-green-600">{{ booking.status|capfirst }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Upcoming Sessions -->
        <div class="upcoming-sessions bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Upcoming Sessions</h3>
                <a href="/mentor/sessions/" class="text-blue-600 hover:text-blue-800 text-sm font-medium">View All</a>
            </div>
            
            <div class="space-y-4">
                {% for session in upcoming_sessions %}
                <div class="session-item flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                        </div>
                        <div>
                            <div class="font-medium text-gray-900">{{ session.title|truncatechars:25 }}</div>
                            <div class="text-sm text-gray-500">{{ session.schedule|date:"M d, Y" }} at {{ session.schedule|time:"g:i A" }}</div>
                            <div class="text-xs text-gray-400">{{ session.current_participants }} / {{ session.max_participants }} participants</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="font-medium text-gray-900">₹{{ session.price|floatformat:0 }}</div>
                        <div class="text-sm text-blue-600">{{ session.duration }} min</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
```

### 13.1.2 Learner Dashboard Layout

**Personalized Learning Progress Display:**
```html
<!-- Learner Dashboard Output Design -->
<div class="learner-dashboard-layout">
    <!-- Dashboard Header -->
    <div class="dashboard-header bg-gradient-to-r from-green-600 to-green-800 text-white p-8 rounded-lg mb-8">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-3xl font-bold">Keep Learning, {{ learner_name }}!</h1>
                <p class="text-green-100 mt-2">Continue your journey to mastery</p>
            </div>
            <div class="text-right">
                <div class="text-2xl font-bold">{{ learning_stats.total_sessions }}</div>
                <div class="text-green-100">Sessions Completed</div>
            </div>
        </div>
    </div>

    <!-- Learning Progress Cards -->
    <div class="progress-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Current Streak Card -->
        <div class="progress-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Learning Streak</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ learning_stats.current_streak }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-medium text-orange-600">
                                days
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Skills Learned Card -->
        <div class="progress-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Skills Learned</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ learning_stats.skills_count }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-semibold text-blue-600">
                                +{{ learning_stats.new_skills_this_month }} this month
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Hours Learned Card -->
        <div class="progress-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Total Hours</dt>
                        <dd class="flex items-baseline">
                            <div class="text-2xl font-semibold text-gray-900">{{ learning_stats.total_hours }}</div>
                            <div class="ml-2 flex items-baseline text-sm font-medium text-purple-600">
                                hours
                            </div>
                        </dd>
                    </dl>
                </div>
            </div>
        </div>

        <!-- Next Goal Card -->
        <div class="progress-card bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
                        </svg>
                    </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                    <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">Next Goal</dt>
                        <dd class="flex items-baseline">
                            <div class="text-sm font-semibold text-gray-900">{{ learning_stats.next_goal_progress }}%</div>
                            <div class="ml-2 flex items-baseline text-xs font-medium text-green-600">
                                {{ learning_stats.next_goal_title|truncatechars:15 }}
                            </div>
                        </dd>
                        <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-green-500 h-2 rounded-full" style="width: {{ learning_stats.next_goal_progress }}%"></div>
                        </div>
                    </dl>
                </div>
            </div>
        </div>
    </div>

    <!-- Personalized Recommendations Section -->
    <div class="recommendations-section mb-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-xl font-bold text-gray-900">Recommended For You</h3>
                <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">Refresh Recommendations</button>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {% for session in recommended_sessions %}
                <div class="recommendation-card bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                    <div class="flex items-start space-x-3">
                        <img src="{{ session.thumbnail.url }}" 
                             alt="{{ session.title }}"
                             class="w-16 h-16 object-cover rounded-lg">
                        <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-semibold text-gray-900 truncate">{{ session.title }}</h4>
                            <p class="text-sm text-gray-600 mt-1">{{ session.mentor.get_full_name }}</p>
                            <div class="flex items-center mt-2 text-xs text-gray-500">
                                <span class="flex items-center">
                                    <svg class="w-3 h-3 mr-1 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                                    </svg>
                                    {{ session.average_rating|floatformat:1 }}
                                </span>
                                <span class="mx-2">•</span>
                                <span>{{ session.duration }} min</span>
                            </div>
                            <div class="flex items-center justify-between mt-3">
                                <span class="text-lg font-bold text-gray-900">
                                    {% if session.price %}₹{{ session.price|floatformat:0 }}{% else %}Free{% endif %}
                                </span>
                                <button class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium px-3 py-1 rounded-md">
                                    View Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- Learning Path and Progress -->
    <div class="learning-path-section grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Current Learning Path -->
        <div class="learning-path bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Learning Path</h3>
            
            <div class="space-y-4">
                {% for path_item in learning_path %}
                <div class="path-item flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        {% if path_item.completed %}
                        <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        {% elif path_item.current %}
                        <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                        {% else %}
                        <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                            <span class="text-gray-600 text-sm font-medium">{{ forloop.counter }}</span>
                        </div>
                        {% endif %}
                    </div>
                    <div class="flex-1">
                        <h4 class="text-sm font-semibold text-gray-900">{{ path_item.title }}</h4>
                        <p class="text-sm text-gray-600">{{ path_item.description }}</p>
                        {% if path_item.current %}
                        <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-blue-500 h-2 rounded-full" style="width: {{ path_item.progress }}%"></div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">{{ path_item.progress }}% complete</p>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity bg-white rounded-lg shadow-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            
            <div class="space-y-4">
                {% for activity in recent_activities %}
                <div class="activity-item flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        {% if activity.type == 'session_completed' %}
                        <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                            <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        {% elif activity.type == 'session_booked' %}
                        <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                        </div>
                        {% elif activity.type == 'skill_earned' %}
                        <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                            <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        {% endif %}
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm text-gray-900">{{ activity.description }}</p>
                        <p class="text-xs text-gray-500 mt-1">{{ activity.created_at|timesince }} ago</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
```

## 13.2 Session Output Design

### 13.2.1 WebRTC Video Interface

**Real-time Video Session Layout:**
```html
<!-- WebRTC Session Interface -->
<div class="webrtc-session-container h-screen bg-gray-900 flex flex-col">
    <!-- Session Header -->
    <div class="session-header bg-gray-800 text-white p-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
            <h1 class="text-lg font-semibold">{{ session.title }}</h1>
            <span class="bg-red-500 text-white px-2 py-1 rounded text-sm font-medium">LIVE</span>
            <div class="flex items-center text-gray-300">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span id="session-timer">00:00:00</span>
            </div>
        </div>
        
        <div class="flex items-center space-x-4">
            <!-- Participants Count -->
            <div class="flex items-center text-gray-300">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
                <span id="participants-count">{{ session.current_participants }}</span>
            </div>
            
            <!-- Session Status -->
            <div class="text-gray-300 text-sm">
                <span id="connection-status">Connected</span>
                <div id="connection-indicator" class="inline-block w-2 h-2 bg-green-500 rounded-full ml-1"></div>
            </div>
        </div>
    </div>

    <!-- Main Video Area -->
    <div class="video-container flex-1 flex">
        <!-- Primary Video Area -->
        <div class="primary-video-area flex-1 relative">
            <!-- Main Video Stream -->
            <video id="remoteVideo" 
                   class="w-full h-full object-cover bg-gray-800"
                   autoplay 
                   playsinline>
            </video>
            
            <!-- Video Controls Overlay -->
            <div class="video-controls absolute bottom-4 left-1/2 transform -translate-x-1/2">
                <div class="flex items-center space-x-4 bg-black bg-opacity-50 rounded-lg px-6 py-3">
                    <!-- Microphone Toggle -->
                    <button id="micToggle" 
                            class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                            onclick="toggleMicrophone()">
                        <svg id="micOnIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        </svg>
                        <svg id="micOffIcon" class="w-5 h-5 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 5.586l12.828 12.828M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        </svg>
                    </button>

                    <!-- Camera Toggle -->
                    <button id="cameraToggle" 
                            class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                            onclick="toggleCamera()">
                        <svg id="cameraOnIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                        </svg>
                        <svg id="cameraOffIcon" class="w-5 h-5 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364L18.364 5.636"></path>
                        </svg>
                    </button>

                    <!-- Screen Share -->
                    <button id="screenShareToggle" 
                            class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                            onclick="toggleScreenShare()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </button>

                    <!-- Chat Toggle -->
                    <button id="chatToggle" 
                            class="p-3 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                            onclick="toggleChat()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                        </svg>
                    </button>

                    <!-- End Session -->
                    <button id="endSession" 
                            class="p-3 rounded-full bg-red-600 hover:bg-red-700 text-white transition-colors"
                            onclick="endSession()">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 16l5-5m0 0l5 5M8 11V7a4 4 0 118 0v4m-4 4h.01"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Local Video (Picture-in-Picture) -->
            <div class="local-video absolute top-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-600">
                <video id="localVideo" 
                       class="w-full h-full object-cover"
                       autoplay 
                       playsinline 
                       muted>
                </video>
                <div class="absolute bottom-2 left-2 text-white text-xs bg-black bg-opacity-50 px-2 py-1 rounded">
                    You
                </div>
            </div>

            <!-- Screen Share Indicator -->
            <div id="screenShareIndicator" 
                 class="absolute top-4 left-4 bg-blue-600 text-white px-3 py-1 rounded-lg text-sm font-medium hidden">
                <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                Screen Sharing
            </div>
        </div>

        <!-- Chat Sidebar -->
        <div id="chatSidebar" class="chat-sidebar w-80 bg-white border-l border-gray-300 flex flex-col hidden">
            <!-- Chat Header -->
            <div class="chat-header bg-gray-50 p-4 border-b border-gray-200">
                <div class="flex items-center justify-between">
                    <h3 class="font-semibold text-gray-900">Session Chat</h3>
                    <button onclick="toggleChat()" class="text-gray-500 hover:text-gray-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Chat Messages -->
            <div id="chatMessages" class="chat-messages flex-1 overflow-y-auto p-4 space-y-4">
                <!-- System Message -->
                <div class="system-message text-center">
                    <p class="text-sm text-gray-500 bg-gray-100 rounded-lg px-3 py-2 inline-block">
                        Session started. Welcome to {{ session.title }}!
                    </p>
                </div>

                <!-- Chat Message Template -->
                <div class="chat-message">
                    <div class="flex items-start space-x-3">
                        <img src="/static/images/default-avatar.png" alt="User" class="w-8 h-8 rounded-full">
                        <div class="flex-1">
                            <div class="flex items-center space-x-2">
                                <span class="font-medium text-gray-900">John Doe</span>
                                <span class="text-xs text-gray-500">2:34 PM</span>
                            </div>
                            <p class="text-gray-700 mt-1">Great session! Really helpful explanations.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chat Input -->
            <div class="chat-input p-4 border-t border-gray-200">
                <div class="flex space-x-2">
                    <input 
                        type="text" 
                        id="chatInput"
                        placeholder="Type a message..."
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                        onkeypress="handleChatKeyPress(event)"
                    >
                    <button 
                        onclick="sendChatMessage()"
                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Gift/Tip Section (for learners) -->
            {% if user.role == 'learner' %}
            <div class="gift-section p-4 border-t border-gray-200 bg-yellow-50">
                <h4 class="font-medium text-gray-900 mb-3">Appreciate your mentor</h4>
                <div class="flex space-x-2 mb-3">
                    <button onclick="sendGift(50)" class="flex-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 py-2 px-3 rounded-lg text-sm font-medium">
                        ₹50
                    </button>
                    <button onclick="sendGift(100)" class="flex-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 py-2 px-3 rounded-lg text-sm font-medium">
                        ₹100
                    </button>
                    <button onclick="sendGift(200)" class="flex-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-800 py-2 px-3 rounded-lg text-sm font-medium">
                        ₹200
                    </button>
                </div>
                <button onclick="showCustomGiftModal()" class="w-full bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-3 rounded-lg text-sm font-medium">
                    Custom Amount
                </button>
            </div>
            {% endif %}
        </div>
    </div>

    <!-- Connection Quality Indicator -->
    <div id="connectionQuality" class="absolute top-20 right-4 bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg text-sm">
        <div class="flex items-center space-x-2">
            <div id="qualityIndicator" class="flex space-x-1">
                <div class="w-1 h-3 bg-green-500 rounded"></div>
                <div class="w-1 h-4 bg-green-500 rounded"></div>
                <div class="w-1 h-5 bg-green-500 rounded"></div>
                <div class="w-1 h-6 bg-gray-400 rounded"></div>
            </div>
            <span id="qualityText">Good</span>
        </div>
    </div>

    <!-- Session Recording Indicator -->
    <div id="recordingIndicator" class="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hidden">
        <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span>Recording</span>
        </div>
    </div>
</div>

<!-- Custom Gift Modal -->
<div id="customGiftModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
    <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Send a Custom Gift</h3>
        
        <div class="mb-4">
            <label for="giftAmount" class="block text-sm font-medium text-gray-700 mb-2">Amount (₹)</label>
            <input 
                type="number" 
                id="giftAmount"
                min="10"
                max="10000"
                step="10"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter amount"
            >
        </div>
        
        <div class="mb-4">
            <label for="giftMessage" class="block text-sm font-medium text-gray-700 mb-2">Message (optional)</label>
            <textarea 
                id="giftMessage"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                placeholder="Add a personal message..."
            ></textarea>
        </div>
        
        <div class="flex space-x-3">
            <button 
                onclick="hideCustomGiftModal()"
                class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-lg font-medium">
                Cancel
            </button>
            <button 
                onclick="processCustomGift()"
                class="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-4 rounded-lg font-medium">
                Send Gift
            </button>
        </div>
    </div>
</div>
```

# 14. DATABASE DESIGN

## 14.1 Entity Relationship Model

### 14.1.1 Core Database Entities

**Primary Entities and Relationships:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │     Session     │    │     Booking     │
│                 │    │                 │    │                 │
│ • id (PK)       │───▶│ • id (PK)       │◄──▶│ • id (PK)       │
│ • username      │    │ • mentor_id(FK) │    │ • learner_id(FK)│
│ • email         │    │ • title         │    │ • session_id(FK)│
│ • role          │    │ • description   │    │ • status        │
│ • skills        │    │ • price         │    │ • payment_id    │
│ • profile_image │    │ • schedule      │    │ • amount_paid   │
│ • created_at    │    │ • duration      │    │ • created_at    │
└─────────────────┘    │ • status        │    └─────────────────┘
                       └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │PopularityMetric │
                    │                 │
                    │ • id (PK)       │
                    │ • session_id(FK)│
                    │ • view_count    │
                    │ • booking_count │
                    │ • completion_rate│
                    │ • rating_average│
                    └─────────────────┘
```

### 14.1.2 Complete Database Schema

**User Management Tables:**
```sql
-- Users table with extended fields
CREATE TABLE users_customuser (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('mentor', 'learner', 'admin')),
    profile_image VARCHAR(100),
    bio TEXT,
    skills TEXT,
    phone VARCHAR(20),
    location VARCHAR(100),
    timezone VARCHAR(50),
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mentor specific profile data
CREATE TABLE users_mentorprofile (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    expertise_areas TEXT,
    teaching_experience INTEGER DEFAULT 0,
    hourly_rate DECIMAL(8,2),
    availability_schedule JSONB,
    certifications TEXT,
    languages TEXT,
    total_earnings DECIMAL(10,2) DEFAULT 0.00,
    available_for_payout DECIMAL(10,2) DEFAULT 0.00,
    total_sessions INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learner specific profile data
CREATE TABLE users_learnerprofile (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    learning_goals TEXT,
    skill_level VARCHAR(20) DEFAULT 'beginner',
    preferred_schedule JSONB,
    budget_range VARCHAR(50),
    learning_style VARCHAR(50),
    interests TEXT,
    total_sessions INTEGER DEFAULT 0,
    total_hours DECIMAL(6,2) DEFAULT 0.00,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    skills_learned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Session Management Tables:**
```sql
-- Sessions table
CREATE TABLE sessions_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mentor_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    thumbnail VARCHAR(100),
    category VARCHAR(50),
    skills TEXT,
    price DECIMAL(8,2),
    schedule TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER NOT NULL,
    max_participants INTEGER DEFAULT 10,
    current_participants INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft' CHECK (
        status IN ('draft', 'scheduled', 'live', 'completed', 'cancelled')
    ),
    room_id VARCHAR(100) UNIQUE,
    recording_url VARCHAR(200),
    materials JSONB,
    prerequisites TEXT,
    learning_objectives TEXT,
    session_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bookings table
CREATE TABLE sessions_booking (
    id SERIAL PRIMARY KEY,
    learner_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'confirmed', 'completed', 'cancelled', 'refunded', 'no_show')
    ),
    payment_id VARCHAR(100),
    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    razorpay_signature VARCHAR(200),
    amount_paid DECIMAL(8,2),
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    booking_notes TEXT,
    attendance_status VARCHAR(20) DEFAULT 'pending',
    joined_at TIMESTAMP WITH TIME ZONE,
    left_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(learner_id, session_id)
);

-- Session feedback and ratings
CREATE TABLE sessions_feedback (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    booking_id INTEGER REFERENCES sessions_booking(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    feedback_type VARCHAR(20) DEFAULT 'session' CHECK (
        feedback_type IN ('session', 'mentor', 'platform')
    ),
    is_public BOOLEAN DEFAULT TRUE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, user_id)
);
```

**Payment and Financial Tables:**
```sql
-- Payment transactions
CREATE TABLE payments_transaction (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions_session(id) ON DELETE SET NULL,
    booking_id INTEGER REFERENCES sessions_booking(id) ON DELETE SET NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (
        transaction_type IN ('session_payment', 'gift_payment', 'payout', 'refund')
    ),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'completed', 'failed', 'cancelled', 'refunded')
    ),
    payment_gateway VARCHAR(20) DEFAULT 'razorpay',
    gateway_transaction_id VARCHAR(100),
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    gateway_signature VARCHAR(200),
    gateway_response JSONB,
    description TEXT,
    fees_amount DECIMAL(8,2) DEFAULT 0.00,
    net_amount DECIMAL(10,2),
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Gift payments during sessions
CREATE TABLE payments_gift (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    from_user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    transaction_id INTEGER NOT NULL REFERENCES payments_transaction(id) ON DELETE CASCADE,
    amount DECIMAL(8,2) NOT NULL,
    message TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'completed', 'failed')
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mentor earnings and payouts
CREATE TABLE payments_earning (
    id SERIAL PRIMARY KEY,
    mentor_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions_session(id) ON DELETE SET NULL,
    booking_id INTEGER REFERENCES sessions_booking(id) ON DELETE SET NULL,
    gift_id INTEGER REFERENCES payments_gift(id) ON DELETE SET NULL,
    earning_type VARCHAR(20) NOT NULL CHECK (
        earning_type IN ('session_fee', 'gift_received', 'bonus', 'commission')
    ),
    gross_amount DECIMAL(8,2) NOT NULL,
    platform_fee DECIMAL(8,2) DEFAULT 0.00,
    platform_fee_percentage DECIMAL(5,2) DEFAULT 15.00,
    net_amount DECIMAL(8,2) NOT NULL,
    tax_amount DECIMAL(8,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'available', 'paid_out', 'on_hold')
    ),
    available_for_payout_at TIMESTAMP WITH TIME ZONE,
    payout_id INTEGER,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payout requests and processing
CREATE TABLE payments_payout (
    id SERIAL PRIMARY KEY,
    mentor_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    bank_account_number VARCHAR(50),
    bank_ifsc_code VARCHAR(15),
    bank_account_name VARCHAR(100),
    upi_id VARCHAR(100),
    payout_method VARCHAR(20) NOT NULL CHECK (
        payout_method IN ('bank_transfer', 'upi', 'wallet')
    ),
    status VARCHAR(20) DEFAULT 'requested' CHECK (
        status IN ('requested', 'processing', 'completed', 'failed', 'cancelled')
    ),
    gateway_payout_id VARCHAR(100),
    gateway_response JSONB,
    processing_fee DECIMAL(8,2) DEFAULT 0.00,
    net_amount DECIMAL(10,2),
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Recommendation and Analytics Tables:**
```sql
-- Session popularity metrics for ML recommendations
CREATE TABLE recommendations_popularitymetric (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    view_count INTEGER DEFAULT 0,
    booking_count INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0.00,
    rating_average DECIMAL(3,2) DEFAULT 0.00,
    rating_count INTEGER DEFAULT 0,
    revenue_generated DECIMAL(10,2) DEFAULT 0.00,
    mentor_response_time DECIMAL(8,2) DEFAULT 0.00,
    repeat_booking_rate DECIMAL(5,2) DEFAULT 0.00,
    trending_score DECIMAL(8,4) DEFAULT 0.0000,
    recommendation_score DECIMAL(8,4) DEFAULT 0.0000,
    last_booked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User interaction tracking for ML
CREATE TABLE recommendations_userinteraction (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL CHECK (
        interaction_type IN ('view', 'click', 'bookmark', 'share', 'book', 'complete', 'rate')
    ),
    interaction_data JSONB,
    interaction_duration INTEGER DEFAULT 0,
    device_type VARCHAR(20),
    user_agent TEXT,
    ip_address INET,
    referrer_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skill popularity and trending
CREATE TABLE recommendations_skillmetric (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    total_sessions INTEGER DEFAULT 0,
    total_mentors INTEGER DEFAULT 0,
    total_learners INTEGER DEFAULT 0,
    average_price DECIMAL(8,2) DEFAULT 0.00,
    popularity_score DECIMAL(8,4) DEFAULT 0.0000,
    growth_rate DECIMAL(5,2) DEFAULT 0.00,
    demand_score DECIMAL(8,4) DEFAULT 0.0000,
    supply_score DECIMAL(8,4) DEFAULT 0.0000,
    market_gap_score DECIMAL(8,4) DEFAULT 0.0000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(skill_name, category)
);
```

**Communication and Notification Tables:**
```sql
-- Real-time notifications
CREATE TABLE notifications_notification (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(30) NOT NULL CHECK (
        notification_type IN (
            'booking_confirmed', 'session_starting', 'session_completed',
            'payment_received', 'payout_processed', 'new_message',
            'rating_received', 'session_cancelled', 'system_update'
        )
    ),
    category VARCHAR(20) DEFAULT 'general' CHECK (
        category IN ('general', 'payment', 'session', 'system', 'promotional')
    ),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (
        priority IN ('low', 'medium', 'high', 'urgent')
    ),
    is_read BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(200),
    action_data JSONB,
    delivery_method VARCHAR(20) DEFAULT 'in_app' CHECK (
        delivery_method IN ('in_app', 'email', 'sms', 'push')
    ),
    scheduled_for TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Session chat messages
CREATE TABLE communications_sessionmessage (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_customuser(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (
        message_type IN ('text', 'file', 'image', 'system', 'emoji')
    ),
    is_system_message BOOLEAN DEFAULT FALSE,
    reply_to_id INTEGER REFERENCES communications_sessionmessage(id) ON DELETE SET NULL,
    file_url VARCHAR(200),
    file_name VARCHAR(100),
    file_size INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    edited_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- WebRTC session logs
CREATE TABLE communications_webrtcsession (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions_session(id) ON DELETE CASCADE,
    room_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'initializing' CHECK (
        status IN ('initializing', 'connecting', 'connected', 'disconnected', 'failed')
    ),
    participants JSONB,
    connection_quality JSONB,
    bandwidth_stats JSONB,
    recording_status VARCHAR(20) DEFAULT 'not_recording',
    recording_url VARCHAR(200),
    duration_seconds INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    technical_logs JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 14.2 Database Indexes and Optimization

### 14.2.1 Performance Indexes

**Primary Performance Indexes:**
```sql
-- User table indexes
CREATE INDEX idx_users_email ON users_customuser(email);
CREATE INDEX idx_users_username ON users_customuser(username);
CREATE INDEX idx_users_role ON users_customuser(role);
CREATE INDEX idx_users_created_at ON users_customuser(created_at);
CREATE INDEX idx_users_is_active ON users_customuser(is_active);

-- Session table indexes
CREATE INDEX idx_sessions_mentor ON sessions_session(mentor_id);
CREATE INDEX idx_sessions_status ON sessions_session(status);
CREATE INDEX idx_sessions_schedule ON sessions_session(schedule);
CREATE INDEX idx_sessions_category ON sessions_session(category);
CREATE INDEX idx_sessions_price ON sessions_session(price);
CREATE INDEX idx_sessions_created_at ON sessions_session(created_at);

-- Booking table indexes
CREATE INDEX idx_bookings_learner ON sessions_booking(learner_id);
CREATE INDEX idx_bookings_session ON sessions_booking(session_id);
CREATE INDEX idx_bookings_status ON sessions_booking(status);
CREATE INDEX idx_bookings_payment_status ON sessions_booking(payment_status);
CREATE INDEX idx_bookings_created_at ON sessions_booking(created_at);

-- Payment table indexes
CREATE INDEX idx_transactions_user ON payments_transaction(user_id);
CREATE INDEX idx_transactions_type ON payments_transaction(transaction_type);
CREATE INDEX idx_transactions_status ON payments_transaction(status);
CREATE INDEX idx_transactions_created_at ON payments_transaction(created_at);
CREATE INDEX idx_transactions_gateway_id ON payments_transaction(gateway_transaction_id);

-- Recommendation indexes
CREATE INDEX idx_popularity_session ON recommendations_popularitymetric(session_id);
CREATE INDEX idx_popularity_score ON recommendations_popularitymetric(recommendation_score);
CREATE INDEX idx_popularity_trending ON recommendations_popularitymetric(trending_score);
CREATE INDEX idx_popularity_updated ON recommendations_popularitymetric(updated_at);

-- Notification indexes
CREATE INDEX idx_notifications_user ON notifications_notification(user_id);
CREATE INDEX idx_notifications_read ON notifications_notification(is_read);
CREATE INDEX idx_notifications_type ON notifications_notification(notification_type);
CREATE INDEX idx_notifications_created ON notifications_notification(created_at);
```

**Search Optimization Indexes:**
```sql
-- Full-text search indexes
CREATE INDEX idx_sessions_title_search ON sessions_session 
    USING gin(to_tsvector('english', title));
    
CREATE INDEX idx_sessions_description_search ON sessions_session 
    USING gin(to_tsvector('english', description));
    
CREATE INDEX idx_users_skills_search ON users_customuser 
    USING gin(to_tsvector('english', skills));

-- Composite indexes for complex queries
CREATE INDEX idx_sessions_mentor_status_schedule ON sessions_session(mentor_id, status, schedule);
CREATE INDEX idx_bookings_learner_status_created ON sessions_booking(learner_id, status, created_at);
CREATE INDEX idx_sessions_category_price_schedule ON sessions_session(category, price, schedule);
```

## 14.3 Database Triggers and Functions

### 14.3.1 Automated Business Logic

**Update Triggers:**
```sql
-- Update session participant count
CREATE OR REPLACE FUNCTION update_session_participants() 
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'confirmed' THEN
        UPDATE sessions_session 
        SET current_participants = current_participants + 1 
        WHERE id = NEW.session_id;
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status != 'confirmed' AND NEW.status = 'confirmed' THEN
            UPDATE sessions_session 
            SET current_participants = current_participants + 1 
            WHERE id = NEW.session_id;
        ELSIF OLD.status = 'confirmed' AND NEW.status != 'confirmed' THEN
            UPDATE sessions_session 
            SET current_participants = current_participants - 1 
            WHERE id = NEW.session_id;
        END IF;
    ELSIF TG_OP = 'DELETE' AND OLD.status = 'confirmed' THEN
        UPDATE sessions_session 
        SET current_participants = current_participants - 1 
        WHERE id = OLD.session_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_participants
    AFTER INSERT OR UPDATE OR DELETE ON sessions_booking
    FOR EACH ROW EXECUTE FUNCTION update_session_participants();

-- Update mentor earnings
CREATE OR REPLACE FUNCTION update_mentor_earnings() 
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND OLD.status != NEW.status) THEN
        UPDATE users_mentorprofile 
        SET 
            total_earnings = (
                SELECT COALESCE(SUM(net_amount), 0) 
                FROM payments_earning 
                WHERE mentor_id = NEW.mentor_id AND status IN ('available', 'paid_out')
            ),
            available_for_payout = (
                SELECT COALESCE(SUM(net_amount), 0) 
                FROM payments_earning 
                WHERE mentor_id = NEW.mentor_id AND status = 'available'
            )
        WHERE user_id = NEW.mentor_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_mentor_earnings
    AFTER INSERT OR UPDATE ON payments_earning
    FOR EACH ROW EXECUTE FUNCTION update_mentor_earnings();

-- Update popularity metrics
CREATE OR REPLACE FUNCTION update_popularity_metrics() 
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'confirmed' THEN
        INSERT INTO recommendations_popularitymetric (session_id, booking_count, last_booked_at)
        VALUES (NEW.session_id, 1, NEW.created_at)
        ON CONFLICT (session_id) 
        DO UPDATE SET 
            booking_count = recommendations_popularitymetric.booking_count + 1,
            last_booked_at = NEW.created_at;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_popularity_metrics
    AFTER INSERT OR UPDATE ON sessions_booking
    FOR EACH ROW EXECUTE FUNCTION update_popularity_metrics();
```

# 15. NORMALIZATION

## 15.1 Database Normalization Analysis

### 15.1.1 First Normal Form (1NF)

**1NF Compliance Analysis:**
The PeerLearn database achieves First Normal Form by ensuring:

1. **Atomic Values:** All columns contain indivisible values
2. **Unique Column Names:** Each column has a distinct name
3. **Consistent Data Types:** Each column contains values of the same data type
4. **Primary Keys:** Every table has a unique identifier

**Example - Users Table 1NF Compliance:**
```sql
-- BEFORE (Violates 1NF - Non-atomic skills column)
CREATE TABLE users_bad (
    id UUID PRIMARY KEY,
    username VARCHAR(150),
    skills VARCHAR(500) -- "Python, React, Django, Machine Learning"
);

-- AFTER (1NF Compliant - Atomic values)
CREATE TABLE users_customuser (
    id UUID PRIMARY KEY,
    username VARCHAR(150),
    skills TEXT -- Will be handled by application layer or separate table
);

-- Better approach - Separate skills table
CREATE TABLE user_skills (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users_customuser(id),
    skill_name VARCHAR(100),
    proficiency_level VARCHAR(20),
    UNIQUE(user_id, skill_name)
);
```

### 15.1.2 Second Normal Form (2NF)

**2NF Compliance Analysis:**
All tables achieve Second Normal Form by ensuring:

1. **1NF Compliance:** Tables are already in 1NF
2. **Full Functional Dependency:** All non-key attributes depend on the entire primary key

**Example - Booking Table 2NF Analysis:**
```sql
-- POTENTIAL 2NF VIOLATION (if designed poorly)
CREATE TABLE booking_details_bad (
    booking_id INTEGER,
    session_id UUID,
    learner_name VARCHAR(100),  -- Depends only on learner_id, not full key
    session_title VARCHAR(200), -- Depends only on session_id, not full key
    booking_date DATE,
    PRIMARY KEY (booking_id, session_id)
);

-- 2NF COMPLIANT DESIGN
CREATE TABLE sessions_booking (
    id SERIAL PRIMARY KEY,           -- Single primary key
    learner_id UUID NOT NULL,        -- References user for name
    session_id UUID NOT NULL,        -- References session for title
    status VARCHAR(20),              -- Depends on full primary key
    created_at TIMESTAMP,            -- Depends on full primary key
    FOREIGN KEY (learner_id) REFERENCES users_customuser(id),
    FOREIGN KEY (session_id) REFERENCES sessions_session(id)
);
```

### 15.1.3 Third Normal Form (3NF)

**3NF Compliance Analysis:**
The database achieves Third Normal Form by eliminating transitive dependencies:

**Example - Session Table 3NF Analysis:**
```sql
-- POTENTIAL 3NF VIOLATION
CREATE TABLE sessions_bad (
    id UUID PRIMARY KEY,
    mentor_id UUID,
    mentor_email VARCHAR(254),  -- Transitively dependent on mentor_id
    mentor_rating DECIMAL(3,2), -- Transitively dependent on mentor_id
    title VARCHAR(200),
    price DECIMAL(8,2)
);

-- 3NF COMPLIANT DESIGN
CREATE TABLE sessions_session (
    id UUID PRIMARY KEY,
    mentor_id UUID REFERENCES users_customuser(id), -- Only mentor reference
    title VARCHAR(200),
    price DECIMAL(8,2)
    -- Mentor details accessed through foreign key relationship
);

CREATE TABLE users_customuser (
    id UUID PRIMARY KEY,
    email VARCHAR(254),
    -- Other user attributes including calculated ratings
);
```

### 15.1.4 Boyce-Codd Normal Form (BCNF)

**BCNF Analysis:**
Most tables achieve BCNF compliance. The primary consideration is ensuring determinants are candidate keys.

**Example - Payment Transaction BCNF:**
```sql
-- BCNF COMPLIANT
CREATE TABLE payments_transaction (
    id SERIAL PRIMARY KEY,                    -- Candidate key
    gateway_transaction_id VARCHAR(100),      -- Alternative candidate key
    user_id UUID NOT NULL,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    -- All non-key attributes depend only on candidate keys
    UNIQUE(gateway_transaction_id)
);
```

## 15.2 Denormalization Decisions

### 15.2.1 Strategic Denormalization

**Performance-Driven Denormalization:**
Some strategic denormalization improves query performance for frequently accessed data:

```sql
-- Denormalized popularity metrics for fast recommendations
CREATE TABLE recommendations_popularitymetric (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    view_count INTEGER DEFAULT 0,           -- Denormalized count
    booking_count INTEGER DEFAULT 0,        -- Denormalized count  
    completion_rate DECIMAL(5,2),          -- Calculated field
    rating_average DECIMAL(3,2),           -- Calculated field
    trending_score DECIMAL(8,4),           -- Computed score
    recommendation_score DECIMAL(8,4)      -- ML-computed score
);

-- Denormalized user profile summary
ALTER TABLE users_customuser ADD COLUMN 
    session_count INTEGER DEFAULT 0,       -- Denormalized for quick access
    total_earned DECIMAL(10,2) DEFAULT 0,  -- Denormalized mentor earnings
    average_rating DECIMAL(3,2) DEFAULT 0; -- Denormalized rating
```

**Justification for Denormalization:**
1. **Read Performance:** Frequently queried aggregations
2. **Recommendation Engine:** Real-time ML computations need fast access
3. **Dashboard Performance:** User metrics displayed on every page load
4. **Search Optimization:** Faceted search requires quick aggregations

### 15.2.2 Controlled Redundancy

**Maintained through Triggers:**
```sql
-- Automatic updates maintain denormalized data consistency
CREATE OR REPLACE FUNCTION maintain_user_stats() 
RETURNS TRIGGER AS $$
BEGIN
    -- Update session count when session status changes
    UPDATE users_customuser 
    SET session_count = (
        SELECT COUNT(*) 
        FROM sessions_session 
        WHERE mentor_id = NEW.mentor_id AND status = 'completed'
    )
    WHERE id = NEW.mentor_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

# 16. DATA FLOW DIAGRAM

## 16.1 Context Level DFD (Level 0)

```
                    ┌─────────────────────────────────────┐
                    │                                     │
        ┌───────────│            PEERLEARN                │◄──────────┐
        │           │         LEARNING PLATFORM           │           │
        │           │                                     │           │
        │           └─────────────────────────────────────┘           │
        ▼                                                             │
┌─────────────┐                                                ┌─────────────┐
│   MENTORS   │                                                │  LEARNERS   │
│             │                                                │             │
│ • Create    │                                                │ • Browse    │
│   Sessions  │                                                │   Sessions  │
│ • Teach     │                                                │ • Book &    │
│ • Earn      │                                                │   Learn     │
│   Money     │                                                │ • Pay Fees  │
└─────────────┘                                                └─────────────┘
        │                                                             ▲
        │           ┌─────────────────────────────────────┐           │
        └──────────►│                                     │───────────┘
                    │         ADMIN USERS                 │
                    │                                     │
                    │ • Platform Management               │
                    │ • User Monitoring                   │
                    │ • Financial Oversight               │
                    │ • Content Moderation                │
                    └─────────────────────────────────────┘
```

## 16.2 Level 1 DFD - System Decomposition

```
┌─────────────┐    user_data    ┌─────────────────┐    session_info    ┌─────────────┐
│   MENTORS   │─────────────────►│  1.0 USER       │◄───────────────────│  LEARNERS   │
│             │                  │  MANAGEMENT     │     booking_req    │             │
│             │   session_data   │                 │                    │             │
│             │─────────────────►└─────────────────┘                    │             │
│             │                           │                             │             │
│             │                           │ user_profiles               │             │
│             │                           ▼                             │             │
│             │                  ┌─────────────────┐                    │             │
│             │  earnings_info   │      USER       │                    │             │
│             │◄─────────────────│    DATABASE     │                    │             │
└─────────────┘                  └─────────────────┘                    └─────────────┘
        │                                 │                                      │
        │ session_creation                │ session_retrieval                    │ payment_info
        ▼                                 ▼                                      ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│  2.0 SESSION    │─────────────►│    SESSION      │◄─────────────│  3.0 PAYMENT   │
│  MANAGEMENT     │session_data  │   DATABASE      │booking_data  │   PROCESSING    │
│                 │              │                 │              │                 │
│                 │              └─────────────────┘              │                 │
└─────────────────┘                       │                      └─────────────────┘
        │                                 │                               │
        │ webrtc_session                  │ popularity_data               │ transaction_data
        ▼                                 ▼                               ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│  4.0 VIDEO      │              │  5.0 MACHINE    │              │   FINANCIAL     │
│  COMMUNICATION  │              │  LEARNING       │              │   DATABASE      │
│                 │              │  RECOMMENDATIONS│              │                 │
│                 │              │                 │              │                 │
└─────────────────┘              └─────────────────┘              └─────────────────┘
```

## 16.3 Level 2 DFD - Detailed Process Flow

### 16.3.1 User Management Process (Process 1.0)

```
┌─────────────┐    registration_data    ┌─────────────────┐
│   USERS     │─────────────────────────►│  1.1 USER       │
│             │                          │  REGISTRATION   │
│             │    login_credentials     │                 │
│             │─────────────────────────►└─────────────────┘
│             │                                   │
│             │                                   │ user_profile
│             │                                   ▼
│             │    user_info            ┌─────────────────┐    verified_users
│             │◄────────────────────────│  1.2 USER       │─────────────────┐
│             │                          │  AUTHENTICATION │                 │
│             │    profile_updates       │                 │                 │
│             │─────────────────────────►└─────────────────┘                 │
└─────────────┘                                   │                          │
                                                  │ auth_tokens              │
                                                  ▼                          ▼
                                         ┌─────────────────┐         ┌─────────────┐
                                         │  1.3 PROFILE    │         │    USER     │
                                         │  MANAGEMENT     │         │  DATABASE   │
                                         │                 │         │             │
                                         │                 │         │             │
                                         └─────────────────┘         └─────────────┘
                                                  │                          ▲
                                                  │ updated_profile          │
                                                  └──────────────────────────┘
```

### 16.3.2 Session Management Process (Process 2.0)

```
┌─────────────┐    session_creation    ┌─────────────────┐    session_data
│   MENTORS   │─────────────────────────►│  2.1 SESSION    │─────────────────┐
│             │                          │  CREATION       │                 │
│             │    session_updates       │                 │                 │
│             │─────────────────────────►└─────────────────┘                 │
└─────────────┘                                                              │
                                                                             ▼
┌─────────────┐    booking_request     ┌─────────────────┐         ┌─────────────┐
│  LEARNERS   │─────────────────────────►│  2.2 SESSION    │         │   SESSION   │
│             │                          │  BOOKING        │         │  DATABASE   │
│             │    session_access        │                 │         │             │
│             │◄─────────────────────────└─────────────────┘         │             │
└─────────────┘                                   │                  └─────────────┘
                                                  │ booking_confirmation      ▲
                                                  ▼                          │
                                         ┌─────────────────┐                 │
                                         │  2.3 SESSION    │                 │
                                         │  DELIVERY       │                 │
                                         │                 │                 │
                                         │                 │                 │
                                         └─────────────────┘                 │
                                                  │                          │
                                                  │ session_completion       │
                                                  └──────────────────────────┘
```

### 16.3.3 Payment Processing (Process 3.0)

```
┌─────────────┐    payment_request     ┌─────────────────┐
│  LEARNERS   │─────────────────────────►│  3.1 PAYMENT    │
│             │                          │  INITIATION     │
│             │    payment_methods       │                 │
│             │◄─────────────────────────└─────────────────┘
└─────────────┘                                   │
                                                  │ order_creation
                                                  ▼
┌─────────────┐    payment_response    ┌─────────────────┐    payment_verification
│  RAZORPAY   │◄───────────────────────│  3.2 RAZORPAY   │─────────────────────┐
│  GATEWAY    │                        │  INTEGRATION    │                     │
│             │    payment_callback    │                 │                     │
│             │─────────────────────────►└─────────────────┘                     │
└─────────────┘                                   │                            │
                                                  │ verified_payment           │
                                                  ▼                            ▼
┌─────────────┐    earnings_update     ┌─────────────────┐           ┌─────────────┐
│   MENTORS   │◄───────────────────────│  3.3 EARNINGS   │           │  FINANCIAL  │
│             │                        │  DISTRIBUTION   │           │  DATABASE   │
│             │    payout_request      │                 │           │             │
│             │─────────────────────────►└─────────────────┘           │             │
└─────────────┘                                   │                   └─────────────┘
                                                  │ transaction_record         ▲
                                                  └────────────────────────────┘
```

## 16.4 Real-time Data Flow

### 16.4.1 WebRTC Video Session Flow

```
┌─────────────┐    join_session      ┌─────────────────┐    webrtc_offer
│   MENTOR    │──────────────────────►│  4.1 SESSION    │─────────────────┐
│             │                       │  INITIALIZATION │                 │
│             │    video_stream       │                 │                 │
│             │◄──────────────────────└─────────────────┘                 │
└─────────────┘                                │                          │
       ▲                                       │ room_creation            │
       │                                       ▼                          ▼
       │                              ┌─────────────────┐         ┌─────────────┐
       │ peer_connection              │  4.2 WEBRTC     │         │  LEARNERS   │
       │                              │  ROOM MANAGER   │         │             │
       │                              │                 │         │             │
       │                              │                 │◄────────┤ webrtc_answer
       │                              └─────────────────┘         │             │
       │                                       │                  └─────────────┘
       │                                       │ ice_candidates
       │                                       ▼
       │                              ┌─────────────────┐
       └──────────────────────────────│  4.3 P2P        │
                                      │  CONNECTION     │
                                      │  MANAGEMENT     │
                                      │                 │
                                      └─────────────────┘
```

### 16.4.2 Real-time Notification Flow

```
┌─────────────┐    user_action       ┌─────────────────┐    notification_trigger
│   USERS     │──────────────────────►│  6.1 EVENT      │─────────────────────┐
│             │                       │  DETECTION      │                     │
│             │    notifications      │                 │                     │
│             │◄──────────────────────└─────────────────┘                     │
└─────────────┘                                │                              │
       ▲                                       │ event_data                   │
       │                                       ▼                              ▼
       │                              ┌─────────────────┐             ┌─────────────┐
       │ websocket_message            │  6.2 WEBSOCKET  │             │  6.3 EMAIL  │
       │                              │  NOTIFICATION   │             │  NOTIFICATION│
       │                              │  DISPATCHER     │             │  SERVICE    │
       │                              │                 │             │             │
       │                              └─────────────────┘             └─────────────┘
       │                                       │                              │
       │                                       │ real_time_notification       │
       │                                       ▼                              │
       │                              ┌─────────────────┐                     │
       └──────────────────────────────│  NOTIFICATION   │                     │
                                      │  DATABASE       │◄────────────────────┘
                                      │                 │ email_notification
                                      │                 │
                                      └─────────────────┘
```

This documentation now includes comprehensive database design, normalization analysis, and detailed data flow diagrams showing how your PeerLearn platform processes information through every layer of the system. Would you like me to continue with the remaining sections including UML diagrams, testing strategies, and implementation details to complete the full academic project report?
