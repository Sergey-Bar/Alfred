/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       k6 load testing suite for Alfred gateway.
             Tests chat completions, embeddings, health,
             and wallet operations at 10K req/min target.
Root Cause:  Sprint task T199 — Load testing suite.
Context:     Validates P95 < 150ms gateway overhead target.
Suitability: L2 — standard k6 scripting pattern.
──────────────────────────────────────────────────────────────
*/

import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';

// ─── Custom Metrics ─────────────────────────────────────────

const errorRate = new Rate('alfred_error_rate');
const gatewayLatency = new Trend('alfred_gateway_latency_ms', true);
const tokensProcessed = new Counter('alfred_tokens_processed');
const cacheHitRate = new Rate('alfred_cache_hit_rate');
const walletCheckLatency = new Trend('alfred_wallet_check_latency_ms', true);

// ─── Configuration ──────────────────────────────────────────

const BASE_URL = __ENV.ALFRED_BASE_URL || 'http://localhost:8080';
const API_KEY = __ENV.ALFRED_API_KEY || 'test-api-key-load-test';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_KEY}`,
};

// ─── Scenarios ──────────────────────────────────────────────

export const options = {
  scenarios: {
    // Scenario 1: Ramp to 10K req/min (~167 req/s)
    sustained_load: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 500,
      stages: [
        { duration: '30s', target: 50 },   // Warm up
        { duration: '1m', target: 100 },   // Ramp
        { duration: '2m', target: 167 },   // 10K req/min
        { duration: '3m', target: 167 },   // Sustain
        { duration: '30s', target: 0 },    // Cool down
      ],
    },

    // Scenario 2: Spike test (sudden 3x burst)
    spike_test: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 300,
      maxVUs: 600,
      stages: [
        { duration: '1m', target: 50 },    // Baseline
        { duration: '10s', target: 500 },   // Spike to 30K/min
        { duration: '30s', target: 500 },   // Hold spike
        { duration: '10s', target: 50 },    // Back to normal
        { duration: '1m', target: 50 },     // Recovery
      ],
      startTime: '7m30s',  // After sustained load finishes
    },
  },

  thresholds: {
    // Primary SLA targets
    'http_req_duration{type:chat}': ['p(95)<5000'],       // Provider response can be slow
    'alfred_gateway_latency_ms': ['p(95)<150'],           // Gateway overhead must be < 150ms
    'alfred_error_rate': ['rate<0.01'],                    // < 1% error rate
    'http_req_failed': ['rate<0.05'],                      // < 5% HTTP failures
    'alfred_wallet_check_latency_ms': ['p(95)<50'],       // Wallet checks must be fast

    // Per-scenario
    'http_req_duration{scenario:sustained_load}': ['p(95)<10000'],
    'http_req_duration{scenario:spike_test}': ['p(95)<15000'],
  },
};

// ─── Test Data ──────────────────────────────────────────────

const CHAT_PROMPTS = [
  'Explain quantum computing in simple terms',
  'Write a Python function to sort a list',
  'What is the capital of France?',
  'Summarize the theory of relativity',
  'How do neural networks work?',
  'Write a haiku about programming',
  'Explain REST APIs to a beginner',
  'What are design patterns in software?',
  'Compare SQL and NoSQL databases',
  'How does HTTPS encryption work?',
];

const MODELS = [
  'gpt-4o-mini',
  'gpt-4o',
  'claude-3-5-sonnet-20241022',
  'claude-3-haiku-20240307',
];

const EMBEDDING_TEXTS = [
  'Machine learning is a subset of artificial intelligence',
  'The weather today is sunny and warm',
  'Enterprise software requires careful architecture',
];

// ─── Helper Functions ───────────────────────────────────────

function randomItem(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function recordGatewayLatency(res) {
  const gwLatency = res.headers['X-Alfred-Gateway-Latency'];
  if (gwLatency) {
    gatewayLatency.add(parseFloat(gwLatency));
  }

  const cacheHit = res.headers['X-Alfred-Cache-Hit'];
  if (cacheHit !== undefined) {
    cacheHitRate.add(cacheHit === 'true');
  }
}

// ─── Main Test Function ─────────────────────────────────────

export default function () {
  // Weighted distribution: 60% chat, 15% embeddings, 15% health, 10% wallet
  const roll = Math.random();

  if (roll < 0.60) {
    testChatCompletion();
  } else if (roll < 0.75) {
    testEmbeddings();
  } else if (roll < 0.90) {
    testHealthEndpoints();
  } else {
    testWalletOperations();
  }

  sleep(0.1); // Small pause between iterations
}

// ─── Test: Chat Completions ─────────────────────────────────

function testChatCompletion() {
  group('Chat Completions', function () {
    const payload = JSON.stringify({
      model: randomItem(MODELS),
      messages: [
        { role: 'user', content: randomItem(CHAT_PROMPTS) },
      ],
      max_tokens: 100,
      temperature: 0.7,
    });

    const res = http.post(
      `${BASE_URL}/v1/chat/completions`,
      payload,
      {
        headers: headers,
        tags: { type: 'chat' },
        timeout: '30s',
      }
    );

    check(res, {
      'chat: status is 200': (r) => r.status === 200,
      'chat: has choices': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.choices && body.choices.length > 0;
        } catch { return false; }
      },
      'chat: has usage': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.usage && body.usage.total_tokens > 0;
        } catch { return false; }
      },
    });

    errorRate.add(res.status !== 200);
    recordGatewayLatency(res);

    if (res.status === 200) {
      try {
        const body = JSON.parse(res.body);
        if (body.usage) {
          tokensProcessed.add(body.usage.total_tokens);
        }
      } catch { /* ignore */ }
    }
  });
}

// ─── Test: Embeddings ───────────────────────────────────────

function testEmbeddings() {
  group('Embeddings', function () {
    const payload = JSON.stringify({
      model: 'text-embedding-3-small',
      input: randomItem(EMBEDDING_TEXTS),
    });

    const res = http.post(
      `${BASE_URL}/v1/embeddings`,
      payload,
      {
        headers: headers,
        tags: { type: 'embeddings' },
        timeout: '15s',
      }
    );

    check(res, {
      'embed: status is 200': (r) => r.status === 200,
      'embed: has data': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.data && body.data.length > 0;
        } catch { return false; }
      },
    });

    errorRate.add(res.status !== 200);
    recordGatewayLatency(res);
  });
}

// ─── Test: Health Endpoints ─────────────────────────────────

function testHealthEndpoints() {
  group('Health Checks', function () {
    // Liveness
    const liveness = http.get(`${BASE_URL}/health`, {
      tags: { type: 'health' },
      timeout: '5s',
    });
    check(liveness, {
      'health: liveness 200': (r) => r.status === 200,
    });

    // Provider health
    const providers = http.get(`${BASE_URL}/v1/providers`, {
      headers: headers,
      tags: { type: 'providers' },
      timeout: '5s',
    });
    check(providers, {
      'providers: status 200': (r) => r.status === 200,
    });

    // Models list
    const models = http.get(`${BASE_URL}/v1/models`, {
      headers: headers,
      tags: { type: 'models' },
      timeout: '5s',
    });
    check(models, {
      'models: status 200': (r) => r.status === 200,
    });

    errorRate.add(liveness.status !== 200);
  });
}

// ─── Test: Wallet Operations ────────────────────────────────

function testWalletOperations() {
  group('Wallet Operations', function () {
    const start = Date.now();

    const res = http.get(`${BASE_URL}/v1/wallet/balance`, {
      headers: headers,
      tags: { type: 'wallet' },
      timeout: '5s',
    });

    const elapsed = Date.now() - start;
    walletCheckLatency.add(elapsed);

    check(res, {
      'wallet: status is 200 or 404': (r) => r.status === 200 || r.status === 404,
    });

    errorRate.add(res.status >= 500);
  });
}

// ─── Teardown ───────────────────────────────────────────────

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    scenarios: Object.keys(options.scenarios),
    thresholds: {},
    metrics: {},
  };

  // Collect threshold pass/fail
  for (const [name, threshold] of Object.entries(data.root_group ? {} : data.metrics || {})) {
    if (threshold.thresholds) {
      summary.thresholds[name] = threshold.thresholds;
    }
  }

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'qa/results/load_test_report.json': JSON.stringify(summary, null, 2),
  };
}

// k6 built-in text summary helper
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.3/index.js';
