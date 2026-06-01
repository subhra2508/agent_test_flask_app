# Use production-optimized slim base image
FROM python:3.11-slim

# Configure environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

# Create and configure working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY . .

# Create a secure, non-root dedicated user to run the application (Production best practice)
RUN useradd -m flaskuser && chown -R flaskuser:flaskuser /app
USER flaskuser

# Expose target port (matching Cloud Run environment variables)
EXPOSE 8080

# Spin up Gunicorn as production server
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app
