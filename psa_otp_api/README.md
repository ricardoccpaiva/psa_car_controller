# PSA OTP REST API

A standalone REST API for managing PSA OTP (One-Time Password) flows.

## Features

- ✅ Setup OTP session with SMS code
- ✅ Generate OTP codes
- ✅ Check session status
- ✅ Delete sessions
- ✅ Simple REST interface
- ✅ JSON request/response
- ✅ Error handling
- ✅ Health check endpoint

## Quick Start

### 1. Installation

```bash
cd psa_otp_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# With default settings
python app.py

# Or with custom settings
export API_HOST=0.0.0.0
export API_PORT=5000
export API_DEBUG=false
export OTP_SESSION_FILE=otp.bin
python app.py
```

Server will start at: `http://0.0.0.0:5000`

## API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "PSA OTP API",
  "version": "1.0.0"
}
```

### Setup OTP Session

```http
POST /otp/setup
Content-Type: application/json

{
  "sms_code": "123456",
  "pin_code": "1234"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "device_id": "a1b2c3d4e5f6g7h8",
  "session_file": "otp.bin"
}
```

**Error Response (400/500):**
```json
{
  "status": "error",
  "error": "Error message"
}
```

### Generate OTP Code

```http
POST /otp/generate
Content-Type: application/json

{
  "session_file": "otp.bin"  # Optional
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "otp_code": "a3k9m2"
}
```

**Error Response (400/404/500):**
```json
{
  "status": "error",
  "error": "Session file not found"
}
```

### Check Session Status

```http
GET /otp/status?session_file=otp.bin
```

**Response (200):**
```json
{
  "status": "success",
  "session_exists": true,
  "session_file": "otp.bin"
}
```

### Delete Session

```http
DELETE /otp/session
Content-Type: application/json

{
  "session_file": "otp.bin"  # Optional
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Session deleted"
}
```

**Error Response (404/500):**
```json
{
  "status": "error",
  "error": "Session file not found"
}
```

## Usage Examples

### Using curl

```bash
# Setup OTP session
curl -X POST http://localhost:5000/otp/setup \
  -H "Content-Type: application/json" \
  -d '{"sms_code":"123456","pin_code":"1234"}'

# Generate OTP code
curl -X POST http://localhost:5000/otp/generate \
  -H "Content-Type: application/json"

# Check status
curl http://localhost:5000/otp/status

# Delete session
curl -X DELETE http://localhost:5000/otp/session \
  -H "Content-Type: application/json"

# Health check
curl http://localhost:5000/health
```

### Using Python requests

```python
import requests

API_URL = "http://localhost:5000"

# Setup
response = requests.post(f"{API_URL}/otp/setup", json={
    "sms_code": "123456",
    "pin_code": "1234"
})
print(response.json())
# {'status': 'success', 'device_id': '...', 'session_file': 'otp.bin'}

# Generate
response = requests.post(f"{API_URL}/otp/generate")
print(response.json())
# {'status': 'success', 'otp_code': 'a3k9m2'}

# Status
response = requests.get(f"{API_URL}/otp/status")
print(response.json())
# {'status': 'success', 'session_exists': True, 'session_file': 'otp.bin'}

# Delete
response = requests.delete(f"{API_URL}/otp/session")
print(response.json())
# {'status': 'success', 'message': 'Session deleted'}
```

### Using Elixir HTTPoison

```elixir
# Setup
{:ok, response} = HTTPoison.post(
  "http://localhost:5000/otp/setup",
  Jason.encode!(%{sms_code: "123456", pin_code: "1234"}),
  [{"Content-Type", "application/json"}]
)

{:ok, body} = Jason.decode(response.body)
# %{"status" => "success", "device_id" => "...", "session_file" => "otp.bin"}

# Generate
{:ok, response} = HTTPoison.post(
  "http://localhost:5000/otp/generate",
  "{}",
  [{"Content-Type", "application/json"}]
)

{:ok, body} = Jason.decode(response.body)
# %{"status" => "success", "otp_code" => "a3k9m2"}
```

## Configuration

Environment variables:

- `API_HOST` - Server host (default: `0.0.0.0`)
- `API_PORT` - Server port (default: `5000`)
- `API_DEBUG` - Debug mode (default: `false`)
- `OTP_SESSION_FILE` - Session file path (default: `otp.bin`)

Example:

```bash
export API_HOST=127.0.0.1
export API_PORT=8080
export API_DEBUG=true
export OTP_SESSION_FILE=/data/otp.bin
python app.py
```

## Project Structure

```
psa_otp_api/
├── app.py                 # Flask REST API application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── otp_module/           # OTP implementation
│   ├── __init__.py
│   ├── otp.py           # Main OTP logic
│   ├── load.py          # Session data
│   ├── tokenizer.py     # Token parser
│   └── oaep.py          # Encryption
└── otp.bin              # Session file (created at runtime)
```

## Error Handling

All endpoints return consistent JSON responses:

**Success:**
```json
{
  "status": "success",
  ...
}
```

**Error:**
```json
{
  "status": "error",
  "error": "Error description"
}
```

### Common Errors

| HTTP Code | Error | Cause |
|-----------|-------|-------|
| 400 | `sms_code is required` | Missing SMS code in request |
| 400 | `pin_code must be numeric` | PIN is not digits only |
| 400 | `Configuration error` | Invalid SMS code or expired |
| 404 | `Session file not found` | No OTP session, run setup first |
| 500 | `Failed to create OTP session` | Network or API error |
| 500 | `Failed to generate OTP code` | Network or API error |

## Rate Limits

PSA enforces these limits:
- **6 OTP codes per 24 hours** (per account)
- Implement rate limiting in your application

Example rate limit tracking:

```python
# In your Elixir/Python app
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    def __init__(self, max_calls=6, period_hours=24):
        self.max_calls = max_calls
        self.period = timedelta(hours=period_hours)
        self.calls = deque()

    def can_call(self):
        now = datetime.now()
        # Remove old calls
        while self.calls and now - self.calls[0] > self.period:
            self.calls.popleft()
        return len(self.calls) < self.max_calls

    def record_call(self):
        self.calls.append(datetime.now())
```

## Security Considerations

1. **Session File**
   - `otp.bin` contains sensitive encryption keys
   - Set proper file permissions: `chmod 600 otp.bin`
   - Don't expose via web server

2. **API Access**
   - Add authentication (API key, JWT, etc.)
   - Use HTTPS in production
   - Implement rate limiting

3. **Network**
   - Don't expose directly to internet
   - Use reverse proxy (nginx, Apache)
   - Add CORS headers if needed

## Production Deployment

### With Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### With systemd

```ini
[Unit]
Description=PSA OTP API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/psa_otp_api
Environment="PATH=/opt/psa_otp_api/venv/bin"
ExecStart=/opt/psa_otp_api/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### With nginx

```nginx
server {
    listen 80;
    server_name otp-api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Testing

### Manual Testing

```bash
# Start server
python app.py

# In another terminal
# Test health
curl http://localhost:5000/health

# Test setup
curl -X POST http://localhost:5000/otp/setup \
  -H "Content-Type: application/json" \
  -d '{"sms_code":"test","pin_code":"1234"}'

# Test generate
curl -X POST http://localhost:5000/otp/generate
```

### Automated Tests

```python
import unittest
import requests
import json

class TestOTPAPI(unittest.TestCase):
    BASE_URL = "http://localhost:5000"

    def test_health(self):
        r = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "healthy")

    def test_setup(self):
        r = requests.post(
            f"{self.BASE_URL}/otp/setup",
            json={"sms_code": "123456", "pin_code": "1234"}
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("device_id", data)

    def test_generate(self):
        r = requests.post(f"{self.BASE_URL}/otp/generate")
        data = r.json()
        if r.status_code == 200:
            self.assertEqual(data["status"], "success")
            self.assertEqual(len(data["otp_code"]), 6)

if __name__ == "__main__":
    unittest.main()
```

## Troubleshooting

### Server won't start

**Issue:** `Address already in use`
```bash
# Find process using port
lsof -i :5000
# Kill it
kill -9 <PID>
```

**Issue:** `ModuleNotFoundError: No module named 'otp'`
```bash
# Check otp_module directory exists
ls -la otp_module/
# Reinstall dependencies
pip install -r requirements.txt
```

### Session errors

**Issue:** `Session file not found`
- Run `/otp/setup` first to create session

**Issue:** `Configuration error`
- Session expired, run `/otp/setup` again
- Check SMS code is valid

### Network errors

**Issue:** Can't connect to API
```bash
# Check server is running
curl http://localhost:5000/health

# Check firewall
sudo ufw status

# Check logs
journalctl -u psa-otp-api -f
```

## Development

### Running in debug mode

```bash
export API_DEBUG=true
python app.py
```

### Adding new endpoints

```python
@app.route("/otp/info", methods=["GET"])
def otp_info():
    """Get OTP session info"""
    session = load_otp(SESSION_FILE)
    return jsonify({
        "status": "success",
        "device_id": session.device_id if session else None,
        "otp_count": session.otp_count if session else 0
    })
```

## License

Extracted from PSA Car Controller project.

## Support

For issues:
1. Check server logs
2. Verify dependencies installed
3. Test with curl first
4. Check file permissions on `otp.bin`
5. Review PSA rate limits (6 OTP/24h)
