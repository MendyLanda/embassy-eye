#!/bin/bash
# Setup proxychains4 configuration from environment variables and run the application

set -e

PROXY_SERVER="${PROXY_SERVER:-}"
PROXY_USERNAME="${PROXY_USERNAME:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

# Use app-specific proxychains config location (no root permissions needed)
# Use /app/.proxychains which is in the app directory and writable by appuser
PROXYCHAINS_CONF="/app/.proxychains/proxychains.conf"
PROXYCHAINS_DIR="$(dirname "$PROXYCHAINS_CONF")"

if [ -n "$PROXY_SERVER" ]; then
    echo "Proxy server configured: $PROXY_SERVER"
    echo "Setting up proxychains4 configuration..."
    
    # Parse proxy URL
    # Support formats: http://host:port, https://host:port, http://user:pass@host:port
    if [[ "$PROXY_SERVER" =~ ^https?:// ]]; then
        # Extract scheme, host, port
        PROXY_URL="${PROXY_SERVER#http://}"
        PROXY_URL="${PROXY_URL#https://}"
        
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
            # Default port based on scheme
            if [[ "$PROXY_SERVER" =~ ^https:// ]]; then
                PROXY_PORT="443"
            else
                PROXY_PORT="8080"
            fi
            PROXY_HOST="$PROXY_HOST_PORT"
        fi
        
        # Determine proxy type (http or https)
        if [[ "$PROXY_SERVER" =~ ^https:// ]]; then
            PROXY_TYPE="http"
            # Note: proxychains4 doesn't support HTTPS proxy directly, 
            # but HTTP proxy can handle HTTPS traffic
        else
            PROXY_TYPE="http"
        fi
    else
        # Assume format: host:port or just host
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
    
    # Add proxy entry
    if [ -n "$PROXY_USER" ] && [ -n "$PROXY_PASS" ]; then
        echo -e "${PROXY_TYPE}\t${PROXY_HOST}\t${PROXY_PORT}\t${PROXY_USER}\t${PROXY_PASS}" >> "$PROXYCHAINS_CONF"
    else
        echo -e "${PROXY_TYPE}\t${PROXY_HOST}\t${PROXY_PORT}" >> "$PROXYCHAINS_CONF"
    fi
    
    echo "Proxychains4 configuration created at $PROXYCHAINS_CONF"
    echo "Running application with proxychains4..."
    
    # Set environment variable to indicate system-level proxy is being used
    export USE_SYSTEM_PROXY=true
    
    # Run with proxychains4 using custom config file
    exec proxychains4 -f "$PROXYCHAINS_CONF" python fill_form.py "$@"
else
    echo "No proxy server configured (PROXY_SERVER not set)"
    echo "Running application without proxychains4..."
    
    # Run without proxychains
    exec python fill_form.py "$@"
fi
