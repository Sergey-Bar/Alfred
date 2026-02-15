#!/bin/bash

# Script to implement security headers and Content Security Policy (CSP) in frontend and API

# Define security headers
SECURITY_HEADERS="\
    add_header X-Content-Type-Options \"nosniff\";\
    add_header X-Frame-Options \"DENY\";\
    add_header X-XSS-Protection \"1; mode=block\";\
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains; preload\";\
    add_header Content-Security-Policy \"default-src 'self'; script-src 'self'; object-src 'none';\";\
"

# Apply headers to Nginx configuration
NGINX_CONF="/etc/nginx/sites-available/default"
if grep -q "add_header" $NGINX_CONF; then
    echo "Security headers already configured in Nginx."
else
    echo "Configuring security headers in Nginx..."
    sudo sed -i "/server_name _;/a $SECURITY_HEADERS" $NGINX_CONF
    sudo systemctl reload nginx
    echo "Security headers applied."
fi

# Apply headers to API (example for Express.js)
API_FILE="../dev/app/middleware/securityHeaders.js"
if [ ! -f $API_FILE ]; then
    echo "Creating middleware for security headers in Express.js..."
    cat <<EOL > $API_FILE
const helmet = require('helmet');

module.exports = function (app) {
    app.use(helmet());
    app.use(helmet.contentSecurityPolicy({
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'"]
        }
    }));
};
EOL
    echo "Middleware created."
else
    echo "Security headers middleware already exists."
fi

echo "Security headers and CSP setup complete."