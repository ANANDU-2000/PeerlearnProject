# 📧 SendGrid Email Service Setup for PeerLearn

## What is SendGrid?
SendGrid provides reliable email delivery for your application:
- Welcome emails for new users
- Email verification for accounts
- Password reset emails
- Session booking confirmations
- Payment receipts

## Step-by-Step Setup

### 1. Create SendGrid Account
- Go to: https://sendgrid.com
- Click "Start for Free"
- Sign up with your email
- Choose FREE plan (100 emails/day)

### 2. Verify Your Email Address
- Go to Settings → Sender Authentication
- Click "Single Sender Verification"
- Add your email address (e.g., anandukrishna2999@gmail.com)
- Verify the email in your inbox

### 3. Create API Key
- Go to Settings → API Keys
- Click "Create API Key"
- Name: PeerLearn-API-Key
- Permissions: Full Access (for simplicity)
- Copy the API key (starts with SG.xxxx)

### 4. Update Environment Configuration

Copy this to your .env file:
```
SENDGRID_API_KEY=SG.your-actual-api-key-here
DEFAULT_FROM_EMAIL=anandukrishna2999@gmail.com
```

### 5. Update render.yaml for Production
```yaml
- key: SENDGRID_API_KEY
  value: "SG.your-actual-api-key-here"
- key: DEFAULT_FROM_EMAIL
  value: "anandukrishna2999@gmail.com"
```

### 6. Test Email Functionality
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'Testing SendGrid integration',
    'anandukrishna2999@gmail.com',
    ['anandukrishna2999@gmail.com'],
)
```

## Quick Setup Summary
1. Create free SendGrid account
2. Verify your email address
3. Create API key with full access
4. Update .env and render.yaml with API key
5. Test email sending

## Cost: FREE
- 100 emails per day
- Perfect for development and small scale

Your email service is now ready for PeerLearn platform! 