import * as vscode from 'vscode';

export function activateSidebar(context: vscode.ExtensionContext) {
    const viewType = 'alfredSidebar';

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(viewType, new SidebarProvider(context))
    );
}

class SidebarProvider implements vscode.WebviewViewProvider {
    private readonly context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    resolveWebviewView(webviewView: vscode.WebviewView) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.context.extensionUri]
        };

        webviewView.webview.html = this.getHtmlContent();
    }

    private getHtmlContent(): string {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Alfred Sidebar</title>
            </head>
            <body>
                <h1>Welcome to Alfred Sidebar</h1>
                <p>View your transfer history, approvals, and efficiency ranking here.</p>
            </body>
            </html>
        `;
    }
}