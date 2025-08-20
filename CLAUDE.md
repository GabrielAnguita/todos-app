# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Django Todos App - Claude Documentation

## 🚀 Project Overview
A real-time collaborative todo application built with Django, WebSockets, and optimistic UI updates.

## 🏗️ Architecture
- **Backend**: Django 4.2.7 with Django REST Framework
- **Real-time**: Django Channels + WebSockets + Redis
- **Frontend**: Vanilla JavaScript with Tailwind CSS
- **Auth**: Google OAuth2 only (django-allauth)
- **Database**: PostgreSQL
- **Deployment**: Docker Compose

## 🏗️ Architecture Overview

### Core Applications
- **accounts/**: Custom user model extending Django's User
- **workspaces/**: Multi-tenant workspace system with member management and invitations
- **tasks/**: Task management with real-time collaboration features

### Key Technologies
- **Django Channels + WebSockets**: Real-time task updates via TaskConsumer and WorkspaceConsumer
- **Django REST Framework**: API endpoints for task CRUD operations
- **django-allauth**: Google OAuth2-only authentication (SOCIALACCOUNT_ONLY = True)
- **Celery**: Background task processing (configured but optional)
- **Redis**: Channel layer backend and Celery broker

### Data Models
- **User** (accounts): Custom user model with email-based authentication
- **Workspace** (workspaces): Multi-tenant containers for tasks
- **WorkspaceMember** (workspaces): User membership in workspaces
- **Invite** (workspaces): Email-based workspace invitations
- **Task** (tasks): Core task model with workspace association, assignment, due dates, and AI time estimation

### Real-time Architecture
- **WebSocket Consumers**: 
  - `/ws/task/{id}/` - Individual task updates (TaskConsumer)
  - `/ws/workspace/{id}/` - Workspace-level task notifications (WorkspaceConsumer)
- **Django Signals**: Automatic WebSocket broadcasts on model changes (tasks/signals.py)
- **Permission Checks**: WebSocket connections validate workspace access before allowing connections

### API Design
- REST API endpoints in `tasks/api_views.py`
- DRF serializers handle JSON serialization
- Session-based authentication with IsAuthenticated permission
- PATCH `/tasks/api/tasks/{id}/` for task field updates

### Frontend Integration
- Vanilla JavaScript with optimistic UI updates
- HTMX integration for seamless form submissions
- Tailwind CSS for styling
- Real-time WebSocket client in `static/js/task-detail.js`

## 🔧 Development Commands

### Docker Environment
```bash
# Start all services (PostgreSQL, Redis, Django web server, Celery worker)
docker-compose up -d

# Rebuild containers after dependency changes
docker-compose build

# View application logs
docker-compose logs web

# Stop and remove all containers and volumes (full reset)
docker-compose down -v
```

### Database Operations
```bash
# Run Django migrations
docker-compose exec web python manage.py migrate

# Create new migrations after model changes
docker-compose exec web python manage.py makemigrations

# Access Django shell
docker-compose exec web python manage.py shell
```

### OAuth Setup
```bash
# Configure Google OAuth credentials (after setting up Google Cloud project)
docker-compose exec web python manage.py setup_oauth
```

### Testing and Development
```bash
# No specific test framework configured - check for Django's default test setup
# Run Django tests (if any exist):
docker-compose exec web python manage.py test
```

### Admin Access
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

## 🔑 Google OAuth Setup (TODO)

### Quick Commands
```bash
# 1. Install gcloud
brew install --cask google-cloud-sdk

# 2. Initialize
gcloud init

# 3. Create project
gcloud projects create todos-app-$(date +%s) --name="Todos App"

# 4. Enable APIs
gcloud services enable plus.googleapis.com identitytoolkit.googleapis.com

# 5. Open credentials page
open "https://console.cloud.google.com/apis/credentials?project=$(gcloud config get-value project)"

# 6. Create OAuth 2.0 Web App with redirect URI:
# http://127.0.0.1:8000/accounts/google/login/callback/

# 7. Update .env with real credentials and run:
docker-compose exec web python manage.py setup_oauth
```

## 🌍 Environment Configuration

### .env File Structure
```bash
DEBUG=True
SECRET_KEY=django-insecure-_k^go=pb%nea4(pf780y(2ljrky##*(tc$w_rt#9(dpf#(-i&*

# Site configuration
SITE_DOMAIN=127.0.0.1:8000        # Change for production
SITE_NAME=Todos App

# Database
DATABASE_URL=postgres://todos_user:todos_password@db:5432/todos_db

# Redis
REDIS_URL=redis://redis:6379

# Google OAuth (set these up)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id-here
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret-here

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key-here
```

### Production Configuration
For production, update:
```bash
SITE_DOMAIN=yourdomain.com
DEBUG=False
SECRET_KEY=your-secure-secret-key
```

## 🔄 Real-time Features

### WebSocket Architecture
- **TaskConsumer**: Individual task updates (`/ws/task/{id}/`)
- **WorkspaceConsumer**: Workspace task lists (`/ws/workspace/{id}/`)
- **Signals**: Auto-broadcast on model changes
- **Optimistic Updates**: Immediate UI feedback

### API Endpoints
- `PATCH /tasks/api/tasks/{id}/` - Update task fields
- WebSocket rooms handle real-time sync

## 🎯 Key Features
✅ **Google OAuth** authentication only  
✅ **Workspace sharing** with permissions  
✅ **Real-time collaboration** via WebSockets  
✅ **Optimistic UI** updates  
✅ **Inline editing** for all task fields  
✅ **Modern frontend** with Tailwind CSS  
✅ **REST API** with DRF serializers  
✅ **Docker deployment** ready  

## 🐛 Common Issues

1. **OAuth Authentication**: Requires valid Google Cloud OAuth credentials - app uses SOCIALACCOUNT_ONLY=True
2. **WebSocket Connections**: Depend on Redis being available - check `docker-compose logs redis`
3. **Port Conflicts**: Default ports 8000 (Django), 5432 (PostgreSQL), 6379 (Redis)
4. **Permission System**: Uses Django's built-in permissions with workspace-level access control
5. **Migration errors**: Delete containers and volumes, rebuild from scratch
6. **OAuth errors**: Ensure no duplicate SocialApp objects in database

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_oauth
```

## 📋 TODO for Next Session
- [ ] Set up Google Cloud project
- [ ] Create OAuth credentials
- [ ] Test Google authentication
- [ ] Set up Celery for OpenAI integration (optional)

## 🏃‍♂️ Current Status
✅ **App DEPLOYED and running** on http://34.46.123.23.nip.io  
✅ **All features implemented**  
✅ **Google OAuth configured and working**
✅ **Production deployment with nginx + static files**

## 🚀 Production Deployment Info

### GCP Details
- **Project ID**: `todos-app-aug-2025`
- **VM Name**: `todos-vm`
- **Zone**: `us-central1-a`
- **External IP**: `34.46.123.23`
- **Machine Type**: `e2-medium` (2 vCPUs, 4GB RAM)
- **Monthly Cost**: ~$23

### Access Commands
```bash
# SSH into production VM
gcloud compute ssh todos-vm --zone=us-central1-a --project=todos-app-aug-2025

# Deploy updates
cd todos-app
git pull
./deploy-vm.sh

# Check logs
docker-compose logs -f web

# Check status
docker-compose ps
```

### URLs
- **Live App**: http://34.46.123.23.nip.io
- **GitHub Repo**: https://github.com/GabrielAnguita/todos-app.git

### Services Running
- **Django app** (with Channels WebSockets)
- **PostgreSQL** database
- **Redis** (Channels + Celery)
- **Nginx** (static files + proxy)
- **Celery** worker (AI estimation)