# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd bzd-taper
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up React frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Run the application**
   ```bash
   ./dev.sh
   ```
   
   Or run separately:
   ```bash
   # Terminal 1: Backend
   source venv/bin/activate && python app.py
   
   # Terminal 2: Frontend
   cd frontend && npm start
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:10000

## Production Deployment

### Render.com (Recommended)

The project is configured for automatic deployment on Render.com:

1. **Connect your GitHub repository** to Render.com
2. **Create a new Web Service**
3. **Use the existing `render.yaml`** configuration
4. **Deploy automatically** on every push to main branch

The `render.yaml` file handles:
- Python dependency installation
- Node.js dependency installation
- React frontend build
- Flask backend serving the built frontend

### Manual Deployment

If deploying elsewhere:

1. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Set environment variables**
   ```bash
   export FLASK_ENV=production
   ```

3. **Run the Flask application**
   ```bash
   source venv/bin/activate
   python app.py
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy frontend files and install Node.js dependencies
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

# Copy source code
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Expose port
EXPOSE 10000

# Run the application
CMD ["python", "app.py"]
```

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port for the Flask application (default: 10000)

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **Node.js dependency conflicts**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

3. **Port conflicts**
   - Change the port in `app.py` or set `PORT` environment variable
   - Update the proxy in `frontend/package.json`

4. **Build failures on Render**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt` and `package.json`

### Development Tips

- Use `./dev.sh` for easy local development
- The frontend proxies API calls to the backend during development
- Production builds serve the frontend from the Flask backend
- Check browser console for API errors during development 