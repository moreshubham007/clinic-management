# Docker Flask-Only Setup

This guide explains how to use the `docker-compose-flask.yml` file to run only the Flask application in a Docker container.

## Overview

The `docker-compose-flask.yml` file is designed to run only the Flask application without the MySQL database and Adminer services. This is useful when:

- You want to connect to an external database
- You're running MySQL locally on your host machine
- You want to use a different database setup
- You're doing development and want more control over individual services

## Quick Start

### 1. Basic Usage

```bash
# Build and start the Flask app
docker-compose -f docker-compose-flask.yml up --build

# Run in detached mode (background)
docker-compose -f docker-compose-flask.yml up -d

# Stop the Flask app
docker-compose -f docker-compose-flask.yml down
```

### 2. Database Configuration Options

The file includes three database configuration options. Choose one by uncommenting the appropriate line in the `docker-compose-flask.yml` file:

#### Option 1: External MySQL Database (Default)
```yaml
- DATABASE_URL=mysql://hospital:hospital123@host.docker.internal:3306/clinic_db
```
- Use this when you have MySQL running on your host machine
- The container can access host services via `host.docker.internal`

#### Option 2: Local MySQL
```yaml
- DATABASE_URL=mysql://hospital:hospital123@localhost:3306/clinic_db
```
- Use this if you have specific network configurations

#### Option 3: SQLite for Development
```yaml
- DATABASE_URL=sqlite:///clinic.db
```
- Use this for simple development without MySQL

### 3. Prerequisites

Before running the Flask-only container, ensure you have:

1. **Database Running** (if using MySQL):
   ```bash
   # If using the original docker-compose.yml for database only
   docker-compose up mysql_db -d
   
   # Or if you have MySQL installed locally
   mysql -u root -p
   ```

2. **Environment Variables**: Update the environment variables in `docker-compose-flask.yml`:
   - `SECRET_KEY`: Change to a secure random key for production
   - `MAIL_*`: Update with your email configuration
   - `GOOGLE_*`: Update with your Google OAuth credentials

## Configuration Details

### Container Settings
- **Container Name**: `clinic_flask_app`
- **Port**: `5000:5000` (host:container)
- **Restart Policy**: `unless-stopped`

### Volumes Mounted
- `./:/app` - Your application code (for development)
- `./data/uploads:/app/uploads` - File uploads
- `./logs:/app/logs` - Application logs

### Health Check
The container includes a health check that:
- Checks if the app responds on `http://localhost:5000/`
- Runs every 30 seconds
- Times out after 10 seconds
- Retries 3 times before marking as unhealthy

## Common Commands

### Development Commands
```bash
# View logs
docker-compose -f docker-compose-flask.yml logs -f

# Execute commands in the running container
docker-compose -f docker-compose-flask.yml exec flask_app bash

# Restart just the Flask app
docker-compose -f docker-compose-flask.yml restart flask_app

# View container status
docker-compose -f docker-compose-flask.yml ps
```

### Database Migration Commands
```bash
# Run migrations inside the container
docker-compose -f docker-compose-flask.yml exec flask_app flask db upgrade

# Create new migration
docker-compose -f docker-compose-flask.yml exec flask_app flask db migrate -m "Your migration message"
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure your database is running and accessible
   - Check the `DATABASE_URL` environment variable
   - Verify network connectivity

2. **Port Already in Use**:
   ```bash
   # Change the port mapping in docker-compose-flask.yml
   ports:
     - "5001:5000"  # Use port 5001 instead
   ```

3. **File Permission Issues**:
   ```bash
   # Fix upload directory permissions
   chmod 777 data/uploads
   ```

### Checking Container Health
```bash
# Check if container is healthy
docker inspect clinic_flask_app | grep Health -A 10

# View health check logs
docker-compose -f docker-compose-flask.yml logs flask_app | grep health
```

## Comparison with Full Setup

| Feature | docker-compose.yml | docker-compose-flask.yml |
|---------|-------------------|---------------------------|
| Flask App | ✅ | ✅ |
| MySQL Database | ✅ | ❌ |
| Adminer UI | ✅ | ❌ |
| Network Isolation | ✅ | ❌ |
| External DB Support | ❌ | ✅ |
| Lighter Resource Usage | ❌ | ✅ |

## Production Considerations

When using this setup for production:

1. **Change the SECRET_KEY** to a secure random value
2. **Update database credentials** for security
3. **Configure proper mail settings**
4. **Set up SSL/HTTPS** if needed
5. **Use production WSGI server** (consider updating Dockerfile)
6. **Set up proper logging and monitoring**

## Integration with Existing Setup

You can run both setups simultaneously on different ports:

```bash
# Run full setup on port 5000
docker-compose up -d

# Run Flask-only on port 5001
# (after changing port in docker-compose-flask.yml)
docker-compose -f docker-compose-flask.yml up -d
``` 