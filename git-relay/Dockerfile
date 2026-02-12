# Git relay image
# Acts as a webhook relay for git events

FROM node:20-alpine

LABEL org.opencontainers.image.source=https://github.com/triimd/images
LABEL org.opencontainers.image.description="Git relay for webhook events"
LABEL org.opencontainers.image.licenses=MIT

# Install git and required tools
RUN apk add --no-cache \
    git \
    bash \
    curl

# Create relay script
COPY <<'EOF' /usr/local/bin/git-relay.js
#!/usr/bin/env node

const http = require('http');
const { execSync } = require('child_process');

const PORT = process.env.PORT || 8080;
const RELAY_URL = process.env.RELAY_URL || '';

const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/webhook') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });
        
        req.on('end', () => {
            console.log(`[${new Date().toISOString()}] Webhook received`);
            
            if (RELAY_URL) {
                try {
                    execSync(`curl -X POST -H "Content-Type: application/json" -d '${body}' ${RELAY_URL}`, {
                        stdio: 'inherit'
                    });
                    console.log('Webhook relayed successfully');
                } catch (error) {
                    console.error('Failed to relay webhook:', error.message);
                }
            }
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ status: 'received' }));
        });
    } else if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy' }));
    } else {
        res.writeHead(404);
        res.end();
    }
});

server.listen(PORT, () => {
    console.log(`Git relay server listening on port ${PORT}`);
    if (RELAY_URL) {
        console.log(`Relaying to: ${RELAY_URL}`);
    }
});
EOF

RUN chmod +x /usr/local/bin/git-relay.js

WORKDIR /app

EXPOSE 8080

CMD ["/usr/local/bin/git-relay.js"]
