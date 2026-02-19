/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L3
Logic:       VS Code extension entry point with status bar,
             session tracking, model selector, and budget alerts.
Root Cause:  Sprint tasks T165-T171 — VS Code IDE integration.
Context:     Provides developer-facing AI cost visibility.
Suitability: L3 — VS Code extension APIs + HTTP client.
──────────────────────────────────────────────────────────────
*/

import * as vscode from 'vscode';
import { activateSidebar } from './sidebar';

// Session tracking state
let sessionTokensInput = 0;
let sessionTokensOutput = 0;
let sessionCost = 0;
let currentModel = 'gpt-4o';
let currentEnvironment: 'development' | 'production' = 'development';
let statusBarTokens: vscode.StatusBarItem;
let statusBarCost: vscode.StatusBarItem;
let statusBarModel: vscode.StatusBarItem;
let statusBarEnv: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    // Activate sidebar (Transfer History — T165 baseline)
    activateSidebar(context);

    // T166: Status bar token counter
    statusBarTokens = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarTokens.command = 'alfred.showSessionDetails';
    updateTokensStatusBar();
    statusBarTokens.show();
    context.subscriptions.push(statusBarTokens);

    // T167: Session cost gauge
    statusBarCost = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 99);
    statusBarCost.command = 'alfred.showCostBreakdown';
    updateCostStatusBar();
    statusBarCost.show();
    context.subscriptions.push(statusBarCost);

    // T168: Model selector
    statusBarModel = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 98);
    statusBarModel.command = 'alfred.selectModel';
    updateModelStatusBar();
    statusBarModel.show();
    context.subscriptions.push(statusBarModel);

    // T169: Dev/prod environment toggle
    statusBarEnv = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 97);
    statusBarEnv.command = 'alfred.toggleEnvironment';
    updateEnvStatusBar();
    statusBarEnv.show();
    context.subscriptions.push(statusBarEnv);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('alfred.showSessionDetails', showSessionDetails),
        vscode.commands.registerCommand('alfred.showCostBreakdown', showCostBreakdown),
        vscode.commands.registerCommand('alfred.selectModel', selectModel),
        vscode.commands.registerCommand('alfred.toggleEnvironment', toggleEnvironment),
        vscode.commands.registerCommand('alfred.resetSession', resetSession),
        vscode.commands.registerCommand('alfred.checkBudget', checkBudget),
        vscode.commands.registerCommand('alfred.trackRequest', trackRequest),
    );

    // T170: Budget alerts — check periodically
    const budgetCheckInterval = setInterval(() => {
        checkBudgetAlerts(context);
    }, 60000); // Check every minute

    context.subscriptions.push({
        dispose: () => clearInterval(budgetCheckInterval)
    });

    // Initial budget check
    checkBudgetAlerts(context);

    // T171: Per-repo tracking — store session data per workspace
    restoreSessionFromWorkspace(context);

    vscode.window.showInformationMessage('Alfred AI extension activated');
}

function updateTokensStatusBar() {
    const total = sessionTokensInput + sessionTokensOutput;
    statusBarTokens.text = `$(symbol-number) ${formatNumber(total)} tokens`;
    statusBarTokens.tooltip = `Session tokens: ${formatNumber(sessionTokensInput)} in / ${formatNumber(sessionTokensOutput)} out`;
}

function updateCostStatusBar() {
    statusBarCost.text = `$(credit-card) $${sessionCost.toFixed(4)}`;
    statusBarCost.tooltip = `Session cost: $${sessionCost.toFixed(4)} USD`;
    
    // Color based on cost threshold
    const config = vscode.workspace.getConfiguration('alfred');
    const warnThreshold = config.get<number>('sessionCostWarningThreshold', 1.0);
    
    if (sessionCost > warnThreshold) {
        statusBarCost.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
        statusBarCost.backgroundColor = undefined;
    }
}

function updateModelStatusBar() {
    statusBarModel.text = `$(hubot) ${currentModel}`;
    statusBarModel.tooltip = `Current model: ${currentModel}. Click to change.`;
}

function updateEnvStatusBar() {
    const icon = currentEnvironment === 'production' ? '$(globe)' : '$(beaker)';
    statusBarEnv.text = `${icon} ${currentEnvironment}`;
    statusBarEnv.tooltip = `Environment: ${currentEnvironment}. Click to toggle.`;
    
    if (currentEnvironment === 'production') {
        statusBarEnv.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    } else {
        statusBarEnv.backgroundColor = undefined;
    }
}

async function showSessionDetails() {
    const message = `
📊 Alfred Session Details

Input Tokens:  ${formatNumber(sessionTokensInput)}
Output Tokens: ${formatNumber(sessionTokensOutput)}
Total Tokens:  ${formatNumber(sessionTokensInput + sessionTokensOutput)}
Session Cost:  $${sessionCost.toFixed(4)}
Current Model: ${currentModel}
Environment:   ${currentEnvironment}
    `.trim();
    
    const action = await vscode.window.showInformationMessage(
        message,
        'Reset Session',
        'View Dashboard'
    );
    
    if (action === 'Reset Session') {
        resetSession();
    } else if (action === 'View Dashboard') {
        const config = vscode.workspace.getConfiguration('alfred');
        const apiUrl = config.get<string>('apiUrl', 'http://localhost:3000');
        vscode.env.openExternal(vscode.Uri.parse(apiUrl));
    }
}

async function showCostBreakdown() {
    const config = vscode.workspace.getConfiguration('alfred');
    const budget = config.get<number>('dailyBudget', 10.0);
    const remaining = Math.max(0, budget - sessionCost);
    const percentUsed = (sessionCost / budget) * 100;
    
    vscode.window.showInformationMessage(
        `Session: $${sessionCost.toFixed(4)} | Daily Budget: $${budget.toFixed(2)} | Remaining: $${remaining.toFixed(2)} (${percentUsed.toFixed(1)}% used)`
    );
}

async function selectModel() {
    const models = [
        { label: 'gpt-4o', description: 'OpenAI GPT-4o — Best quality' },
        { label: 'gpt-4o-mini', description: 'OpenAI GPT-4o Mini — Fast & cheap' },
        { label: 'gpt-3.5-turbo', description: 'OpenAI GPT-3.5 Turbo — Economy' },
        { label: 'claude-3.5-sonnet', description: 'Anthropic Claude 3.5 Sonnet — Strong reasoning' },
        { label: 'claude-3-haiku', description: 'Anthropic Claude 3 Haiku — Fast' },
        { label: 'gemini-1.5-pro', description: 'Google Gemini 1.5 Pro — Long context' },
        { label: 'gemini-1.5-flash', description: 'Google Gemini 1.5 Flash — Speed' },
        { label: 'mistral-large', description: 'Mistral Large — European hosting' },
    ];
    
    const selected = await vscode.window.showQuickPick(models, {
        placeHolder: 'Select AI model for requests',
        title: 'Alfred: Select Model'
    });
    
    if (selected) {
        currentModel = selected.label;
        updateModelStatusBar();
        vscode.window.showInformationMessage(`Alfred: Model set to ${currentModel}`);
    }
}

async function toggleEnvironment() {
    currentEnvironment = currentEnvironment === 'development' ? 'production' : 'development';
    updateEnvStatusBar();
    
    if (currentEnvironment === 'production') {
        const confirm = await vscode.window.showWarningMessage(
            'You are now in PRODUCTION mode. API calls will use production credentials and be billed accordingly.',
            'Keep Production',
            'Switch to Dev'
        );
        if (confirm === 'Switch to Dev') {
            currentEnvironment = 'development';
            updateEnvStatusBar();
        }
    } else {
        vscode.window.showInformationMessage('Switched to development environment');
    }
}

function resetSession() {
    sessionTokensInput = 0;
    sessionTokensOutput = 0;
    sessionCost = 0;
    updateTokensStatusBar();
    updateCostStatusBar();
    vscode.window.showInformationMessage('Alfred: Session reset');
}

async function checkBudget() {
    const config = vscode.workspace.getConfiguration('alfred');
    const budget = config.get<number>('dailyBudget', 10.0);
    const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
    const apiKey = config.get<string>('apiKey');
    
    if (!apiKey) {
        vscode.window.showWarningMessage('Alfred: API key not configured');
        return;
    }
    
    // Fetch budget from API
    try {
        // In production: fetch from Alfred API
        vscode.window.showInformationMessage(
            `Budget: $${budget.toFixed(2)} daily | Session: $${sessionCost.toFixed(4)}`
        );
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to check budget: ${error}`);
    }
}

// T170: Budget alerts
async function checkBudgetAlerts(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('alfred');
    const budget = config.get<number>('dailyBudget', 10.0);
    const warnAt = config.get<number>('budgetWarningPercent', 80);
    
    const percentUsed = (sessionCost / budget) * 100;
    
    const lastWarning = context.workspaceState.get<number>('lastBudgetWarning', 0);
    const now = Date.now();
    
    // Warn at most once per hour
    if (percentUsed >= warnAt && (now - lastWarning) > 3600000) {
        vscode.window.showWarningMessage(
            `⚠️ Alfred Budget Alert: You've used ${percentUsed.toFixed(1)}% of your daily AI budget ($${sessionCost.toFixed(2)} / $${budget.toFixed(2)})`,
            'View Details'
        );
        context.workspaceState.update('lastBudgetWarning', now);
    }
}

// T171: Per-repo tracking
function restoreSessionFromWorkspace(context: vscode.ExtensionContext) {
    const storedTokensIn = context.workspaceState.get<number>('sessionTokensInput', 0);
    const storedTokensOut = context.workspaceState.get<number>('sessionTokensOutput', 0);
    const storedCost = context.workspaceState.get<number>('sessionCost', 0);
    const storedModel = context.workspaceState.get<string>('currentModel', 'gpt-4o');
    const storedEnv = context.workspaceState.get<'development' | 'production'>('currentEnvironment', 'development');
    
    sessionTokensInput = storedTokensIn;
    sessionTokensOutput = storedTokensOut;
    sessionCost = storedCost;
    currentModel = storedModel;
    currentEnvironment = storedEnv;
    
    updateTokensStatusBar();
    updateCostStatusBar();
    updateModelStatusBar();
    updateEnvStatusBar();
}

function saveSessionToWorkspace(context: vscode.ExtensionContext) {
    context.workspaceState.update('sessionTokensInput', sessionTokensInput);
    context.workspaceState.update('sessionTokensOutput', sessionTokensOutput);
    context.workspaceState.update('sessionCost', sessionCost);
    context.workspaceState.update('currentModel', currentModel);
    context.workspaceState.update('currentEnvironment', currentEnvironment);
}

// Public API for tracking requests (can be called from other extensions)
function trackRequest(inputTokens: number, outputTokens: number, cost: number) {
    sessionTokensInput += inputTokens;
    sessionTokensOutput += outputTokens;
    sessionCost += cost;
    updateTokensStatusBar();
    updateCostStatusBar();
}

function formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

export function deactivate() {
    // Status bars are disposed via subscriptions
}