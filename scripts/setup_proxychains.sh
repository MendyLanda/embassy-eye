#!/bin/bash
# Setup proxychains4 configuration from environment variables and run the application
# Proxy configuration is REQUIRED - the application will not run without it

set -e

PROXY_SERVER="${PROXY_SERVER:-}"
PROXY_USERNAME="${PROXY_USERNAME:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

# Validate that PROXY_SERVER is set (required)
if [ -z "$PROXY_SERVER" ]; then
    echo "ERROR: PROXY_SERVER environment variable is required but not set."
    echo "Please set PROXY_SERVER in your .env file or environment."
    echo ""
    echo "Examples:"
    echo "  PROXY_SERVER=socks5://proxy.example.com:1080    (RECOMMENDED - SOCKS5)"
    echo "  PROXY_SERVER=http://proxy.example.com:8080       (HTTP proxy)"
    echo "  PROXY_SERVER=socks4://proxy.example.com:1080    (SOCKS4)"
    exit 1
fi

# Use app-specific proxychains config location (no root permissions needed)
# Use /app/.proxychains which is in the app directory and writable by appuser
PROXYCHAINS_CONF="/app/.proxychains/proxychains.conf"
PROXYCHAINS_DIR="$(dirname "$PROXYCHAINS_CONF")"

echo "Proxy server configured: $PROXY_SERVER"
echo "Setting up proxychains4 configuration..."

# Parse proxy URL
# Support formats: 
#   http://host:port, https://host:port (HTTP proxy)
#   socks5://host:port (SOCKS5 proxy - RECOMMENDED)
#   socks4://host:port (SOCKS4 proxy)
#   http://user:pass@host:port (with credentials in URL)
if [[ "$PROXY_SERVER" =~ ^(http|https|socks5|socks4):// ]]; then
    # Extract scheme
    if [[ "$PROXY_SERVER" =~ ^(socks5):// ]]; then
        PROXY_TYPE="socks5"
        PROXY_URL="${PROXY_SERVER#socks5://}"
    elif [[ "$PROXY_SERVER" =~ ^(socks4):// ]]; then
        PROXY_TYPE="socks4"
        PROXY_URL="${PROXY_SERVER#socks4://}"
    elif [[ "$PROXY_SERVER" =~ ^(https):// ]]; then
        PROXY_TYPE="http"
        PROXY_URL="${PROXY_SERVER#https://}"
        # Note: proxychains4 doesn't support HTTPS proxy directly,
        # but HTTP proxy can handle HTTPS traffic via CONNECT method
    else
        PROXY_TYPE="http"
        PROXY_URL="${PROXY_SERVER#http://}"
    fi
    
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
        # Default port based on proxy type
        case "$PROXY_TYPE" in
            socks5) PROXY_PORT="1080" ;;
            socks4) PROXY_PORT="1080" ;;
            http) PROXY_PORT="8080" ;;
            *) PROXY_PORT="8080" ;;
        esac
        PROXY_HOST="$PROXY_HOST_PORT"
    fi
else
    # Assume format: host:port or just host (defaults to HTTP proxy)
    if [[ "$PROXY_SERVER" =~ ^([^:]+):([0-9]+)$ ]]; then
        PROXY_HOST="${BASH_REMATCH[1]}"
        PROXY_PORT="${BASH_REMATCH[2]}"
    else
        PROXY_HOST="$PROXY_SERVER"
        PROXY_PORT="8080"
    fi
    PROXY_TYPE="http"
    PROXY_USER="$PROXY_USERNAME"
    PROXY_PASS="$PROXY_PASSWORD"
fi

echo "Parsed proxy configuration:"
echo "  Type: $PROXY_TYPE"
echo "  Host: $PROXY_HOST"
echo "  Port: $PROXY_PORT"
if [ -n "$PROXY_USER" ]; then
    echo "  Username: $PROXY_USER"
    echo "  Password: ***"
fi

# Resolve hostname to IP address
# NOTE: proxychains4 requires numeric IP addresses in the proxy list, not hostnames.
# DNS resolution happens at RUNTIME (every container start), not build time, so IPs are fresh each run.
# If the proxy IP changes, it will be re-resolved on the next container start.
PROXY_IP="$PROXY_HOST"
if ! [[ "$PROXY_HOST" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Resolving hostname $PROXY_HOST to IP address (runtime resolution, not cached)..."
    # Try to resolve hostname using getent (most reliable)
    if command -v getent >/dev/null 2>&1; then
        RESOLVED_IP=$(getent hosts "$PROXY_HOST" | awk '{print $1; exit}' 2>/dev/null)
    fi
    
    # Fallback to host command
    if [ -z "$RESOLVED_IP" ] && command -v host >/dev/null 2>&1; then
        RESOLVED_IP=$(host "$PROXY_HOST" 2>/dev/null | grep -oP 'has address \K[0-9.]+' | head -1)
    fi
    
    # Fallback to nslookup
    if [ -z "$RESOLVED_IP" ] && command -v nslookup >/dev/null 2>&1; then
        RESOLVED_IP=$(nslookup "$PROXY_HOST" 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -1)
    fi
    
    if [ -n "$RESOLVED_IP" ]; then
        PROXY_IP="$RESOLVED_IP"
        echo "  ✓ Resolved to IP: $PROXY_IP (this resolution happens fresh on every container start)"
    else
        echo "  ✗ ERROR: Could not resolve hostname to IP address."
        echo "  Proxychains4 requires numeric IP addresses in the proxy list."
        echo "  Please either:"
        echo "    1. Use an IP address directly in PROXY_SERVER (e.g., socks5://1.2.3.4:1080)"
        echo "    2. Ensure DNS resolution is available in the container"
        exit 1
    fi
fi

# Create proxychains config directory if it doesn't exist
mkdir -p "$PROXYCHAINS_DIR"

# Backup original config if it exists and hasn't been backed up
if [ -f "$PROXYCHAINS_CONF" ] && [ ! -f "${PROXYCHAINS_CONF}.original" ]; then
    cp "$PROXYCHAINS_CONF" "${PROXYCHAINS_CONF}.original"
fi

# Create proxychains configuration
cat > "$PROXYCHAINS_CONF" <<EOF
# proxychains4 configuration
# Generated automatically from environment variables

# strict_chain - Each connection will be done via chained proxies
# all proxies in the chain must be online to play the chain
# otherwise EINTR is returned to the app
strict_chain

# Quiet mode (no output from library)
quiet_mode

# Proxy DNS requests - no leak for DNS data
proxy_dns

# Some timeouts in milliseconds
tcp_read_time_out 15000
tcp_connect_time_out 8000

# ProxyList format
#       type  host  port [user pass]
#       (values separated by 'tab' or 'blank')
#
#        Examples:
#
#            	socks5	192.168.67.78	1080	lamer	secret
#		http	192.168.89.3	8080	justu	hidden
#	 	socks4	192.168.1.49	1080
#		http	192.168.39.93	8080
#
#       proxy types: http, socks4, socks5
#
[ProxyList]
EOF

# Add proxy entry (use resolved IP address)
if [ -n "$PROXY_USER" ] && [ -n "$PROXY_PASS" ]; then
    echo -e "${PROXY_TYPE}\t${PROXY_IP}\t${PROXY_PORT}\t${PROXY_USER}\t${PROXY_PASS}" >> "$PROXYCHAINS_CONF"
else
    echo -e "${PROXY_TYPE}\t${PROXY_IP}\t${PROXY_PORT}" >> "$PROXYCHAINS_CONF"
fi
    
echo "Proxychains4 configuration created at $PROXYCHAINS_CONF"
echo "Running application with proxychains4..."

# Set environment variable to indicate system-level proxy is being used
export USE_SYSTEM_PROXY=true

# Run with proxychains4 using custom config file
exec proxychains4 -f "$PROXYCHAINS_CONF" python fill_form.py "$@"
