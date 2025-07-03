# 📧 **SendGrid Setup Guide for PeerLearn Platform**

## 🎯 **What is SendGrid?**

SendGrid is a cloud-based email service that handles transactional emails for your application:
- **Welcome emails** for new users
- **Email verification** for account activation
- **Password reset** emails
- **Session booking confirmations**
- **Payment receipts**
- **Notifications** to mentors and learners

---

## 🚀 **Step-by-Step SendGrid Setup**

### **Step 1: Create SendGrid Account**

1. **Go to SendGrid Website**
   - Visit: https://sendgrid.com
   - Click "Start for Free" or "Sign Up"

2. **Choose Plan**
   - **Free Tier**: 100 emails/day forever (perfect for testing)
   - **Essentials**: $14.95/month for 50,000 emails
   - **Pro**: $89.95/month for 100,000 emails

3. **Account Setup**
   ```
   Email: your-email@gmail.com
   Password: [Create strong password]
   Company: PeerLearn Platform
   Website: https://your-domain.com (or localhost for development)
   ```

4. **Verify Your Email**
   - Check your email inbox
   - Click verification link
   - Complete account verification

---

### **Step 2: Domain Authentication (Recommended)**

1. **Go to Settings → Sender Authentication**
2. **Authenticate Your Domain**
   ```
   Domain: your-domain.com (or use sendgrid's domain for testing)
   Subdomain: mail (optional)
   ```
3. **Add DNS Records** (if using your own domain)
   - Copy the CNAME records
   - Add them to your domain's DNS settings
   - Verify authentication

**For Development/Testing**: Skip domain authentication and use SendGrid's default domain.

---

### **Step 3: Create API Key**

1. **Navigate to Settings → API Keys**
2. **Click "Create API Key"**
3. **Configure API Key**
   ```
   API Key Name: PeerLearn-Production (or PeerLearn-Development)
   API Key Permissions: Full Access (or Restricted Access)
   ```

4. **For Restricted Access** (Recommended for security):
   ```
   Mail Send: Full Access
   Template Engine: Read Access
   Suppressions: Read Access
   ```

5. **Copy Your API Key**
   ```
   Your API Key will look like:
   SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   ⚠️ IMPORTANT: Copy this immediately - it won't be shown again!
   ```

---

### **Step 4: Verify Email Address (For Development)**

1. **Go to Settings → Sender Authentication**
2. **Single Sender Verification**
3. **Add Your Email**
   ```
   From Name: PeerLearn Platform
   From Email: your-email@gmail.com
   Reply To: your-email@gmail.com
   Address: Your address
   City: Your city
   Country: Your country
   ```
4. **Verify Email**
   - Check your email
   - Click verification link

---

### **Step 5: Update Your Environment Configuration**

**Update your `.env` file:**
```bash
# SendGrid Configuration
SENDGRID_API_KEY=SG.your-actual-api-key-here-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=your-verified-email@gmail.com

# For production with custom domain
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

**Example with actual values:**
```bash
SENDGRID_API_KEY=SG.abc123def456ghi789jkl012mno345pqr678stu901vwx234yzA567BCD890EFG123HIJ456
DEFAULT_FROM_EMAIL=anandukrishna2999@gmail.com
```

---

### **Step 6: Update Render Deployment**

**Update `render.yaml`:**
```yaml
- key: SENDGRID_API_KEY
  value: "SG.your-actual-api-key-here"
- key: DEFAULT_FROM_EMAIL
  value: "your-verified-email@gmail.com"
```

---

## 🧪 **Testing Email Functionality**

### **Test Email in Django Shell**
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email sending
result = send_mail(
    subject='Test Email from PeerLearn',
    message='This is a test email to verify SendGrid integration.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@gmail.com'],
    fail_silently=False,
)

print(f"Email sent successfully: {result}")
```

### **Test User Registration Email**
1. Go to your application: `http://localhost:8000`
2. Register a new user account
3. Check your email for verification message
4. Verify the email works correctly

---

## 📊 **SendGrid Dashboard - Monitoring**

After setup, monitor your emails:

1. **Activity Feed**
   - See all sent emails
   - Track delivery status
   - Monitor bounces and spam reports

2. **Statistics**
   - Delivery rates
   - Open rates
   - Click rates
   - Bounce rates

3. **Suppression Management**
   - Bounced emails
   - Spam reports
   - Unsubscribes

---

## 🔧 **Common Issues & Solutions**

### **Issue 1: API Key Not Working**
```bash
# Check if API key is correctly set
python manage.py shell
>>> import os
>>> print(os.getenv('SENDGRID_API_KEY'))
>>> # Should show your API key starting with SG.
```

**Solution**: Ensure API key is correctly copied and no extra spaces.

### **Issue 2: Email Not Sending**
```bash
# Check Django email settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.SENDGRID_API_KEY)
```

**Solution**: Verify EMAIL_BACKEND is set to SendGrid in settings.py.

### **Issue 3: Authentication Failed**
**Cause**: Email address not verified with SendGrid
**Solution**: Complete Single Sender Verification in SendGrid dashboard.

### **Issue 4: Daily Limit Exceeded**
**Cause**: Free tier limited to 100 emails/day
**Solution**: Upgrade to paid plan or wait for daily reset.

---

## 💰 **SendGrid Pricing for PeerLearn**

### **Free Tier** (Recommended for development)
- **100 emails/day**
- **40,000 emails in first 30 days**
- **All essential features**
- **Perfect for testing and development**

### **Essentials Plan** - $14.95/month
- **50,000 emails/month**
- **Email analytics**
- **24/7 support**
- **Good for small scale production**

### **Pro Plan** - $89.95/month
- **100,000 emails/month**
- **Advanced analytics**
- **Dedicated IP**
- **Perfect for scaling PeerLearn**

---

## 📋 **Quick Setup Checklist**

- ✅ **Create SendGrid account** (free tier)
- ✅ **Verify email address** 
- ✅ **Create API key** with appropriate permissions
- ✅ **Copy API key** to safe location
- ✅ **Update .env file** with API key and email
- ✅ **Update render.yaml** for production deployment
- ✅ **Test email functionality** in Django shell
- ✅ **Test user registration** email flow
- ✅ **Monitor emails** in SendGrid dashboard

---

## 🎯 **Next Steps After Setup**

1. **Update All Configuration Files**
   ```bash
   # Your API key should be in:
   - .env (development)
   - render.yaml (production)
   - Any other deployment configs
   ```

2. **Test All Email Features**
   - User registration verification
   - Password reset emails
   - Session booking confirmations
   - Payment receipts

3. **Monitor Usage**
   - Track daily email limits
   - Monitor delivery rates
   - Set up alerts for issues

4. **Scale When Needed**
   - Upgrade plan as user base grows
   - Implement email templates
   - Add email automation

---

## 🔗 **Useful SendGrid Resources**

- **Documentation**: https://docs.sendgrid.com/
- **Django Integration**: https://docs.sendgrid.com/for-developers/sending-email/django
- **API Reference**: https://docs.sendgrid.com/api-reference
- **Status Page**: https://status.sendgrid.com/
- **Support**: https://support.sendgrid.com/

---

## ✅ **Ready for Production**

Once configured, your PeerLearn platform will have:

🎯 **Professional Email Service** - Reliable email delivery  
🎯 **User Communication** - Registration, booking, payment emails  
🎯 **Monitoring & Analytics** - Email performance tracking  
🎯 **Scalable Solution** - From 100 to 100,000+ emails  
🎯 **High Deliverability** - Industry-leading email delivery rates  

**Your platform is now ready for professional email communication!** 📧 