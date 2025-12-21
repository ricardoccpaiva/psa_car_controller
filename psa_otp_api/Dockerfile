FROM python:3.11-slim

LABEL maintainer="PSA OTP API"
LABEL description="REST API for PSA OTP flows"

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY otp_module/ ./otp_module/

# Create directory for session file
RUN mkdir -p /data && chmod 755 /data

# Environment variables
ENV API_HOST=0.0.0.0
ENV API_PORT=5000
ENV API_DEBUG=false
ENV OTP_SESSION_FILE=/data/otp.bin

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn
RUN pip install gunicorn

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
