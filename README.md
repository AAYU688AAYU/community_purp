# CommunityConnect Backend

This is the backend implementation for CommunityConnect, a smart society management system. The backend is split into two main components:

1. Django Application (REST API)
2. FastAPI Application (Real-time Features)

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual Environment

### Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```sql
CREATE DATABASE communityconnect;
```

5. Configure environment variables:
Create a `.env` file in the root directory with:
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/communityconnect
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000
```

6. Run Django migrations:
```bash
cd django_app
python manage.py migrate
python manage.py createsuperuser
```

7. Start the Django development server:
```bash
python manage.py runserver
```

8. Start the FastAPI server (in a new terminal):
```bash
cd fastapi_app
uvicorn app.main:app --reload
```

## API Documentation

### Django REST API (http://localhost:8000)

#### Authentication Endpoints
- POST `/api/auth/register/` - Register new user
- POST `/api/auth/login/` - Login user
- POST `/api/auth/refresh/` - Refresh JWT token
- POST `/api/auth/verify/` - Verify JWT token

#### User Management
- GET `/api/users/me/` - Get current user profile
- PUT `/api/users/me/` - Update user profile
- GET `/api/users/` - List all users (admin only)

#### Society Management
- GET `/api/issues/` - List all issues
- POST `/api/issues/` - Create new issue
- GET `/api/issues/{id}/` - Get issue details
- PUT `/api/issues/{id}/` - Update issue
- POST `/api/issues/{id}/comments/` - Add comment to issue

- GET `/api/notices/` - List all notices
- POST `/api/notices/` - Create new notice
- GET `/api/notices/{id}/` - Get notice details

- GET `/api/meetings/` - List all meetings
- POST `/api/meetings/` - Schedule new meeting
- GET `/api/meetings/{id}/` - Get meeting details

### FastAPI (http://localhost:8000)

#### Real-time Features

##### QR Code Generation
- POST `/api/qr/generate` - Generate QR code for visitor
- GET `/api/qr/validate/{token}` - Validate QR code

##### Virtual Meetings
- WebSocket `/api/meetings/ws/{meeting_id}` - Join virtual meeting
- GET `/api/meetings/active` - List active meetings
- POST `/api/meetings/{meeting_id}/recording/start` - Start meeting recording
- POST `/api/meetings/{meeting_id}/recording/stop` - Stop meeting recording

##### Notifications
- WebSocket `/api/notifications/ws` - Real-time notifications
- POST `/api/notifications/send/{user_id}` - Send notification to user
- POST `/api/notifications/broadcast` - Broadcast notification to all users

## Development

### Project Structure
```
backend/
├── django_app/
│   ├── community_connect/
│   │   ├── users/
│   │   └── society/
│   ├── fastapi_app/
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   └── main.py
│   ├── static/
│   ├── media/
│   ├── requirements.txt
│   └── README.md
```

### Testing
```bash
# Run Django tests
cd django_app
python manage.py test

# Run FastAPI tests
cd fastapi_app
pytest
```

### Code Style
The project follows PEP 8 style guide. Use `black` for formatting:
```bash
black .
```

## Security Considerations

1. JWT tokens are used for authentication
2. CORS is configured for frontend origin only
3. Sensitive data is not exposed in API responses
4. File uploads are validated and sanitized
5. WebSocket connections are authenticated
6. Database queries are protected against SQL injection
7. Password hashing using Django's default hasher

## Production Deployment

For production:
1. Set `DEBUG=False`
2. Use proper secret keys
3. Configure proper database credentials
4. Set up proper CORS origins
5. Use HTTPS
6. Set up proper static/media file serving
7. Configure proper logging
8. Use production-grade servers (Gunicorn/Uvicorn behind Nginx)
9. Set up Redis for WebSocket/real-time features
10. Configure proper email backend

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 