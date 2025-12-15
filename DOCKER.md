# Docker Setup for PSA Car Controller

This document explains how to run PSA Car Controller using Docker.

---

## 🚀 Quick Start

### Development Mode (with hot reload)

Run both the Flask backend and SvelteKit frontend with live reload:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

**Access the app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

**Features:**
- ✨ Hot reload for both frontend and backend
- 🔄 Code changes reflect immediately
- 📦 Separate containers for frontend and backend
- 🐛 Better for development and debugging

---

### Production Mode (optimized build)

Run the complete app in a single optimized container:

```bash
docker-compose -f docker-compose.prod.yml up --build
```

**Access the app:**
- Full app: http://localhost:5000

**Features:**
- 📦 Single container with built frontend
- ⚡ Optimized for performance
- 🔒 Production-ready configuration
- 🚀 Smaller image size

---

## 📋 Available Docker Compose Files

| File | Purpose | Use Case |
|------|---------|----------|
| `docker-compose.yml` | Legacy production (uses published image) | Quick start with official image |
| `docker-compose.dev.yml` | **Development** | Active development with hot reload |
| `docker-compose.prod.yml` | **Production** | Optimized build for deployment |

---

## 🛠️ Development Workflow

### 1. Start Development Environment

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. Making Changes

**Frontend changes:**
- Edit files in `frontend/src/`
- Changes auto-reload in browser (HMR)

**Backend changes:**
- Edit files in `psa_car_controller/`
- Flask auto-reloads on code changes

### 3. Stop Services

```bash
# Stop and remove containers
docker-compose -f docker-compose.dev.yml down

# Stop, remove, and clean volumes
docker-compose -f docker-compose.dev.yml down -v
```

---

## 📦 Production Deployment

### Build Production Image

```bash
# Build the production image
docker-compose -f docker-compose.prod.yml build

# Run production container
docker-compose -f docker-compose.prod.yml up -d
```

### What Happens in Production Build:

1. **Frontend:**
   - SvelteKit app is built (`npm run build`)
   - Static files optimized and bundled
   - Output placed in `frontend/build/`

2. **Backend:**
   - Python dependencies installed
   - Built frontend copied into container
   - Flask serves static files + API

3. **Result:**
   - Single container serving everything
   - One port (5000) for entire app
   - Smaller, faster, production-ready

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Backend
PSACC_PORT=5000
PSACC_HOST=0.0.0.0
PSACC_CONFIG_DIR=/config

# SvelteKit Frontend (dev only)
VITE_API_URL=http://localhost:5000
```

### Volumes

**Development:**
- Source code mounted for hot reload
- Config directory: `./config:/config`
- Database persists in `./config/`

**Production:**
- Only config directory mounted
- Application code baked into image

---

## 🐳 Docker Commands Reference

### View Running Containers

```bash
docker ps
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.dev.yml logs

# Specific service
docker-compose -f docker-compose.dev.yml logs frontend
docker-compose -f docker-compose.dev.yml logs backend

# Follow logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.dev.yml restart

# Restart specific service
docker-compose -f docker-compose.dev.yml restart frontend
```

### Execute Commands in Container

```bash
# Open shell in backend container
docker exec -it psacc-backend /bin/bash

# Open shell in frontend container
docker exec -it psacc-frontend /bin/sh

# Run Python command
docker exec psacc-backend python -c "print('Hello')"
```

### Clean Up

```bash
# Remove stopped containers
docker-compose -f docker-compose.dev.yml down

# Remove containers and volumes
docker-compose -f docker-compose.dev.yml down -v

# Remove containers, volumes, and images
docker-compose -f docker-compose.dev.yml down -v --rmi all

# Clean all Docker resources (use with caution!)
docker system prune -a
```

---

## 🔍 Troubleshooting

### Port Already in Use

If port 5000 or 5173 is already in use:

```bash
# Find process using port
lsof -i :5000
lsof -i :5173

# Kill the process
kill -9 <PID>

# Or change port in docker-compose file
```

### Container Won't Start

```bash
# View detailed logs
docker-compose -f docker-compose.dev.yml logs

# Rebuild from scratch
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

### Frontend Can't Connect to Backend

1. Check backend is running: http://localhost:5000/get_vehicles
2. Verify `VITE_API_URL` in frontend environment
3. Check CORS settings in Flask backend

### Database/Config Issues

```bash
# Reset database (delete and recreate)
rm -rf ./config/psa_car_controller.db
docker-compose -f docker-compose.dev.yml restart backend
```

---

## 🏗️ Architecture

### Development Mode

```
┌─────────────────────────────────────────┐
│         Docker Network (psacc)          │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │    │   Backend    │  │
│  │  (Node.js)   │    │   (Python)   │  │
│  │  Port: 5173  │────│  Port: 5000  │  │
│  │   Vite Dev   │    │    Flask     │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
└─────────┼────────────────────┼──────────┘
          │                    │
     Host: 5173           Host: 5000
```

### Production Mode

```
┌──────────────────────────────────────┐
│     Single Docker Container          │
│                                      │
│  ┌────────────────────────────────┐ │
│  │      Flask Backend             │ │
│  │      Port: 5000                │ │
│  │                                │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  SvelteKit Build (static)│ │ │
│  │  │  Served by Flask         │ │ │
│  │  └──────────────────────────┘ │ │
│  └────────────────────────────────┘ │
│                 │                    │
└─────────────────┼────────────────────┘
                  │
            Host: 5000
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SvelteKit Deployment](https://kit.svelte.dev/docs/adapter-node)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

## 🎯 Best Practices

1. **Development:**
   - Always use `docker-compose.dev.yml` for development
   - Keep containers running for fast iteration
   - Use `docker-compose logs -f` to debug issues

2. **Production:**
   - Build with `--no-cache` for clean builds
   - Test production build locally before deploying
   - Use health checks for monitoring

3. **Resource Management:**
   - Stop containers when not in use
   - Regularly clean up unused images and volumes
   - Monitor container resource usage

---

**Happy Coding! 🚀**
