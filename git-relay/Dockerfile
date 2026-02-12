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
const https = require('https');
const { URL } = require('url');

const PORT = process.env.PORT || 8080;
const RELAY_URL = process.env.RELAY_URL || '';

function relayWebhook(body, headers) {
    if (!RELAY_URL) {
        return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
        try {
            const url = new URL(RELAY_URL);
            const protocol = url.protocol === 'https:' ? https : http;
            
            const options = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(body)
                }
            };

            const req = protocol.request(options, (res) => {
                res.on('data', () => {});
                res.on('end', () => {
                    console.log(`Webhook relayed successfully (status: ${res.statusCode})`);
                    resolve();
                });
            });

            req.on('error', (error) => {
                console.error('Failed to relay webhook:', error.message);
                reject(error);
            });

            req.write(body);
            req.end();
        } catch (error) {
            console.error('Invalid RELAY_URL:', error.message);
            reject(error);
        }
    });
}

const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/webhook') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });
        
        req.on('end', async () => {
            console.log(`[${new Date().toISOString()}] Webhook received`);
            
            try {
                await relayWebhook(body, req.headers);
            } catch (error) {
                // Error already logged
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
