# Local Testing Guide

This guide shows you how to build and run the embassy-eye application locally using Docker to simulate server runs.

## Prerequisites

- Docker Desktop installed and running
- `.env` file configured with your credentials and proxy settings

## Step 1: Configure Environment Variables

Make sure your `.env` file has all required variables:

```bash
# Required: Proxy configuration (SOCKS5 recommended)
PROXY_SERVER=socks5://your-proxy.com:1080
PROXY_USERNAME=your_proxy_user
PROXY_PASSWORD=your_proxy_pass

# Required: Telegram configuration
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id

# Optional: Hungary scraper settings
HUNGARY_HEADLESS=true

# Optional: Italy scraper settings (if testing Italy)
ITALY_EMAIL=your_email@example.com
ITALY_PASSWORD=your_password
ITALY_HEADLESS=true
```

## Step 2: Build Docker Image

### Option A: Using the build script (recommended - only rebuilds if needed)
```bash
./build_docker.sh
```

### Option B: Force rebuild
```bash
docker compose build
```

### Option C: Build without cache (clean build)
```bash
docker compose build --no-cache
```

**Note:** First build may take 5-10 minutes as it downloads Chrome and installs dependencies.

## Step 3: Run the Application

### Run Hungary Scraper (Default)

```bash
# Run with default settings (Tel Aviv location)
docker compose run --rm embassy-eye hungary

# Run checking both locations
docker compose run --rm embassy-eye hungary both

# Run specific location
docker compose run --rm embassy-eye hungary tel_aviv
docker compose run --rm embassy-eye hungary subotica
docker compose run --rm embassy-eye hungary belgrade
```

### Run Italy Scraper

```bash
docker compose run --rm embassy-eye italy
```

**Note:** The `--rm` flag automatically removes the container after it finishes.

## Step 4: View Logs

### View logs in real-time (while running)
```bash
# In another terminal, get container name first
docker ps

# Then tail logs
docker logs -f embassy-eye
```

### View logs after container exits
```bash
docker compose logs embassy-eye
```

## Step 5: Run in Background (Detached Mode)

```bash
# Start container in background
docker compose up -d embassy-eye

# View logs
docker logs -f embassy-eye

# Stop container
docker compose stop embassy-eye
docker compose rm -f embassy-eye
```

## Important Notes for macOS Users

⚠️ **Network Mode Issue:** The `docker-compose.yml` uses `network_mode: "host"` which **doesn't work on macOS**. 

### Fix for macOS:

1. **Option 1: Comment out network_mode (Recommended for local testing)**
   
   Edit `docker-compose.yml` and comment out line 9:
   ```yaml
   # network_mode: "host"
   ```
   
   Then rebuild and run:
   ```bash
   docker compose build
   docker compose run --rm embassy-eye hungary
   ```

2. **Option 2: Use bridge network (Default Docker network)**
   
   The container will work fine without `network_mode: "host"` - it just won't share the host's network stack. This is fine for testing.

## Testing Different Scenarios

### Test Proxy Configuration

```bash
# Test with SOCKS5 proxy
PROXY_SERVER=socks5://proxy.example.com:1080 docker compose run --rm embassy-eye hungary

# Test with HTTP proxy
PROXY_SERVER=http://proxy.example.com:8080 docker compose run --rm embassy-eye hungary
```

### Test Headless vs Interactive Mode

```bash
# Headless mode (default for Docker)
HUNGARY_HEADLESS=true docker compose run --rm embassy-eye hungary

# Interactive mode (for debugging - requires X11 forwarding on Linux)
HUNGARY_HEADLESS=false docker compose run --rm embassy-eye hungary
```

### Test Specific Locations (Hungary)

```bash
# Test Tel Aviv only (default)
docker compose run --rm embassy-eye hungary tel_aviv

# Test Subotica only
docker compose run --rm embassy-eye hungary subotica

# Test Belgrade only
docker compose run --rm embassy-eye hungary belgrade

# Test both locations
docker compose run --rm embassy-eye hungary both
```

## Troubleshooting

### Container fails to start - "PROXY_SERVER not set"
- Make sure `.env` file exists and has `PROXY_SERVER` set
- Check: `cat .env | grep PROXY_SERVER`

### Proxy connection fails
- Verify proxy credentials are correct
- Test proxy manually: `curl -x socks5://user:pass@proxy:port https://api.ipify.org`
- Check proxy logs in container: `docker logs embassy-eye`

### Chrome/ChromeDriver issues
- Rebuild image: `docker compose build --no-cache`
- Check Chrome version: `docker compose run --rm embassy-eye google-chrome --version`

### Network connectivity issues on macOS
- Comment out `network_mode: "host"` in `docker-compose.yml`
- Rebuild: `docker compose build`

### View container shell for debugging
```bash
# Run interactive shell in container
docker compose run --rm embassy-eye /bin/bash

# Inside container, you can test:
# - Check proxy: echo $PROXY_SERVER
# - Test proxychains: proxychains4 curl https://api.ipify.org
# - Run Python directly: python fill_form.py hungary
```

## Clean Up

```bash
# Stop and remove containers
docker compose down

# Remove images
docker rmi embassy-eye_embassy-eye

# Remove volumes (if any)
docker volume prune
```

## Quick Reference Commands

```bash
# Build
./build_docker.sh

# Run Hungary scraper (defaults to Tel Aviv)
docker compose run --rm embassy-eye hungary

# Run Hungary scraper checking both locations
docker compose run --rm embassy-eye hungary both

# Run Italy scraper  
docker compose run --rm embassy-eye italy

# View logs
docker logs -f embassy-eye

# Clean up
docker compose down
```

## Simulating Server Environment

To exactly simulate server runs:

1. **Use headless mode** (default in Docker)
2. **Use proxy** (required - always uses proxychains)
3. **Run detached** for background execution:
   ```bash
   docker compose up -d embassy-eye
   docker logs -f embassy-eye
   ```
4. **Check exit codes**:
   ```bash
   docker compose ps
   # Exit code 0 = success
   # Exit code 2 = IP blocked (Hungary scraper)
   ```

## Next Steps

Once local testing works:
- Deploy to server using `DEPLOYMENT.md` guide
- Set up cron scheduling using `CRON_SETUP.md`
- Monitor logs and Telegram notifications
