"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activateSidebar = void 0;
const vscode = __importStar(require("vscode"));
const https = require('https');
const http = require('http');
function activateSidebar(context) {
    const viewType = 'alfredSidebar';
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(viewType, new SidebarProvider(context)));
    // Register refresh command
    context.subscriptions.push(vscode.commands.registerCommand('alfred.refreshTransferHistory', () => {
        // Find the active webview and refresh it
        // This will be handled by the provider
    }));
}
exports.activateSidebar = activateSidebar;
class SidebarProvider {
    constructor(context) {
        this.context = context;
    }
    resolveWebviewView(webviewView) {
        this.webviewView = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.context.extensionUri]
        };
        webviewView.webview.html = this.getHtmlContent();
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'refresh':
                    await this.refreshTransferHistory();
                    break;
                case 'error':
                    vscode.window.showErrorMessage(`Alfred: ${message.message}`);
                    break;
            }
        }, undefined, this.context.subscriptions);
        // Initial load
        this.refreshTransferHistory();
    }
    async refreshTransferHistory() {
        if (!this.webviewView)
            return;
        try {
            const config = vscode.workspace.getConfiguration('alfred');
            const apiUrl = config.get('apiUrl', 'http://localhost:8000');
            const apiKey = config.get('apiKey');
            if (!apiKey) {
                this.webviewView.webview.postMessage({
                    type: 'error',
                    message: 'API key not configured. Please set alfred.apiKey in settings.'
                });
                return;
            }
            const url = new URL(`${apiUrl}/v1/governance/users/me/transfers`);
            const data = await this.makeHttpRequest(url, apiKey);
            this.webviewView.webview.postMessage({
                type: 'transfers',
                data: data.transfers || []
            });
        }
        catch (error) {
            this.webviewView.webview.postMessage({
                type: 'error',
                message: error instanceof Error ? error.message : 'Unknown error occurred'
            });
        }
    }
    async makeHttpRequest(url, apiKey) {
        return new Promise((resolve, reject) => {
            const isHttps = url.protocol === 'https:';
            const client = isHttps ? https : http;
            const options = {
                hostname: url.hostname,
                port: url.port || (isHttps ? 443 : 80),
                path: url.pathname + url.search,
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'Alfred-VSCode-Extension/1.0'
                }
            };
            const req = client.request(options, (res) => {
                let body = '';
                res.on('data', (chunk) => {
                    body += chunk;
                });
                res.on('end', () => {
                    if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
                        try {
                            resolve(JSON.parse(body));
                        }
                        catch (e) {
                            reject(new Error('Invalid JSON response'));
                        }
                    }
                    else {
                        reject(new Error(`HTTP ${res.statusCode}: ${body}`));
                    }
                });
            });
            req.on('error', (err) => {
                reject(err);
            });
            req.setTimeout(10000, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
            req.end();
        });
    }
    getHtmlContent() {
        const nonce = getNonce();
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
                <title>Alfred Transfer History</title>
                <style>
                    body {
                        font-family: var(--vscode-font-family);
                        font-size: var(--vscode-font-size);
                        background-color: var(--vscode-editor-background);
                        color: var(--vscode-editor-foreground);
                        margin: 0;
                        padding: 10px;
                    }
                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 10px;
                    }
                    .title {
                        font-weight: bold;
                        font-size: 1.1em;
                    }
                    .refresh-btn {
                        background: none;
                        border: none;
                        color: var(--vscode-foreground);
                        cursor: pointer;
                        padding: 2px;
                    }
                    .refresh-btn:hover {
                        color: var(--vscode-textLink-foreground);
                    }
                    .transfer-item {
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 3px;
                        padding: 8px;
                        margin-bottom: 8px;
                        background-color: var(--vscode-input-background);
                    }
                    .transfer-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 4px;
                    }
                    .transfer-type {
                        font-weight: bold;
                        padding: 2px 6px;
                        border-radius: 3px;
                        font-size: 0.9em;
                    }
                    .transfer-type.sent {
                        background-color: var(--vscode-notificationsErrorIcon-foreground);
                        color: white;
                    }
                    .transfer-type.received {
                        background-color: var(--vscode-notificationsInfoIcon-foreground);
                        color: white;
                    }
                    .transfer-amount {
                        font-weight: bold;
                        color: var(--vscode-textLink-foreground);
                    }
                    .transfer-user {
                        color: var(--vscode-descriptionForeground);
                        font-size: 0.9em;
                    }
                    .transfer-message {
                        margin-top: 4px;
                        font-style: italic;
                        color: var(--vscode-descriptionForeground);
                    }
                    .transfer-timestamp {
                        font-size: 0.8em;
                        color: var(--vscode-descriptionForeground);
                        margin-top: 4px;
                    }
                    .loading {
                        text-align: center;
                        padding: 20px;
                        color: var(--vscode-descriptionForeground);
                    }
                    .error {
                        color: var(--vscode-notificationsErrorIcon-foreground);
                        padding: 10px;
                        border: 1px solid var(--vscode-notificationsErrorIcon-foreground);
                        border-radius: 3px;
                        margin-bottom: 10px;
                    }
                    .empty {
                        text-align: center;
                        padding: 20px;
                        color: var(--vscode-descriptionForeground);
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">Transfer History</div>
                    <button class="refresh-btn" onclick="refresh()" title="Refresh">
                        &#x21bb;
                    </button>
                </div>
                <div id="content">
                    <div class="loading">Loading transfer history...</div>
                </div>
                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    let transfers = [];

                    function refresh() {
                        vscode.postMessage({ type: 'refresh' });
                        document.getElementById('content').innerHTML = '<div class="loading">Loading transfer history...</div>';
                    }

                    function formatTimestamp(timestamp) {
                        const date = new Date(timestamp);
                        return date.toLocaleString();
                    }

                    function formatAmount(amount) {
                        return parseFloat(amount).toFixed(2);
                    }

                    function renderTransfers(transferData) {
                        if (!transferData || transferData.length === 0) {
                            return '<div class="empty">No transfers found</div>';
                        }

                        return transferData.map(transfer => \`
                            <div class="transfer-item">
                                <div class="transfer-header">
                                    <span class="transfer-type \${transfer.type}">\${transfer.type.toUpperCase()}</span>
                                    <span class="transfer-amount">\${formatAmount(transfer.amount)} credits</span>
                                </div>
                                <div class="transfer-user">\${transfer.other_user.name} (\${transfer.other_user.email})</div>
                                \${transfer.message ? \`<div class="transfer-message">\${transfer.message}</div>\` : ''}
                                <div class="transfer-timestamp">\${formatTimestamp(transfer.timestamp)}</div>
                            </div>
                        \`).join('');
                    }

                    function renderError(message) {
                        return \`<div class="error">\${message}</div>\`;
                    }

                    window.addEventListener('message', event => {
                        const message = event.data;
                        const content = document.getElementById('content');

                        switch (message.type) {
                            case 'transfers':
                                content.innerHTML = renderTransfers(message.data);
                                break;
                            case 'error':
                                content.innerHTML = renderError(message.message);
                                break;
                        }
                    });

                    // Initial load
                    refresh();
                </script>
            </body>
            </html>
        `;
    }
}
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=sidebar.js.map