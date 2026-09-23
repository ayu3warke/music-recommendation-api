# Music Recommendation API

A Django REST API for personalized music recommendations using Spotify Web API, PostgreSQL, Redis, and Celery.

## Features

- Create and update user profiles
- Store favorite genres, artists, and moods
- Generate personalized music recommendations
- Spotify Web API integration
- Demo fallback when Spotify credentials are unavailable
- Redis caching
- Celery background recommendation refresh
- Play, like, and skip activity tracking
- Analytics summary, trends, and per-user analytics
- PostgreSQL persistence
- Docker Compose architecture with Django, PostgreSQL, Redis, Celery, Celery Beat, and Nginx

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Spotify Web API
- Docker / Docker Compose
- Nginx

## API Endpoints

### User APIs

- POST /users/ - Create or update a user profile
- GET /users/{user_id}/ - Get a user profile

### Recommendation APIs

- POST /recommendations/{user_id}/refresh/ - Start asynchronous recommendation refresh
- GET /recommendations/{user_id}/ - Get recommendations

### Activity API

- POST /activity/ - Record play, like, or skip activity

Supported actions: play, like, skip.

### Analytics APIs

- GET /analytics/summary/ - Overall activity summary
- GET /analytics/trends/ - Activity trends
- GET /analytics/user/{user_id}/ - Per-user analytics

### Health Check

- GET /health/ - Application health check

## Spotify Integration

The project includes a Spotify Web API client using the Client Credentials flow.

When Spotify credentials are not configured, the application uses a clearly labelled demo dataset so the API can still be demonstrated.

## Background Processing

Celery is used for asynchronous recommendation refreshes. Celery Beat is configured for periodic processing.

## Caching

Redis is configured as the recommendation cache and Celery broker.

## Database

PostgreSQL is the production database configured through environment variables. SQLite is used as a local fallback when PostgreSQL environment variables are not supplied.

## Docker

Docker Compose includes:

- Django/Gunicorn web service
- PostgreSQL
- Redis
- Celery worker
- Celery Beat
- Nginx reverse proxy

## Setup

Install dependencies:

    pip install -r requirements.txt

Run migrations:

    python manage.py migrate

Start the development server:

    python manage.py runserver

Run checks:

    python manage.py check

Run tests:

    python manage.py test

## Environment Variables

Copy .env.example and provide values for PostgreSQL, Redis, Celery, and Spotify credentials as required.

Do not commit real credentials or .env files.

## Design Assumptions

- Email uniquely identifies a user profile.
- Recommendation results are persisted in PostgreSQL.
- Recommendations are cached in Redis.
- User activities are stored for analytics.
- Celery handles asynchronous recommendation refresh.
- Spotify credentials are optional for local demonstration.

## Security Notes

- Do not commit real Spotify credentials.
- Use environment variables for secrets.
- Configure production authentication, HTTPS, ALLOWED_HOSTS, and stronger rate limits before deployment.
