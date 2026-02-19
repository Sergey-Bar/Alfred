/**
 * [AI GENERATED - GOVERNANCE PROTOCOL]
 * ──────────────────────────────────────────────────────────────
 * Model:       Claude Opus 4.6
 * Tier:        L2
 * Logic:       Node.js SDK for Alfred AI Credit Governance Platform.
 *              Provides typed client for all Alfred API endpoints.
 * Root Cause:  Sprint task T185 — Node.js SDK for developers.
 * Context:     Drop-in replacement for direct API calls with
 *              automatic retries, rate limiting, and TypeScript types.
 * Suitability: L2 — Standard SDK pattern with HTTP client.
 * ──────────────────────────────────────────────────────────────
 */

// ============================================================
// Types
// ============================================================

export interface AlfredConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin' | 'team_admin' | 'super_admin';
  teamId?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt?: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  memberCount: number;
  createdAt: string;
  updatedAt?: string;
}

export interface Wallet {
  id: string;
  ownerId: string;
  ownerType: 'user' | 'team';
  balance: number;
  hardLimit: number;
  softLimit: number;
  currency: string;
  createdAt: string;
  updatedAt?: string;
}

export interface Transaction {
  id: string;
  walletId: string;
  type: 'deduction' | 'refund' | 'credit' | 'transfer_in' | 'transfer_out' | 'chargeback';
  amount: number;
  balanceAfter: number;
  description?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  idempotencyKey?: string;
}

export interface Transfer {
  id: string;
  fromWalletId: string;
  toWalletId: string;
  amount: number;
  message?: string;
  status: 'pending' | 'completed' | 'cancelled' | 'rejected';
  requiresApproval: boolean;
  approvedBy?: string;
  createdAt: string;
  completedAt?: string;
}

export interface APIKey {
  id: string;
  name: string;
  keyPrefix: string;
  userId: string;
  scopes: string[];
  isActive: boolean;
  lastUsedAt?: string;
  expiresAt?: string;
  createdAt: string;
}

export interface Provider {
  id: string;
  name: string;
  type: string;
  isEnabled: boolean;
  priority: number;
  rateLimit?: number;
  models: string[];
  healthStatus: string;
  lastHealthCheck?: string;
}

export interface Policy {
  id: string;
  name: string;
  description?: string;
  rules: Record<string, unknown>;
  action: 'allow' | 'deny' | 'warn' | 'audit';
  isActive: boolean;
  isDryRun: boolean;
  priority: number;
  createdAt: string;
  updatedAt?: string;
}

export interface Experiment {
  id: string;
  name: string;
  description?: string;
  status: 'draft' | 'running' | 'paused' | 'concluded';
  variants: Record<string, unknown>[];
  trafficSplit: Record<string, number>;
  metrics: Record<string, unknown>;
  startTime?: string;
  endTime?: string;
  createdAt: string;
}

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface CompletionOptions {
  model: string;
  messages: Message[];
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  [key: string]: unknown;
}

export interface CompletionResponse {
  id: string;
  model: string;
  choices: Array<{
    index: number;
    message: Message;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  created: number;
  cost?: number;
  cached?: boolean;
}

export interface UsageReport {
  periodStart: string;
  periodEnd: string;
  totalRequests: number;
  totalTokensInput: number;
  totalTokensOutput: number;
  totalCost: number;
  byModel: Array<{ model: string; requests: number; tokens: number; cost: number }>;
  byDay: Array<{ date: string; requests: number; cost: number }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// ============================================================
// Errors
// ============================================================

export class AlfredError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AlfredError';
  }
}

export class AuthenticationError extends AlfredError {
  constructor(message: string, response?: Record<string, unknown>) {
    super(message, 401, response);
    this.name = 'AuthenticationError';
  }
}

export class QuotaExceededError extends AlfredError {
  constructor(
    message: string,
    public currentBalance?: number,
    public required?: number
  ) {
    super(message, 429);
    this.name = 'QuotaExceededError';
  }
}

export class RateLimitError extends AlfredError {
  constructor(message: string, public retryAfter?: number) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

export class ValidationError extends AlfredError {
  constructor(message: string, public errors?: unknown[]) {
    super(message, 422);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AlfredError {
  constructor(message: string) {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

// ============================================================
// Client
// ============================================================

export class AlfredClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly maxRetries: number;

  constructor(config: AlfredConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = (config.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.timeout = config.timeout || 60000;
    this.maxRetries = config.maxRetries || 3;
  }

  // ========================================================
  // Internal HTTP methods
  // ========================================================

  private async request<T>(
    method: string,
    path: string,
    options: {
      params?: Record<string, string | number>;
      body?: unknown;
    } = {}
  ): Promise<T> {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        let url = `${this.baseUrl}${path}`;
        if (options.params) {
          const searchParams = new URLSearchParams();
          for (const [key, value] of Object.entries(options.params)) {
            searchParams.set(key, String(value));
          }
          url += `?${searchParams.toString()}`;
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url, {
          method,
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
            'User-Agent': 'alfred-sdk-node/1.0.0',
          },
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          await this.handleError(response);
        }

        if (response.status === 204) {
          return {} as T;
        }

        return await response.json() as T;
      } catch (error) {
        lastError = error as Error;
        if (!this.shouldRetry(error)) {
          throw error;
        }
        await this.sleep(Math.pow(2, attempt) * 1000);
      }
    }

    throw lastError || new AlfredError('Max retries exceeded');
  }

  private async handleError(response: Response): Promise<never> {
    let data: Record<string, unknown> = {};
    try {
      data = await response.json();
    } catch {
      data = { detail: await response.text() };
    }

    const message = (data.detail || data.message || 'Unknown error') as string;

    switch (response.status) {
      case 401:
        throw new AuthenticationError(message, data);
      case 403:
        throw new AlfredError(message, 403, data);
      case 404:
        throw new NotFoundError(message);
      case 422:
        throw new ValidationError(message, data.errors as unknown[]);
      case 429:
        if (message.toLowerCase().includes('quota') || message.toLowerCase().includes('credit')) {
          throw new QuotaExceededError(message);
        }
        const retryAfter = response.headers.get('Retry-After');
        throw new RateLimitError(message, retryAfter ? parseInt(retryAfter) : undefined);
      default:
        throw new AlfredError(message, response.status, data);
    }
  }

  private shouldRetry(error: unknown): boolean {
    if (error instanceof AlfredError) {
      return error.statusCode !== undefined && [429, 500, 502, 503, 504].includes(error.statusCode);
    }
    return false;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ========================================================
  // User Management
  // ========================================================

  async getMe(): Promise<User> {
    return this.request<User>('GET', '/v1/users/me');
  }

  async updateMe(data: { name?: string }): Promise<User> {
    return this.request<User>('PATCH', '/v1/users/me', { body: data });
  }

  async listUsers(page = 1, pageSize = 20): Promise<PaginatedResponse<User>> {
    return this.request<PaginatedResponse<User>>('GET', '/v1/users', { params: { page, page_size: pageSize } });
  }

  async getUser(userId: string): Promise<User> {
    return this.request<User>('GET', `/v1/users/${userId}`);
  }

  // ========================================================
  // Team Management
  // ========================================================

  async listTeams(page = 1, pageSize = 20): Promise<PaginatedResponse<Team>> {
    return this.request<PaginatedResponse<Team>>('GET', '/v1/teams', { params: { page, page_size: pageSize } });
  }

  async getTeam(teamId: string): Promise<Team> {
    return this.request<Team>('GET', `/v1/teams/${teamId}`);
  }

  async createTeam(data: { name: string; description?: string }): Promise<Team> {
    return this.request<Team>('POST', '/v1/teams', { body: data });
  }

  async addTeamMember(teamId: string, userId: string, role = 'member'): Promise<unknown> {
    return this.request('POST', `/v1/teams/${teamId}/members`, { body: { user_id: userId, role } });
  }

  async removeTeamMember(teamId: string, userId: string): Promise<void> {
    await this.request('DELETE', `/v1/teams/${teamId}/members/${userId}`);
  }

  // ========================================================
  // Wallet & Credits
  // ========================================================

  async getWallet(): Promise<Wallet> {
    return this.request<Wallet>('GET', '/v1/wallets/me');
  }

  async getWalletById(walletId: string): Promise<Wallet> {
    return this.request<Wallet>('GET', `/v1/wallets/${walletId}`);
  }

  async addCredits(walletId: string, amount: number, description?: string): Promise<Transaction> {
    return this.request<Transaction>('POST', `/v1/wallets/${walletId}/credit`, { body: { amount, description } });
  }

  async getTransactions(walletId?: string, page = 1, pageSize = 20): Promise<PaginatedResponse<Transaction>> {
    const path = walletId ? `/v1/wallets/${walletId}/transactions` : '/v1/wallets/me/transactions';
    return this.request<PaginatedResponse<Transaction>>('GET', path, { params: { page, page_size: pageSize } });
  }

  // ========================================================
  // Transfers
  // ========================================================

  async transferCredits(toUserId: string, amount: number, message?: string): Promise<Transfer> {
    return this.request<Transfer>('POST', '/v1/transfers', { body: { to_user_id: toUserId, amount, message } });
  }

  async getTransfers(page = 1, pageSize = 20): Promise<PaginatedResponse<Transfer>> {
    return this.request<PaginatedResponse<Transfer>>('GET', '/v1/transfers', { params: { page, page_size: pageSize } });
  }

  // ========================================================
  // API Keys
  // ========================================================

  async listApiKeys(): Promise<APIKey[]> {
    const data = await this.request<{ items: APIKey[] } | APIKey[]>('GET', '/v1/api-keys');
    return Array.isArray(data) ? data : data.items;
  }

  async createApiKey(data: { name: string; scopes?: string[]; expiresInDays?: number }): Promise<{ key: string; id: string }> {
    return this.request('POST', '/v1/api-keys', { body: { name: data.name, scopes: data.scopes || [], expires_in_days: data.expiresInDays } });
  }

  async revokeApiKey(keyId: string): Promise<void> {
    await this.request('DELETE', `/v1/api-keys/${keyId}`);
  }

  async rotateApiKey(keyId: string): Promise<{ key: string }> {
    return this.request('POST', `/v1/api-keys/${keyId}/rotate`);
  }

  // ========================================================
  // AI Completions
  // ========================================================

  async chatCompletion(options: CompletionOptions): Promise<CompletionResponse> {
    const payload = {
      model: options.model,
      messages: options.messages,
      temperature: options.temperature ?? 0.7,
      max_tokens: options.maxTokens,
      stream: options.stream ?? false,
      ...Object.fromEntries(Object.entries(options).filter(([k]) => !['model', 'messages', 'temperature', 'maxTokens', 'stream'].includes(k))),
    };
    return this.request<CompletionResponse>('POST', '/v1/chat/completions', { body: payload });
  }

  // Streaming requires a different approach — for now, returns async generator placeholder
  async *streamCompletion(options: CompletionOptions): AsyncGenerator<string, void, undefined> {
    const url = `${this.baseUrl}/v1/chat/completions`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ...options, stream: true }),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new AlfredError('Stream not available');

    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          yield data;
        }
      }
    }
  }

  // ========================================================
  // Providers
  // ========================================================

  async listProviders(): Promise<Provider[]> {
    const data = await this.request<{ items: Provider[] } | Provider[]>('GET', '/v1/providers');
    return Array.isArray(data) ? data : data.items;
  }

  async getProviderHealth(): Promise<Record<string, unknown>> {
    return this.request('GET', '/v1/providers/health');
  }

  // ========================================================
  // Policies
  // ========================================================

  async listPolicies(): Promise<Policy[]> {
    const data = await this.request<{ items: Policy[] } | Policy[]>('GET', '/v1/policies');
    return Array.isArray(data) ? data : data.items;
  }

  async getPolicy(policyId: string): Promise<Policy> {
    return this.request<Policy>('GET', `/v1/policies/${policyId}`);
  }

  async createPolicy(data: { name: string; rules: Record<string, unknown>; action?: string; description?: string }): Promise<Policy> {
    return this.request<Policy>('POST', '/v1/policies', { body: data });
  }

  // ========================================================
  // Experiments
  // ========================================================

  async listExperiments(): Promise<Experiment[]> {
    const data = await this.request<{ items: Experiment[] } | Experiment[]>('GET', '/v1/experiments');
    return Array.isArray(data) ? data : data.items;
  }

  async getExperiment(experimentId: string): Promise<Experiment> {
    return this.request<Experiment>('GET', `/v1/experiments/${experimentId}`);
  }

  async createExperiment(data: { name: string; variants: unknown[]; trafficSplit: Record<string, number>; description?: string }): Promise<Experiment> {
    return this.request<Experiment>('POST', '/v1/experiments', { body: { name: data.name, variants: data.variants, traffic_split: data.trafficSplit, description: data.description } });
  }

  async startExperiment(experimentId: string): Promise<Experiment> {
    return this.request<Experiment>('POST', `/v1/experiments/${experimentId}/start`);
  }

  async concludeExperiment(experimentId: string, winner: string): Promise<Experiment> {
    return this.request<Experiment>('POST', `/v1/experiments/${experimentId}/conclude`, { body: { winner } });
  }

  // ========================================================
  // Analytics
  // ========================================================

  async getUsageReport(startDate?: string, endDate?: string): Promise<UsageReport> {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.request<UsageReport>('GET', '/v1/analytics/usage/me', { params });
  }
}

export default AlfredClient;
