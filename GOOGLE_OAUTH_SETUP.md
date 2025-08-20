# Google Cloud OAuth Setup Instructions

## Step-by-Step Setup

### 1. Install Google Cloud CLI

**On macOS (using Homebrew):**
```bash
brew install --cask google-cloud-sdk
```

**On Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 2. Initialize and Authenticate
```bash
# Initialize gcloud
gcloud init

# This will:
# - Open browser for authentication
# - Let you select/create a project
# - Set default region/zone
```

### 3. Create the "todos" Project
```bash
# Create the project
gcloud projects create todos-app-$(date +%s) --name="Todos App"

# Set it as your active project
gcloud config set project todos-app-$(date +%s)

# Or if you want a specific project ID:
gcloud projects create todos-app-unique --name="Todos App"
gcloud config set project todos-app-unique
```

### 4. Enable Required APIs
```bash
# Enable Google+ API (for OAuth)
gcloud services enable plus.googleapis.com

# Enable Google Identity API (newer, recommended)
gcloud services enable identitytoolkit.googleapis.com

# List enabled services to verify
gcloud services list --enabled
```

### 5. Create OAuth 2.0 Credentials

**Open the credentials page:**
```bash
# Open the credentials page for your project
open "https://console.cloud.google.com/apis/credentials?project=$(gcloud config get-value project)"
```

**Manual steps in Console:**
1. Click "**+ CREATE CREDENTIALS**" → "**OAuth client ID**"
2. Choose "**Web application**"
3. Name: "Todos App"
4. **Authorized redirect URIs:** 
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/` (backup)
5. Copy the credentials that appear in the popup

### 6. Configure OAuth Consent Screen
If prompted, set up the OAuth consent screen:
- **User Type:** External (unless you have Google Workspace)
- **App name:** Todos App
- **User support email:** Your email
- **Developer contact:** Your email
- **Scopes:** Just the basic profile and email scopes (already selected)

### 7. Update Your .env File
```bash
# Update your .env file with the real credentials
GOOGLE_OAUTH_CLIENT_ID=your-client-id-from-google
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-from-google
```

### 8. Apply the Configuration
```bash
# Run the setup command to update Django
docker-compose exec web python manage.py setup_oauth
```

## Quick Commands Summary

```bash
# 1. Install gcloud (if not installed)
brew install --cask google-cloud-sdk

# 2. Initialize
gcloud init

# 3. Create project
gcloud projects create todos-app-$(date +%s) --name="Todos App"

# 4. Enable APIs
gcloud services enable plus.googleapis.com identitytoolkit.googleapis.com

# 5. Open credentials page
open "https://console.cloud.google.com/apis/credentials?project=$(gcloud config get-value project)"

# 6. After creating OAuth credentials, update .env and run:
docker-compose exec web python manage.py setup_oauth
```

## Current Status
✅ Django todo app fully built and running  
✅ Docker environment ready  
✅ Templates, JavaScript, and API endpoints complete  
✅ OAuth configuration ready (needs real credentials)  
✅ Admin access available (admin/admin123)  

**Next:** Set up Google Cloud OAuth credentials and you'll have a fully functional collaborative todo app! 🚀