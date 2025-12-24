#!/bin/sh
# Generate 3proxy configuration file from environment variables
# This script is run inside the proxy container to generate the config dynamically
# Uses POSIX-compliant shell syntax for maximum compatibility

set -e

PROXY_SERVER="${PROXY_SERVER:-}"
PROXY_USERNAME="${PROXY_USERNAME:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

# Validate that PROXY_SERVER is set (required)
if [ -z "$PROXY_SERVER" ]; then
    echo "ERROR: PROXY_SERVER environment variable is required but not set."
    exit 1
fi

PROXY_CONF="/etc/3proxy/3proxy.cfg"

# Parse proxy URL
# Support formats: 
#   socks5://host:port (SOCKS5 proxy - RECOMMENDED)
#   socks5://user:pass@host:port (with credentials in URL)
PROXY_URL="${PROXY_SERVER#socks5://}"

# Check if it starts with socks5://
case "$PROXY_SERVER" in
    socks5://*)
        ;;
    *)
        echo "ERROR: Only SOCKS5 proxies are supported (socks5://host:port)"
        exit 1
        ;;
esac

# Extract credentials and host:port
# Try to match user:pass@host:port pattern
case "$PROXY_URL" in
    *@*)
        # Has credentials in URL
        PROXY_USER_PASS="${PROXY_URL%%@*}"
        PROXY_HOST_PORT="${PROXY_URL#*@}"
        PROXY_USER="${PROXY_USER_PASS%%:*}"
        PROXY_PASS="${PROXY_USER_PASS#*:}"
        ;;
    *)
        # No credentials in URL, check environment variables
        PROXY_HOST_PORT="$PROXY_URL"
        if [ -n "$PROXY_USERNAME" ] && [ -n "$PROXY_PASSWORD" ]; then
            PROXY_USER="$PROXY_USERNAME"
            PROXY_PASS="$PROXY_PASSWORD"
        else
            PROXY_USER=""
            PROXY_PASS=""
        fi
        ;;
esac

# Extract host and port
case "$PROXY_HOST_PORT" in
    *:*)
        PROXY_HOST="${PROXY_HOST_PORT%%:*}"
        PROXY_PORT="${PROXY_HOST_PORT#*:}"
        ;;
    *)
        PROXY_HOST="$PROXY_HOST_PORT"
        PROXY_PORT="1080"
        ;;
esac

echo "Generating 3proxy configuration..."
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
EOF

# Add authentication if credentials are provided
if [ -n "$PROXY_USER" ] && [ -n "$PROXY_PASS" ]; then
    cat >> "$PROXY_CONF" <<EOF
parent 1000 socks5 ${PROXY_HOST} ${PROXY_PORT} ${PROXY_USER} ${PROXY_PASS}
EOF
else
    cat >> "$PROXY_CONF" <<EOF
parent 1000 socks5 ${PROXY_HOST} ${PROXY_PORT}
EOF
fi

cat >> "$PROXY_CONF" <<EOF

# HTTP proxy on port 3128 (accessible from Docker network)
proxy -p3128

# SOCKS5 proxy on port 1080 (optional, for direct SOCKS5 access)
socks -p1080
EOF

echo "3proxy configuration created at $PROXY_CONF"
echo "Starting 3proxy..."

# Execute 3proxy with the generated config
exec 3proxy "$PROXY_CONF"
