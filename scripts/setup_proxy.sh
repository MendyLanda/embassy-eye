#!/bin/bash
# Setup 3proxy configuration from environment variables
# This script generates the 3proxy config file that forwards to the external SOCKS5 proxy

set -e

PROXY_SERVER="${PROXY_SERVER:-}"
PROXY_USERNAME="${PROXY_USERNAME:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

# Validate that PROXY_SERVER is set (required)
if [ -z "$PROXY_SERVER" ]; then
    echo "ERROR: PROXY_SERVER environment variable is required but not set."
    echo "Please set PROXY_SERVER in your .env file or environment."
    exit 1
fi

PROXY_CONF="/etc/3proxy/3proxy.cfg"

# Parse proxy URL
# Support formats: 
#   socks5://host:port (SOCKS5 proxy - RECOMMENDED)
#   socks5://user:pass@host:port (with credentials in URL)
if [[ "$PROXY_SERVER" =~ ^socks5:// ]]; then
    PROXY_URL="${PROXY_SERVER#socks5://}"
    
    # Check if credentials are in URL
    if [[ "$PROXY_URL" =~ ^([^:]+):([^@]+)@(.+)$ ]]; then
        PROXY_USER="${BASH_REMATCH[1]}"
        PROXY_PASS="${BASH_REMATCH[2]}"
        PROXY_HOST_PORT="${BASH_REMATCH[3]}"
    elif [ -n "$PROXY_USERNAME" ] && [ -n "$PROXY_PASSWORD" ]; then
        PROXY_USER="$PROXY_USERNAME"
        PROXY_PASS="$PROXY_PASSWORD"
        PROXY_HOST_PORT="$PROXY_URL"
    else
        PROXY_USER=""
        PROXY_PASS=""
        PROXY_HOST_PORT="$PROXY_URL"
    fi
    
    # Extract host and port
    if [[ "$PROXY_HOST_PORT" =~ ^([^:]+):([0-9]+)$ ]]; then
        PROXY_HOST="${BASH_REMATCH[1]}"
        PROXY_PORT="${BASH_REMATCH[2]}"
    else
        PROXY_PORT="1080"
        PROXY_HOST="$PROXY_HOST_PORT"
    fi
else
    echo "ERROR: Only SOCKS5 proxies are supported (socks5://host:port)"
    exit 1
fi

echo "Proxy configuration:"
echo "  External proxy: socks5://${PROXY_HOST}:${PROXY_PORT}"
if [ -n "$PROXY_USER" ]; then
    echo "  Username: $PROXY_USER"
    echo "  Password: ***"
fi

# Generate 3proxy configuration
# 3proxy will listen on port 3128 (HTTP proxy) and forward to the external SOCKS5 proxy
cat > "$PROXY_CONF" <<EOF
# 3proxy configuration
# Generated automatically from environment variables

# Logging
log

# Authentication (none - we're forwarding to authenticated upstream)
# Allow all connections from the Docker network
allow

# SOCKS5 parent proxy configuration
# This forwards all HTTP/HTTPS traffic to the external SOCKS5 proxy
parent 1000 socks5 ${PROXY_HOST} ${PROXY_PORT}
EOF

# Add authentication if credentials are provided
if [ -n "$PROXY_USER" ] && [ -n "$PROXY_PASS" ]; then
    cat >> "$PROXY_CONF" <<EOF
parent 1000 socks5 ${PROXY_HOST} ${PROXY_PORT} ${PROXY_USER} ${PROXY_PASS}
EOF
fi

cat >> "$PROXY_CONF" <<EOF

# HTTP proxy on port 3128 (accessible from Docker network)
proxy -p3128

# SOCKS5 proxy on port 1080 (optional, for direct SOCKS5 access)
socks -p1080
EOF

echo "3proxy configuration created at $PROXY_CONF"
echo "Proxy service will forward traffic to: socks5://${PROXY_HOST}:${PROXY_PORT}"
