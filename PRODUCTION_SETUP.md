# Production Setup Notes

## Domain and HTTPS Configuration

Your production server is now configured with:

- **Domain**: bananatasks.app
- **HTTPS**: SSL certificates from Let's Encrypt
- **Auto-renewal**: Certbot configured for automatic renewal

## Environment Variables (.env)

Update your production .env file with:

```bash
# Site configuration 
SITE_DOMAIN=bananatasks.app

# Other variables remain the same:
SECRET_KEY=your-production-secret-key
DEBUG=False
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret  
OPENAI_API_KEY=your-openai-key
```

## Google OAuth Setup

Make sure to update your Google OAuth configuration:

1. Go to: https://console.cloud.google.com/apis/credentials?project=todos-app-aug-2025
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add:
   - https://bananatasks.app/accounts/google/login/callback/
   - https://www.bananatasks.app/accounts/google/login/callback/
4. Save the changes

## Firewall Rules

The following GCP firewall rules are configured:
- `allow-todos-http` - Port 80 (HTTP)
- `allow-todos-https` - Port 443 (HTTPS)

## SSL Certificate Renewal

SSL certificates are automatically renewed by certbot. The certificates are located at:
- `/etc/letsencrypt/live/bananatasks.app/`

## Production Deployment

To deploy updates:

```bash
# SSH into production server
gcloud compute ssh todos-vm --zone=us-central1-a --project=todos-app-aug-2025

# Navigate to project directory
cd todos-app

# Pull latest changes (after you push them)
git pull

# Restart services
docker-compose -f docker-compose.prod.yml up -d --build
```

## Production URLs

- **Main site**: https://bananatasks.app
- **Alternative**: https://www.bananatasks.app
- **Admin**: https://bananatasks.app/admin/

## Security Features

- HTTPS with security headers (HSTS, X-Frame-Options, etc.)
- CSRF protection for the domain
- SSL/TLS 1.2+ with modern ciphers
- Automatic HTTP to HTTPS redirect