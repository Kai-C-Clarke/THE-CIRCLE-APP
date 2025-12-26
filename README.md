# THE CIRCLE APP

A family memory preservation application that helps you create, organize, and cherish memories together. Built with Flask and designed for simplicity and security.

## 🌟 Features

- **Memory Management**: Create, edit, and organize family memories with rich text and metadata
- **Photo & Video Support**: Upload and manage media files with automatic organization
- **AI-Powered Photo Matching**: Intelligent photo-to-memory matching using AI
- **Audio Recording**: Capture voice memories directly in the app
- **Categorization**: Organize memories by category, year, and custom tags
- **People Tracking**: Tag family members in memories and media
- **Comments**: Add comments and discussions to memories
- **PDF Export**: Generate beautiful PDF reports of your family memories
- **Secure Authentication**: Password-protected access to family data
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Requirements

- Python 3.8+
- SQLite3 (included with Python)
- Modern web browser

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Kai-C-Clarke/THE-CIRCLE-APP.git
cd THE-CIRCLE-APP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```bash
# Required for production
APP_PASSWORD=your-secure-password
SECRET_KEY=your-64-character-hex-string

# Optional
DEEPSEEK_API_KEY=your-api-key  # For AI features
```

Generate a secure SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Initialize Database

The database will be created automatically on first run:

```bash
python app.py
```

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_PASSWORD` | Production | None | Password for authentication |
| `SECRET_KEY` | Production | Auto-generated | Flask session encryption key |
| `ALLOWED_ORIGINS` | No | localhost:5000 | Comma-separated list of allowed CORS origins |
| `DEEPSEEK_API_KEY` | No | None | API key for AI photo matching |
| `FLASK_DEBUG` | No | false | Enable debug mode (development only) |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Development Mode

For local development without authentication:

```bash
# Don't set APP_PASSWORD
python app.py
```

The app will warn about missing authentication but allow access.

### Production Mode

Always set these variables in production:

```bash
export APP_PASSWORD='strong-password-here'
export SECRET_KEY='your-64-char-hex-string'
export ALLOWED_ORIGINS='https://yourdomain.com'
```

## 📚 API Documentation

### Authentication

All write operations require HTTP Basic Authentication:

```bash
curl -X POST http://localhost:5000/api/memories/save \
  -H "Authorization: Basic $(echo -n ':your-password' | base64)" \
  -H "Content-Type: application/json" \
  -d '{"text": "My memory"}'
```

### Endpoints

#### Memories

- `GET /api/memories` - Get all memories
- `GET /api/memories/<id>` - Get specific memory
- `POST /api/memories/save` - Create new memory (requires auth)
- `PUT /api/memories/<id>` - Update memory (requires auth)
- `DELETE /api/memories/delete/<id>` - Delete memory (requires auth)

#### Media

- `GET /api/media` - Get all media files
- `GET /api/media/<id>` - Get specific media
- `POST /api/media/upload` - Upload media (requires auth)
- `PUT /api/media/<id>/update` - Update media (requires auth)
- `DELETE /api/media/delete/<id>` - Delete media (requires auth)

#### Profile

- `GET /api/profile` - Get profile data
- `POST /api/profile/save` - Save profile (requires auth)

#### Audio

- `POST /api/audio/save` - Upload audio recording (requires auth)
- `GET /api/audio/<filename>` - Retrieve audio file

#### AI Features

- `POST /api/ai/match-photos` - Match photos to memories using AI

## 🛡️ Security Features

### Implemented Security

- ✅ **Path Traversal Prevention**: Secure file handling with path validation
- ✅ **Authentication**: HTTP Basic Auth on all write operations
- ✅ **CORS Protection**: Restricted cross-origin requests
- ✅ **Session Security**: Encrypted sessions with SECRET_KEY
- ✅ **SQL Injection Prevention**: Parameterized queries throughout
- ✅ **File Upload Validation**: Type and size restrictions
- ✅ **Environment-Based Configuration**: Secrets in environment variables
- ✅ **Debug Mode Control**: Production-safe debug settings

### Security Best Practices

1. **Never commit secrets**: Use `.env` file (gitignored)
2. **Strong passwords**: Use long, random passwords
3. **HTTPS in production**: Use SSL/TLS (Render provides this)
4. **Regular updates**: Keep dependencies updated
5. **Access logs**: Monitor who accesses the app

## 🖥️ Development

### Project Structure

```
THE-CIRCLE-APP/
├── app.py                  # Main Flask application
├── database.py             # Database schema and operations
├── ai_photo_matcher.py     # AI photo matching logic
├── logging_config.py       # Centralized logging
├── requirements.txt        # Python dependencies
├── static/                 # CSS, JavaScript, images
├── templates/              # HTML templates
├── uploads/                # User-uploaded files (gitignored)
├── logs/                   # Application logs (gitignored)
└── circle_memories.db      # SQLite database (gitignored)
```

### Running Tests

Install test dependencies:

```bash
pip install pytest pytest-cov
```

Run tests:

```bash
pytest
```

### Code Formatting

Format code with Black:

```bash
pip install black
black .
```

### Logging

The app uses Python's logging module with rotating file handlers:

- `logs/the_circle_app.log` - All logs
- `logs/the_circle_app_error.log` - Errors only

Configure log level:

```bash
export LOG_LEVEL=DEBUG
```

## 🚢 Deployment

### Deploying to Render

1. **Create Render Account**: Sign up at [render.com](https://render.com)

2. **Create Web Service**:
   - Connect your GitHub repository
   - Select "Web Service"
   - Choose the repository

3. **Configure Build**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Set Environment Variables** in Render Dashboard:
   ```
   APP_PASSWORD=your-secure-password
   SECRET_KEY=your-64-char-hex-string
   ALLOWED_ORIGINS=https://your-app.onrender.com
   DEEPSEEK_API_KEY=your-api-key (optional)
   ```

5. **Deploy**: Render will automatically deploy on push to main branch

### Database Persistence

On Render, use a persistent disk:
- Add a disk mount at `/opt/render/project/src`
- Database will persist across deploys

### HTTPS

Render automatically provides SSL/TLS certificates.

## 🔍 Database Schema

### Tables

- **memories**: Main memory records
- **media**: Photos and videos
- **memory_media**: Links memories to media
- **comments**: Comments on memories
- **memory_tags**: Tags for memories
- **memory_people**: People tagged in memories
- **profile**: User profile data

### Indexes

Performance-optimized with 10 indexes on foreign keys and search columns.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a personal family project, but suggestions and bug reports are welcome via GitHub issues.

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review security audit reports in the repository

## 🎯 Roadmap

Future enhancements:
- [ ] Rate limiting for API endpoints
- [ ] CSRF protection for forms
- [ ] Audit logging for data modifications
- [ ] Multi-user support with roles
- [ ] Email notifications
- [ ] Timeline view
- [ ] Advanced search filters
- [ ] Mobile app

## 📊 Health Status

**Overall Security Score**: 97/100 (A+)

See detailed reports:
- [Security Audit Report](SECURITY_AUDIT_REPORT.md)
- [Security Fixes Applied](SECURITY_FIXES_APPLIED.md)
- [Comprehensive Health Report](COMPREHENSIVE_HEALTH_REPORT.md)
- [Dependency Audit Report](DEPENDENCY_AUDIT_REPORT.md)

---

**Built with ❤️ for preserving family memories**
