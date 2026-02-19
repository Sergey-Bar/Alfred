# AI Orchestrator — UI/UX Design & Development Specification

**Product:** AI Orchestrator — Enterprise AI Control & Economy Platform
**Document Type:** UI/UX Master Spec for AI-Assisted Development
**Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Recharts
**Last Updated:** February 2026
**Reference Docs:** AI_Orchestrator_PRD_MASTER.md, AI_Orchestrator_TASKS.md

---

## How to Use This Document

This file is the single source of truth for every screen, component, interaction, and design decision in AI Orchestrator's dashboard. Each section maps directly to a feature in the PRD. When building any screen:

1. Read the **Screen Goal** — what job does this screen do for the user?
2. Read the **User Type** — who is looking at this?
3. Follow the **Layout Spec** — exact component placement
4. Follow the **Data Requirements** — what API calls are needed
5. Follow the **States** — empty, loading, error, success must all be designed
6. Follow the **Interactions** — every click, hover, and transition

---

## Table of Contents

1. [Design System](#1-design-system)
2. [Layout & Navigation](#2-layout--navigation)
3. [Authentication Screens](#3-authentication-screens)
4. [Onboarding Flow](#4-onboarding-flow)
5. [Dashboard — Home](#5-dashboard--home)
6. [Cost Analytics](#6-cost-analytics)
7. [Wallet Management](#7-wallet-management)
8. [Routing Rules](#8-routing-rules)
9. [Security & Policies](#9-security--policies)
10. [Audit Log](#10-audit-log)
11. [Prompt Registry](#11-prompt-registry)
12. [Provider Management](#12-provider-management)
13. [Team & User Management](#13-team--user-management)
14. [API Key Management](#14-api-key-management)
15. [Notifications & Alerts](#15-notifications--alerts)
16. [Experiments](#16-experiments)
17. [Settings](#17-settings)
18. [Admin / Super-Admin Panel](#18-admin--super-admin-panel)
19. [Shared Components Library](#19-shared-components-library)
20. [Empty States](#20-empty-states)
21. [Mobile Responsiveness](#21-mobile-responsiveness)
22. [Accessibility Requirements](#22-accessibility-requirements)
23. [Performance Requirements](#23-performance-requirements)
24. [AI-Specific UX Patterns](#24-ai-specific-ux-patterns)

---

## 1. Design System

### 1.1 Brand Identity

```
Product Name:   AI Orchestrator
Tagline:        Control. Optimize. Govern.
Personality:    Precise, trustworthy, powerful — not playful
Aesthetic:      Enterprise-grade; like Datadog + Linear had a child
Avoid:          Candy colors, rounded blobs, consumer-app vibes
```

### 1.2 Color Palette

```css
/* Primary Brand */
--color-primary-900: #0F172A;   /* Darkest navy — main headings */
--color-primary-800: #1E293B;   /* Dark slate — sidebar bg */
--color-primary-700: #334155;   /* Medium slate — secondary text */
--color-primary-600: #475569;   /* Muted — tertiary text */
--color-primary-500: #64748B;   /* Placeholder text */
--color-primary-400: #94A3B8;   /* Disabled elements */
--color-primary-100: #F1F5F9;   /* Page background */
--color-primary-50:  #F8FAFC;   /* Card background */

/* Accent Blue — CTAs, links, active states */
--color-accent-700: #1D4ED8;
--color-accent-600: #2563EB;    /* Primary button */
--color-accent-500: #3B82F6;    /* Hover state */
--color-accent-100: #DBEAFE;    /* Accent background */
--color-accent-50:  #EFF6FF;    /* Subtle accent bg */

/* Success Green — savings, OK status, positive metrics */
--color-success-700: #15803D;
--color-success-600: #16A34A;
--color-success-100: #DCFCE7;
--color-success-50:  #F0FDF4;

/* Warning Orange — soft limit alerts, caution states */
--color-warning-700: #B45309;
--color-warning-600: #D97706;
--color-warning-100: #FEF3C7;
--color-warning-50:  #FFFBEB;

/* Danger Red — hard limit breach, errors, blocks */
--color-danger-700:  #B91C1C;
--color-danger-600:  #DC2626;
--color-danger-100:  #FEE2E2;
--color-danger-50:   #FEF2F2;

/* Neutral */
--color-white:       #FFFFFF;
--color-border:      #E2E8F0;   /* All borders */
--color-border-dark: #CBD5E1;   /* Focused borders */
```

### 1.3 Typography

```css
/* Font Stack */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;

/* Scale */
--text-xs:   0.75rem  / 1rem;     /* 12px — labels, badges */
--text-sm:   0.875rem / 1.25rem;  /* 14px — table rows, secondary */
--text-base: 1rem     / 1.5rem;   /* 16px — body text */
--text-lg:   1.125rem / 1.75rem;  /* 18px — card titles */
--text-xl:   1.25rem  / 1.75rem;  /* 20px — section headers */
--text-2xl:  1.5rem   / 2rem;     /* 24px — page headers */
--text-3xl:  1.875rem / 2.25rem;  /* 30px — dashboard hero metrics */
--text-4xl:  2.25rem  / 2.5rem;   /* 36px — big numbers */

/* Weights */
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
```

### 1.4 Spacing System

```
Base unit: 4px
Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96

Use Tailwind classes:
p-1 (4px), p-2 (8px), p-3 (12px), p-4 (16px), p-5 (20px),
p-6 (24px), p-8 (32px), p-10 (40px), p-12 (48px), p-16 (64px)
```

### 1.5 Border Radius

```
Buttons:       rounded-md   (6px)
Cards:         rounded-xl   (12px)
Badges:        rounded-full
Inputs:        rounded-md   (6px)
Modals:        rounded-2xl  (16px)
Large panels:  rounded-2xl  (16px)
```

### 1.6 Shadow System

```css
--shadow-sm:  0 1px 2px rgba(0,0,0,0.05);          /* subtle card lift */
--shadow-md:  0 4px 6px -1px rgba(0,0,0,0.07);     /* cards */
--shadow-lg:  0 10px 15px -3px rgba(0,0,0,0.08);   /* modals, dropdowns */
--shadow-xl:  0 20px 25px -5px rgba(0,0,0,0.1);    /* tooltips on dark bg */
```

### 1.7 Component Library

**Base:** shadcn/ui (https://ui.shadcn.com)
**Charts:** Recharts
**Icons:** Lucide React
**Tables:** TanStack Table v8
**Forms:** React Hook Form + Zod
**Toasts:** sonner
**Dates:** date-fns
**Code Editor:** Monaco Editor (for policy + prompt editing)
**Animations:** Framer Motion (use sparingly — enterprise, not playful)

### 1.8 Icon Usage Guidelines

```
Use Lucide React exclusively. Key icons:

Navigation:
  LayoutDashboard    → Home/Dashboard
  TrendingUp         → Analytics/Cost
  Wallet             → Wallets/Budget
  GitBranch          → Routing Rules
  ShieldCheck        → Security
  ScrollText         → Audit Log
  FileText           → Prompt Registry
  Plug               → Providers
  Users              → Team Management
  Key                → API Keys
  Bell               → Notifications
  FlaskConical       → Experiments
  Settings           → Settings

Status/State:
  CheckCircle2       → Success/Active
  XCircle            → Error/Blocked
  AlertTriangle      → Warning
  AlertCircle        → Info
  Clock              → Pending
  Zap                → Fast/Optimized
  Lock               → Secure/Restricted
  Unlock             → Accessible

Actions:
  Plus               → Create
  Pencil             → Edit
  Trash2             → Delete
  Download           → Export
  Upload             → Import
  RefreshCw          → Refresh/Retry
  Copy               → Copy to clipboard
  ExternalLink       → Open in new tab
  ChevronRight       → Expand / navigate
  MoreHorizontal     → More actions menu

Metrics:
  DollarSign         → Cost
  ArrowTrendingDown  → Savings / decrease
  ArrowTrendingUp    → Increase / concern
  Cpu                → Tokens / compute
  Timer              → Latency
  Activity           → Live / real-time
  Database           → Cache / storage
```

### 1.9 Status Color System

```
ALWAYS use these mappings consistently across the entire app:

healthy / active / approved / success  → green  (--color-success-*)
warning / soft-limit / degraded        → orange (--color-warning-*)
error / blocked / hard-limit / denied  → red    (--color-danger-*)
pending / in-progress / loading        → blue   (--color-accent-*)
inactive / disabled / unknown          → gray   (--color-primary-400)
```

---

## 2. Layout & Navigation

### 2.1 Global Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  TOPBAR (height: 56px, sticky)                              │
│  [Logo] [Breadcrumb]              [Search] [Notif] [Avatar] │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  SIDEBAR     │  MAIN CONTENT AREA                           │
│  (width:     │  (flex-1, overflow-y: scroll)                │
│   240px,     │                                              │
│   fixed)     │  ┌──────────────────────────────────────┐   │
│              │  │  PAGE HEADER                         │   │
│              │  │  Title + subtitle + action buttons   │   │
│              │  └──────────────────────────────────────┘   │
│              │                                              │
│              │  ┌──────────────────────────────────────┐   │
│              │  │  PAGE CONTENT                        │   │
│              │  │  (padding: 24px)                     │   │
│              │  └──────────────────────────────────────┘   │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### 2.2 Sidebar Specification

```
Width:       240px (collapsed: 56px with icon-only mode)
Background:  --color-primary-800  (#1E293B)
Border:      1px solid rgba(255,255,255,0.06) on right

LOGO AREA (height: 56px):
  [Orchestrator icon 28px] "AI Orchestrator"
  Font: 15px semibold, color: white

NAVIGATION GROUPS:

  ── OVERVIEW ──────────────────────
  Dashboard               /
  Cost Analytics          /analytics/cost

  ── CONTROL ───────────────────────
  Wallets & Budget        /wallets
  Routing Rules           /routing
  Experiments             /experiments

  ── SECURITY ──────────────────────
  Security & Policies     /security
  Audit Log               /audit

  ── PRODUCT ───────────────────────
  Prompt Registry         /prompts
  Providers               /providers

  ── ADMIN ─────────────────────────
  Team Management         /team
  API Keys                /keys
  Notifications           /notifications
  Settings                /settings

ACTIVE STATE:
  Background: rgba(255,255,255,0.08)
  Left border: 2px solid --color-accent-500
  Icon + text: white (vs default: --color-primary-400)

HOVER STATE:
  Background: rgba(255,255,255,0.04)
  Icon + text: --color-primary-200

BOTTOM OF SIDEBAR:
  [Organization name + plan badge]
  [User avatar + name + role]
```

### 2.3 Topbar Specification

```
Height:     56px
Background: white
Border:     1px solid --color-border on bottom
Position:   sticky top-0, z-index: 50

LEFT:   Organization breadcrumb (e.g., "Acme Corp > Platform Team")
CENTER: Global search (Cmd+K shortcut, opens command palette)
RIGHT:  
  - Notification bell (badge count for unread alerts)
  - "Upgrade" button (if on free plan)
  - Avatar dropdown (Profile, Switch org, Docs, Logout)
```

### 2.4 Page Header Pattern

```
Every page follows this header structure:

┌─────────────────────────────────────────────────────────────┐
│  [Icon] Page Title                    [Secondary] [Primary] │
│  Subtitle explaining what this page does                    │
│  [optional: date range picker] [optional: filter chips]     │
└─────────────────────────────────────────────────────────────┘

Example — Cost Analytics:
  [TrendingUp] Cost Analytics          [Export CSV] [Configure]
  Track AI spend across teams, models, and features
  [Last 30 days ▼] [All teams ▼] [All models ▼]
```

### 2.5 Responsive Breakpoints

```
Mobile:   < 768px   (sidebar hidden, hamburger menu)
Tablet:   768–1024px (sidebar collapsed to icons)
Desktop:  > 1024px  (full sidebar)
Wide:     > 1440px  (max-width: 1400px, centered)
```

---

## 3. Authentication Screens

### 3.1 Sign In Page

```
Route: /auth/signin
Layout: Full-page (no sidebar)

┌─────────────────────────────────────────────────────────────┐
│                     [Left Panel 50%]                        │
│                                                             │
│    [AI Orchestrator Logo + Name]                            │
│                                                             │
│    "The enterprise AI control plane"                        │
│                                                             │
│    ┌──────────────────────────────────┐                     │
│    │  Sign in to your organization    │                     │
│    │                                  │                     │
│    │  [Continue with Okta SSO  ↗]    │                     │
│    │  [Continue with Google    G]    │                     │
│    │  [Continue with Microsoft ⊞]    │                     │
│    │                                  │                     │
│    │  ───────── or ─────────          │                     │
│    │                                  │                     │
│    │  Email address                   │                     │
│    │  [_________________________]     │                     │
│    │                                  │                     │
│    │  Password                        │                     │
│    │  [_________________________] 👁  │                     │
│    │                                  │                     │
│    │  [      Sign In      ]           │                     │
│    │                                  │                     │
│    │  Forgot password? · Sign up      │                     │
│    └──────────────────────────────────┘                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     [Right Panel 50%]                       │
│                                                             │
│    Background: --color-primary-800                          │
│    Show: rotating customer quotes / key stats               │
│                                                             │
│    "Reduced AI spend by 43% in the first month"            │
│    — Head of Platform, Series B SaaS                        │
│                                                             │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│    │ $2.4M    │  │ 10B+     │  │ 30%      │               │
│    │ Governed │  │ Tokens   │  │ Avg Save │               │
│    └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────────┘

STATES:
- Loading: spinner inside button, inputs disabled
- Error: red border on field(s), error message below
- SSO redirect: loading spinner full-page
```

### 3.2 Sign Up Page

```
Route: /auth/signup
Same split layout as sign in.

Step 1: Account Details
  - Work email (validate: not gmail/yahoo)
  - Full name
  - Password + confirm
  - [Create account]

Step 2: Organization Setup  (shown after email verified)
  - Organization name
  - Estimated monthly AI spend (dropdown: <$10K / $10-50K / $50-200K / $200K+)
  - Team size (dropdown)
  - Primary LLM provider (multi-select: OpenAI / Anthropic / Gemini / Other)
  - [Continue]

Validation:
  - Real-time password strength meter
  - Email domain check (warn if personal email)
  - Organization name availability check
```

---

## 4. Onboarding Flow

```
Route: /onboarding
Show: first time after signup, until all 5 steps complete
Layout: Full-page wizard (no sidebar during onboarding)

PROGRESS BAR: horizontal step indicator at top
  [1. Connect] → [2. See Data] → [3. Set Limits] → [4. Invite Team] → [5. Done]

STEP 1: Connect Your AI Traffic
─────────────────────────────────────────────
  Headline: "Route your first AI call in under 60 seconds"

  Show current base URL and new gateway URL side-by-side:
  ┌────────────────────────────────────────────┐
  │  BEFORE                                    │
  │  api.openai.com/v1                         │
  │                                            │
  │  AFTER                                     │
  │  gateway.ai-orchestrator.io/v1             │
  │                                            │
  │  [Copy gateway URL]                        │
  └────────────────────────────────────────────┘

  Code snippet tabs: [Python] [Node.js] [cURL] [Go]
  Each tab shows the one-line change needed.

  Auto-detect when first request arrives:
  - Polling indicator: "Waiting for first request..."
  - On success: green checkmark + "✓ First request received!"
  - Auto-advance to step 2

STEP 2: Your First Insights
─────────────────────────────────────────────
  Show live data populating:
  - "We've seen X requests in the last [time]"
  - Mini cost breakdown (top 3 models used)
  - Top spending user/team
  - Estimated monthly projection

  [Continue →]

STEP 3: Set Your First Budget
─────────────────────────────────────────────
  "Set a monthly limit to prevent bill surprises"

  ┌──────────────────────────────────────────┐
  │  Organization monthly limit              │
  │  $ [________] per month                  │
  │                                          │
  │  Alert me at: [80%] [90%] [100%]         │
  │  (toggleable chips)                      │
  │                                          │
  │  Alert via: [Slack] [Email] [Both]       │
  └──────────────────────────────────────────┘

  [Set Limit & Continue →]

STEP 4: Invite Your Team
─────────────────────────────────────────────
  "Get your team's AI spend under control together"

  ┌──────────────────────────────────────────┐
  │  [email@company.com]  [Role ▼]  [+ Add]  │
  │                                          │
  │  Pending invites:                        │
  │  • jane@company.com — Admin              │
  │  • bob@company.com  — Member             │
  └──────────────────────────────────────────┘

  [Invite & Continue →]  [Skip for now]

STEP 5: You're All Set
─────────────────────────────────────────────
  Celebration moment (subtle confetti, not over-the-top)

  Summary cards:
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ ✓ Gateway    │  │ ✓ Budget     │  │ ✓ Team       │
  │   Connected  │  │   Set        │  │   Invited    │
  └──────────────┘  └──────────────┘  └──────────────┘

  Next steps checklist:
  - [ ] Enable smart routing (save ~30%)
  - [ ] Set up Slack alerts
  - [ ] Configure team wallets
  - [ ] Install VS Code extension

  [Go to Dashboard →]
```

---

## 5. Dashboard — Home

```
Route: /
User Types: All roles see this; data scoped to their permission level
Goal: Instant situational awareness — costs, health, anomalies

LAYOUT:

ROW 1: Hero Metric Cards (4 cards across)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Total Spend │  │  Saved This  │  │  Requests    │  │  Cache Hit   │
│  This Month  │  │  Month       │  │  Today       │  │  Rate        │
│              │  │              │  │              │  │              │
│  $31,420     │  │  $8,240      │  │  847K        │  │  34.2%       │
│  ▲ 12% MoM   │  │  via caching │  │  +2.3% today │  │  ▲ 4% wk    │
│              │  │  + routing   │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

ROW 2: Spend Chart (left 65%) + Budget Status (right 35%)
┌──────────────────────────────────────┐  ┌─────────────────────────┐
│  Daily Spend — Last 30 Days          │  │  Budget Status           │
│                                      │  │                          │
│  [Area chart with                    │  │  Organization            │
│   actual spend (blue)                │  │  $31,420 / $50,000      │
│   + projected line (dashed)          │  │  [████████░░] 63%       │
│   + budget ceiling (red dashed)]     │  │                          │
│                                      │  │  Engineering             │
│  Hover: show exact $ + date          │  │  $12,200 / $20,000      │
│                                      │  │  [████████░░] 61%       │
│                                      │  │                          │
│                                      │  │  Legal                   │
│                                      │  │  $4,800 / $5,000  ⚠️   │
│                                      │  │  [█████████▉] 96%       │
│                                      │  │                          │
│                                      │  │  [View all wallets →]   │
└──────────────────────────────────────┘  └─────────────────────────┘

ROW 3: Top Models (left 33%) + Top Teams (center 33%) + Live Feed (right 33%)
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│  Spend by Model       │  │  Spend by Team        │  │  Live Request Feed    │
│  (horizontal bars)    │  │  (horizontal bars)    │  │  (real-time scroll)   │
│                       │  │                       │  │                       │
│  gpt-4o    $18,200    │  │  Engineering $12,200  │  │  ● gpt-4o  $0.023    │
│  [████████] 58%       │  │  [██████░░░] 61%      │  │  ● haiku   $0.001    │
│                       │  │                       │  │  ● gpt-4o  $0.031    │
│  claude-s  $8,400     │  │  Legal       $4,800   │  │  ● sonnet  $0.018    │
│  [█████░░░] 27%       │  │  [████░░░░░] 24%      │  │  ● haiku   $0.002    │
│                       │  │                       │  │                       │
│  haiku     $4,820     │  │  Sales        $2,100  │  │  Pause / Resume       │
│  [███░░░░░] 15%       │  │  [██░░░░░░░] 11%      │  │  [▐▐] [▶]           │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘

ROW 4: Alerts / Anomalies (full width if any exist)
┌──────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  Active Alerts                                                           │
│                                                                              │
│  [!] Legal team at 96% of $5,000 monthly budget — resets in 11 days         │
│  [!] Usage spike detected: Sales team +340% vs. 7-day avg (last 2 hours)    │
│  [✓] Provider failover event: OpenAI 429 → routed to Anthropic (2h ago)     │
│                                                                              │
│  [View all alerts →]                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

DATA REQUIREMENTS:
- GET /v1/analytics/cost?period=30d&granularity=day
- GET /v1/analytics/cost?group_by=model&period=30d
- GET /v1/analytics/cost?group_by=team&period=30d
- GET /v1/wallet/balance (all wallets)
- GET /v1/alerts?status=active
- WS  /v1/stream/requests (live feed)

STATES:
- Loading: skeleton cards with shimmer animation
- No data yet: onboarding prompt "Connect your first AI call"
- Partial data: show what's available, skeleton for missing
- Error: red banner with retry button
```

---

## 6. Cost Analytics

```
Route: /analytics/cost
Goal: Deep dive into AI spend — by any dimension, any time range
User: FinOps leads, Platform leads, CFOs

LAYOUT:

FILTER BAR (sticky below page header):
  [Date Range: Last 30 days ▼]  [Group by: Team ▼]  [Model: All ▼]
  [Provider: All ▼]  [Feature: All ▼]  [+ Add filter]
  Right side: [Export CSV]  [Schedule Report]

SECTION 1: Summary Ribbon (4 KPI cards, full width)
  Total Spend | vs. Last Period | Projected EOM | Top Cost Driver

SECTION 2: Main Chart (full width)
  Tabs: [Daily] [Weekly] [Monthly] [Hourly]

  Chart type (toggle):
  [Area Chart ▼] — options: Line, Bar, Stacked Bar, Area

  Stacked area chart showing spend per group-by dimension over time.

  Features:
  - Hover tooltip: date + breakdown by all dimensions
  - Click legend item to toggle series
  - Zoom: drag to select date range
  - Annotation: show when budget limit changed, when routing rules activated

SECTION 3: Breakdown Table (full width)

  When grouped by "Team":
  ┌──────────────────────────────────────────────────────────────────┐
  │  Team            │ This Month │ Last Month │  Change  │ % of Total │
  ├──────────────────┼────────────┼────────────┼──────────┼────────────┤
  │  ▼ Engineering   │  $12,200   │  $10,800   │  +12.9%  │   38.8%    │
  │    gpt-4o        │   $8,200   │   $7,100   │  +15.5%  │            │
  │    claude-sonnet │   $3,100   │   $2,900   │   +6.9%  │            │
  │    haiku         │     $900   │     $800   │  +12.5%  │            │
  ├──────────────────┼────────────┼────────────┼──────────┼────────────┤
  │  ▼ Legal         │   $4,800   │   $3,200   │  +50.0%  │   15.3%  🔴│
  └──────────────────────────────────────────────────────────────────┘

  Features:
  - Expandable rows (click to show sub-breakdown)
  - Color-coded change column (green = down, red = up significantly)
  - Click row to drill down into that team's detail view
  - Inline sparkline for each row (7-day trend)

SECTION 4: Cost Forecast Widget
  "At your current spend rate, you'll use $47,800 this month"
  Visual: bar showing actual + projected to EOM vs. limit
  Confidence interval shown as lighter band

SECTION 5: Optimization Opportunities (if applicable)
  "💡 Switch Legal team from gpt-4o → gpt-4o-mini for simple tasks — save ~$1,200/month"
  "💡 Enable semantic caching for Engineering team — estimated 28% fewer API calls"
  Each opportunity: [Learn more] [Enable now]

DATA REQUIREMENTS:
- GET /v1/analytics/cost (with various query params)
- GET /v1/analytics/cost/forecast
- GET /v1/analytics/optimization-suggestions
```

---

## 7. Wallet Management

```
Route: /wallets
Goal: Configure, monitor, and manage all budget wallets
User: FinOps leads, Platform leads, Admins

LAYOUT:

HEADER ACTION BAR:
  [+ Create Wallet]  [Export Chargeback CSV]

WALLET TREE VIEW (left 35%) + WALLET DETAIL (right 65%):

Left panel — Org Tree:
┌─────────────────────────────────┐
│  Acme Corp (Organization)       │
│  $31,420 / $50,000   63%       │
│  [████████░░]                   │
│                                 │
│  ▼ Engineering    $12,200/$20K  │
│      Platform         $8,200    │
│      Growth           $4,000    │
│  ▼ Legal           $4,800/$5K🔴│
│  ▼ Sales           $2,100/$8K  │
│  ▼ Marketing       $1,800/$6K  │
└─────────────────────────────────┘

Right panel — Selected Wallet Detail:
┌─────────────────────────────────────────────────────────────┐
│  Engineering Team Wallet                                     │
│  $12,200 spent of $20,000 limit   (61%)                     │
│                                                             │
│  [████████████████████████████░░░░░░░░░░] 61%               │
│   $0                                              $20,000   │
│                                                             │
│  METRICS ROW:                                               │
│  Daily avg: $407  │  Projected EOM: $18,500  │  13d left   │
│                                                             │
│  LIMIT SETTINGS:                            [Edit]          │
│  Monthly limit:    $20,000                                  │
│  Soft alerts:      80%, 90%, 95%                            │
│  Hard limit:       ✓ Enabled (block at 100%)                │
│  Overdraft:        ✗ Disabled                               │
│  Reset date:       1st of each month                        │
│                                                             │
│  TABS: [Spend History] [Transfers] [Sub-wallets] [Settings] │
│                                                             │
│  SPEND HISTORY (default tab):                               │
│  30-day area chart of this wallet's daily spend             │
│                                                             │
│  RECENT ACTIVITY:                                           │
│  Today        $407.20   ▲ 12% vs yesterday                 │
│  Yesterday    $363.80                                       │
│  Feb 16       $489.00   ⚠️ Spike detected                  │
└─────────────────────────────────────────────────────────────┘

EDIT WALLET MODAL:
┌─────────────────────────────────────┐
│  Edit Wallet: Engineering           │
│                                     │
│  Monthly limit (USD)                │
│  $ [20,000              ]           │
│                                     │
│  Alert thresholds                   │
│  [✓] 80%  [✓] 90%  [✓] 95%        │
│                                     │
│  Hard limit (block at 100%)         │
│  [●] Enabled  [○] Disabled          │
│                                     │
│  Overdraft allowance                │
│  [○] None  [○] 5%  [○] 10%  [○] Custom │
│                                     │
│  Reset period                       │
│  [Monthly ▼]  on the [1st ▼]        │
│                                     │
│  [Cancel]          [Save Changes]   │
└─────────────────────────────────────┘

BUDGET TRANSFER PANEL:
Route: /wallets/transfers

List of pending transfers (table):
  From | To | Amount | Requested by | Reason | Status | Actions
  Engineering → Legal | $2,000 | jane@co | "Q1 compliance audit" | Pending | [Approve] [Reject]

Transfer detail modal:
  Shows full context: requester, reason, wallet balances before/after
  [Approve with note] [Reject with reason]

STATES:
- Wallet at 0%: Muted progress bar, "No spend yet this month"
- Wallet 80-89%: Warning orange bar, soft alert badge
- Wallet 90-99%: Strong orange bar, warning icon
- Wallet 100%: Red bar, "Blocked" badge
- Wallet in overdraft: Red bar > 100% marker
```

---

## 8. Routing Rules

```
Route: /routing
Goal: Configure how AI traffic is routed between models and providers
User: Platform Engineers, Admins

LAYOUT:

HEADER:
  [+ Create Rule]  [Test Routing]  [View Decision Log]

RULES TABLE (full width):

  ┌────┬────────────────────────┬──────────┬────────────────────────┬────────┬────────────┐
  │ ≡  │ Name                   │ Priority │ Conditions             │ Action │ Status     │
  ├────┼────────────────────────┼──────────┼────────────────────────┼────────┼────────────┤
  │ ⠿  │ Compliance Firewall    │   1      │ Data class=CONFIDENTIAL│ Reroute│ ● Active   │
  │ ⠿  │ Premium Model Gating   │  10      │ Model=gpt-4o, team≠eng │ Reroute│ ● Active   │
  │ ⠿  │ After-Hours Cost Save  │  20      │ Time >18:00 UTC        │ Reroute│ ● Active   │
  │ ⠿  │ Token Limit Block      │  30      │ Est. tokens > 20,000   │ Block  │ ○ Inactive │
  │ ⠿  │ Budget Threshold Route │  40      │ Wallet > 80%           │ Reroute│ ● Active   │
  └────┴────────────────────────┴──────────┴────────────────────────┴────────┴────────────┘

  Features:
  - Drag handle (⠿) for priority reordering
  - Click row to expand inline detail
  - Toggle active/inactive with switch
  - Bulk actions: [Delete selected] [Enable selected] [Disable selected]

CREATE/EDIT RULE MODAL (full-height side panel, not modal):

  Slides in from right, 480px wide

  ┌────────────────────────────────────────────┐
  │  Create Routing Rule                    ✕  │
  │  ─────────────────────────────────────     │
  │  Name                                      │
  │  [Premium Model Gating              ]      │
  │                                            │
  │  Priority  (lower = runs first)            │
  │  [10                                ]      │
  │                                            │
  │  CONDITIONS  (all must match)              │
  │  + Add condition                           │
  │                                            │
  │  [Model requested ▼] [is ▼] [gpt-4o ▼] ✕ │
  │  [Team ▼] [is not ▼] [engineering ▼]   ✕ │
  │  [+ Add condition]                         │
  │                                            │
  │  ACTION                                    │
  │  [Reroute ▼]                               │
  │    Target model: [gpt-4o-mini ▼]           │
  │    Notify user:  [✓]                       │
  │    Reason msg:   [Premium model restricted] │
  │                                            │
  │  ─────────────────────────────────────     │
  │  DRY RUN MODE  (log but don't enforce)     │
  │  [○] Off  [●] On                          │
  │                                            │
  │  [Test Rule]    [Cancel]  [Save Rule]      │
  └────────────────────────────────────────────┘

TEST ROUTING PANEL:
  Route: /routing/test

  "Simulate a request and see which rules fire"

  ┌────────────────────────────────────────────┐
  │  Simulate Request                          │
  │                                            │
  │  Model: [gpt-4o ▼]  Team: [Legal ▼]       │
  │  Est. tokens: [5000      ]                 │
  │  Time (UTC):  [14:30     ]                 │
  │  Data class:  [STANDARD ▼]                 │
  │                                            │
  │  [Run Simulation]                          │
  │                                            │
  │  RESULT:                                   │
  │  Rule #10 "Premium Model Gating" matched   │
  │  → Request would be rerouted to gpt-4o-mini│
  │  → Estimated cost: $0.0012 (was $0.0089)  │
  │  → Savings: 86%                            │
  └────────────────────────────────────────────┘
```

---

## 9. Security & Policies

```
Route: /security
Goal: Configure PII detection, prompt scanning, and OPA policies
User: Security leads, Compliance officers, Admins

LAYOUT:

TABS: [Overview] [PII Detection] [Policy Engine] [Quarantine Queue]

─── OVERVIEW TAB ──────────────────────────────────────────────

Summary cards:
  Requests Scanned Today | PII Detections Today | Blocks Today | Avg Scan Latency

Firewall pipeline status:
  ┌─────────────────────────────────────────────────────────────┐
  │  Security Middleware Pipeline                               │
  │                                                             │
  │  [Auth] → [Rate Limit] → [PII Scan] → [OPA Policy] → [✓]  │
  │    ✓           ✓             ✓ (8ms)       ✓ (2ms)         │
  │                                                             │
  │  All systems operational  ●                                 │
  └─────────────────────────────────────────────────────────────┘

Recent detections feed:
  Timestamp | Type | Team | Action | Request ID
  14:32:01  | EMAIL | Legal | Redacted | req_abc123
  14:28:44  | API_KEY | Marketing | Blocked + Alerted | req_xyz789

─── PII DETECTION TAB ─────────────────────────────────────────

Entity types configuration table:
  ┌──────────────────┬─────────┬───────────────────┬──────────────┐
  │  Entity Type     │ Enabled │ Action            │ Sensitivity  │
  ├──────────────────┼─────────┼───────────────────┼──────────────┤
  │  Email addresses │  ●      │ Redact ▼          │ Medium ▼     │
  │  Phone numbers   │  ●      │ Redact ▼          │ Medium ▼     │
  │  SSN             │  ●      │ Block ▼           │ High ▼       │
  │  Credit cards    │  ●      │ Block ▼           │ High ▼       │
  │  API keys/tokens │  ●      │ Block + Alert ▼   │ Critical ▼   │
  │  Full names      │  ○      │ Redact ▼          │ Low ▼        │
  │  Medical info    │  ●      │ Block ▼           │ High ▼       │
  │  IP addresses    │  ○      │ Redact ▼          │ Low ▼        │
  └──────────────────┴─────────┴───────────────────┴──────────────┘

  [+ Add Custom Pattern]

Custom pattern modal:
  Name: [_______]
  Regex: [_______]  [Test]
  Action: [Block ▼]
  Apply to: [All teams ▼]

─── POLICY ENGINE TAB ─────────────────────────────────────────

  Left: Policy list
  ┌──────────────────────────────┐
  │  + New Policy                │
  │                              │
  │  ● Premium Hours Lock        │
  │    OPA · Active · 3 triggers │
  │                              │
  │  ● Token Size Limit          │
  │    OPA · Active · 1 trigger  │
  │                              │
  │  ○ Data Class Router         │
  │    OPA · Inactive            │
  │                              │
  │  [Built-in templates →]      │
  └──────────────────────────────┘

  Right: Policy editor (Monaco editor)
  ┌──────────────────────────────────────────────┐
  │  Premium Hours Lock        [Active ●]  [Save] │
  │  ─────────────────────────────────────────── │
  │  [Rego] [JSON preview] [Test]                │
  │                                              │
  │  1  package orchestrator                     │
  │  2                                           │
  │  3  deny[reason] {                           │
  │  4    input.model == "gpt-4o"                │
  │  5    hour := time.clock(time.now_ns())[0]   │
  │  6    hour >= 18                             │
  │  7    reason := "Premium models restricted   │
  │  8              outside business hours"      │
  │  9  }                                        │
  │                                              │
  │  ─────────────────────────────────────────── │
  │  TEST POLICY:                                │
  │  Input: [{ "model": "gpt-4o", ...}  ]       │
  │  [Run Test]                                  │
  │  Result: DENY — "Premium models restricted"  │
  └──────────────────────────────────────────────┘

─── QUARANTINE QUEUE TAB ──────────────────────────────────────

  Requests flagged for manual review:
  ┌────────────────────────────────────────────────────────────┐
  │  Timestamp    User          Risk Score  Reason    Actions  │
  │  14:32 today  bob@co.com   87/100      Jailbreak [Review] │
  │  09:14 today  ai-service   92/100      PII + Key [Review] │
  └────────────────────────────────────────────────────────────┘

  Review modal:
    Show: prompt text (redacted) + detected issues + risk score breakdown
    Actions: [Allow once] [Block] [Ban user] [Add to allowlist]
```

---

## 10. Audit Log

```
Route: /audit
Goal: Compliance-grade search and export of all system events
User: Security, Compliance, Admins

LAYOUT:

FILTER ROW:
  [Date range ▼]  [Actor type: All ▼]  [Action: All ▼]  [Resource: All ▼]
  Right: [Export] [Verify chain integrity]

AUDIT LOG TABLE (full width, append-only feel):

  ┌────────────────┬──────────────┬────────────────────────┬──────────────┬───────────┐
  │  Timestamp     │  Actor       │  Action                │  Resource    │  IP       │
  ├────────────────┼──────────────┼────────────────────────┼──────────────┼───────────┤
  │  14:32:01.234  │  jane@co.com │  wallet.limit.updated  │  Engineering │  10.0.0.1 │
  │  14:28:44.891  │  System      │  request.blocked.pii   │  req_abc123  │  —        │
  │  14:20:12.001  │  admin       │  policy.created        │  Premium Lock│  10.0.0.2 │
  │  13:55:00.441  │  api-service │  provider.failover     │  OpenAI→Ant. │  —        │
  └────────────────┴──────────────┴────────────────────────┴──────────────┴───────────┘

  Features:
  - Monospace timestamp for precision
  - Click row to expand full detail panel
  - Color-coded action column (red for blocks/breaches, green for approvals)
  - "Chain intact ✓" badge on each row (cryptographic verification)
  - Infinite scroll (not paginated — log is append-only)
  - Keyboard shortcut: Cmd+F for in-page search

DETAIL PANEL (slides in from right on row click):
  Full JSON of before/after state
  Hash of this entry
  Hash of previous entry
  [Copy JSON] [Export this entry]

CHAIN INTEGRITY STATUS (top of page):
  ┌─────────────────────────────────────────────────────────────┐
  │  ✓ Audit chain integrity verified — Last checked: 2 min ago │
  │  3,847,291 entries — No tampering detected                  │
  └─────────────────────────────────────────────────────────────┘
```

---

## 11. Prompt Registry

```
Route: /prompts
Goal: Version-control and govern all AI prompts used across the org
User: Engineers, Product Managers, Admins

LAYOUT:

HEADER: [+ New Prompt]  [Import from LangChain Hub]

LEFT PANEL (33%) — Prompt List:
  Search: [_______________________]
  Filter: [All ▼] [Production ▼]

  ┌──────────────────────────────────┐
  │  cust-support-classifier         │
  │  v3 · Production · $0.00048/call │
  │                                  │
  │  email-summarizer                │
  │  v7 · Production · $0.00021/call │
  │                                  │
  │  code-review-assistant           │
  │  v2 · Draft · Awaiting review   │
  │                                  │
  │  legal-contract-extractor        │
  │  v1 · Production · $0.00380/call │
  └──────────────────────────────────┘

RIGHT PANEL (67%) — Prompt Detail:

  TABS: [Current] [History] [Performance] [Settings]

  CURRENT TAB:
  ┌─────────────────────────────────────────────────────┐
  │  customer-support-classifier           v3 [Edit]    │
  │  Production · gpt-4o-mini             [Roll back]   │
  │  ─────────────────────────────────────────────────  │
  │  PROMPT CONTENT (Monaco editor, read-only):         │
  │                                                     │
  │  System: You are a customer support classifier...   │
  │  User: {{ticket_text}}                              │
  │                                                     │
  │  ─────────────────────────────────────────────────  │
  │  VARIABLES:                                         │
  │  ticket_text (string, required)                     │
  │  customer_tier (string, optional, default: "free")  │
  │                                                     │
  │  PERFORMANCE (last 7 days):                         │
  │  Avg cost: $0.00048  │  Avg tokens: 970             │
  │  Calls: 48,200       │  Error rate: 0.02%           │
  └─────────────────────────────────────────────────────┘

  HISTORY TAB:
  ┌─────────────────────────────────────────────────────┐
  │  v3  [Current]    Feb 15 — jane@co.com              │
  │  "Reduced prompt length by 30%, same quality"       │
  │                                                     │
  │  v2  Feb 10 — bob@co.com      [View] [Restore]      │
  │  "Added tier-specific handling"                     │
  │                                                     │
  │  v1  Feb 01 — alice@co.com    [View]                │
  │  "Initial version"                                  │
  └─────────────────────────────────────────────────────┘

  DIFF VIEW (when comparing versions):
  Side-by-side diff with green/red highlights

APPROVAL WORKFLOW:
  When prompt is in "Pending Review":
  - Show reviewer assignment
  - Comment thread
  - [Approve] [Request Changes] [Reject]
```

---

## 12. Provider Management

```
Route: /providers
Goal: Configure and monitor all connected LLM providers
User: Platform Engineers, Admins

LAYOUT:

HEADER: [+ Add Provider]

PROVIDER GRID (3 columns):

  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
  │  [OpenAI Logo]       │  │  [Anthropic Logo]    │  │  [Gemini Logo]       │
  │  OpenAI              │  │  Anthropic           │  │  Google Gemini       │
  │  ● Healthy           │  │  ● Healthy           │  │  ⚠ Degraded         │
  │                      │  │                      │  │                      │
  │  Models: 6 active    │  │  Models: 4 active    │  │  Models: 3 active    │
  │  Requests today: 42K │  │  Requests today: 18K │  │  Requests today: 3K  │
  │  Avg latency: 842ms  │  │  Avg latency: 1,204ms│  │  Avg latency: 4,120ms│
  │  Cost/1K: $0.005     │  │  Cost/1K: $0.003     │  │  Cost/1K: $0.002     │
  │                      │  │                      │  │                      │
  │  Priority: 1 ▲▼     │  │  Priority: 2 ▲▼     │  │  Priority: 3 ▲▼     │
  │                      │  │                      │  │                      │
  │  [Configure] [Test]  │  │  [Configure] [Test]  │  │  [Configure] [Test]  │
  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘

PROVIDER HEALTH TIMELINE (full width):
  Last 24h status per provider (like GitHub status page)
  Color blocks: green=healthy, yellow=degraded, red=down

PROVIDER DETAIL PANEL (side panel on click):
  ┌────────────────────────────────────────────────┐
  │  OpenAI                              [Edit] ✕  │
  │  ─────────────────────────────────────────     │
  │  Status: ● Healthy (last check: 42s ago)       │
  │  Base URL: https://api.openai.com/v1           │
  │  API Key: sk-...•••••••••••• [Rotate]          │
  │  Region restrictions: us, eu                   │
  │                                                │
  │  MODELS:                                       │
  │  [✓] gpt-4o         $0.005/1K out  [Edit]     │
  │  [✓] gpt-4o-mini    $0.0006/1K out [Edit]     │
  │  [✓] gpt-3.5-turbo  $0.0002/1K out [Edit]     │
  │  [ ] o1-preview     (disabled)      [Enable]   │
  │                                                │
  │  RATE LIMITS:                                  │
  │  Requests/min: 10,000                          │
  │  Tokens/min:   2,000,000                       │
  │                                                │
  │  [Test Connection]  [View Logs]                │
  └────────────────────────────────────────────────┘

ADD PROVIDER FLOW:
  Step 1: Select provider type (grid of logos + "Custom")
  Step 2: Enter credentials (base URL, API key)
  Step 3: Test connection (shows: latency, models found)
  Step 4: Configure models + pricing
  Step 5: Set priority + region restrictions
```

---

## 13. Team & User Management

```
Route: /team
Goal: Manage users, teams, roles, and wallet assignments
User: Admins, Owners

LAYOUT:

TABS: [Teams] [Members] [Invites] [Roles]

─── TEAMS TAB ─────────────────────────────────────────────────

  [+ Create Team]

  Table:
  ┌──────────────────┬──────────┬─────────────┬───────────┬────────────────┐
  │  Team Name       │ Members  │ Wallet      │ This Month│  Actions       │
  ├──────────────────┼──────────┼─────────────┼───────────┼────────────────┤
  │  Engineering     │  24      │ $20K limit  │  $12,200  │ [Edit] [View]  │
  │  Legal           │   8      │ $5K limit   │   $4,800⚠│ [Edit] [View]  │
  │  Sales           │  15      │ $8K limit   │   $2,100  │ [Edit] [View]  │
  └──────────────────┴──────────┴─────────────┴───────────┴────────────────┘

─── MEMBERS TAB ───────────────────────────────────────────────

  [+ Invite Member]  Search: [______________]

  Table:
  ┌─────────────────────┬────────────┬───────────┬──────────┬──────────────┐
  │  Member             │  Role      │  Teams    │ This Mo. │  Actions     │
  ├─────────────────────┼────────────┼───────────┼──────────┼──────────────┤
  │  👤 Jane Doe        │  Admin     │  Eng, Leg │ $1,240   │ [Edit] [···] │
  │     jane@co.com     │            │           │          │              │
  │  👤 Bob Smith       │  Member    │  Eng      │   $840   │ [Edit] [···] │
  │  🤖 ai-service      │  API Only  │  Eng      │ $8,200   │ [Edit] [···] │
  └─────────────────────┴────────────┴───────────┴──────────┴──────────────┘

─── ROLES TAB ─────────────────────────────────────────────────

  Built-in roles (not editable):
  ● Owner    — Full access + billing
  ● Admin    — All settings, no billing
  ● Member   — Use AI + see own spend
  ● Viewer   — Read-only dashboard

  [+ Create Custom Role]
  Custom role builder: permission checklist

INVITE MODAL:
  Email: [_______________________]
  Role: [Member ▼]
  Teams: [Engineering ▼] [+ Add]
  Wallet limit (override): [None — use team wallet ▼]
  [Send Invite]
```

---

## 14. API Key Management

```
Route: /keys
Goal: Create, rotate, and manage API keys for gateway access
User: Engineers, Admins

LAYOUT:

HEADER: [+ Create API Key]

TABLE:
┌──────────────────┬────────────┬───────────┬─────────────┬──────────────────┐
│  Name            │  Key       │  Created  │  Last used  │  Actions         │
├──────────────────┼────────────┼───────────┼─────────────┼──────────────────┤
│  Production App  │ sk-...4f2a │ Feb 01    │ 2 min ago   │ [Rotate] [Revoke]│
│  Dev Environment │ sk-...8c1e │ Jan 15    │ 1 hour ago  │ [Rotate] [Revoke]│
│  CI Pipeline     │ sk-...2b9d │ Jan 10    │ Never       │ [Rotate] [Revoke]│
└──────────────────┴────────────┴───────────┴─────────────┴──────────────────┘

CREATE KEY MODAL:
┌────────────────────────────────────────┐
│  Create API Key                        │
│                                        │
│  Name (for your reference)             │
│  [________________________________]    │
│                                        │
│  Assign to team (for cost attribution) │
│  [Engineering ▼]                       │
│                                        │
│  Spend limit (optional override)       │
│  [ ] No limit  [●] Custom: $[_____]/mo │
│                                        │
│  Permissions                           │
│  [✓] Chat completions                  │
│  [✓] Embeddings                        │
│  [ ] Admin API                         │
│                                        │
│  Expiry                                │
│  [Never ▼]                             │
│                                        │
│  [Cancel]         [Create Key]         │
└────────────────────────────────────────┘

KEY CREATED — SHOW ONCE:
┌────────────────────────────────────────┐
│  ⚠️  Copy your API key now             │
│  This is the only time it will be shown│
│                                        │
│  sk-orch-live-abc123...xyz789          │
│  [████████████████████████] [Copy]     │
│                                        │
│  [I've saved my key — Continue]        │
└────────────────────────────────────────┘
```

---

## 15. Notifications & Alerts

```
Route: /notifications
Goal: Configure alert rules and view notification history
User: All roles (scoped to their teams)

LAYOUT:

TABS: [Alert History] [Alert Rules] [Channels]

─── ALERT HISTORY ─────────────────────────────────────────────

  List of all alerts fired:
  ┌────────────────┬────────────────────────────────────┬─────────┬──────────┐
  │  Time          │  Alert                             │  Team   │  Status  │
  ├────────────────┼────────────────────────────────────┼─────────┼──────────┤
  │  14:32 today   │ Legal team at 96% of $5K budget    │  Legal  │  Active  │
  │  09:14 today   │ Spend spike: Sales +340% vs avg    │  Sales  │  Active  │
  │  Feb 17 22:01  │ Engineering hit 90% threshold      │  Eng.   │  Resolved│
  │  Feb 17 18:00  │ Provider failover: OpenAI → Anthr. │  All    │  Resolved│
  └────────────────┴────────────────────────────────────┴─────────┴──────────┘

─── ALERT RULES ───────────────────────────────────────────────

  [+ Create Alert Rule]

  List of configured rules:
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Budget Threshold Alerts (built-in)                                 │
  │  Alert when any wallet reaches 80%, 90%, 95%, 100% of limit        │
  │  Channels: Slack + Email  ●  [Edit]                                 │
  │                                                                     │
  │  Spend Spike Detection                                              │
  │  Alert when hourly spend > 2x rolling 7-day average                │
  │  Channels: Slack  ●  [Edit]                                         │
  │                                                                     │
  │  Provider Health                                                    │
  │  Alert on any provider failover event                               │
  │  Channels: Slack + PagerDuty  ●  [Edit]                            │
  └─────────────────────────────────────────────────────────────────────┘

─── CHANNELS ──────────────────────────────────────────────────

  [+ Add Channel]

  ┌──────────────────┬──────────────────────────┬─────────┬──────────────┐
  │  Channel         │  Config                  │  Status │  Actions     │
  ├──────────────────┼──────────────────────────┼─────────┼──────────────┤
  │  Slack #ai-alerts│  Connected to Workspace  │  ● Live │ [Test] [Edit]│
  │  Email           │  5 recipients            │  ● Live │ [Test] [Edit]│
  │  PagerDuty       │  escalation-policy-001   │  ● Live │ [Test] [Edit]│
  └──────────────────┴──────────────────────────┴─────────┴──────────────┘
```

---

## 16. Experiments

```
Route: /experiments
Goal: A/B test model routing to optimize cost vs quality
User: Platform Engineers

LAYOUT:

HEADER: [+ New Experiment]

EXPERIMENT LIST:
  ACTIVE:
  ┌──────────────────────────────────────────────────────────────────────┐
  │  GPT-4o vs Claude Sonnet for Code Review     ● Running since Feb 10 │
  │  Traffic: 50/50   Requests: 24,820   Confidence: 67% (need 95%)      │
  │                                                                      │
  │  Variant A (GPT-4o):    $0.00892/req  842ms avg  0.3% error         │
  │  Variant B (Claude):    $0.00341/req  961ms avg  0.2% error         │
  │                              ↑ 62% cheaper  ↑ slightly slower        │
  │                                                                      │
  │  [View Details]  [Stop Experiment]  [Promote Variant B]              │
  └──────────────────────────────────────────────────────────────────────┘

  COMPLETED:
  Collapsible list of past experiments with winner declared

EXPERIMENT DETAIL:

  Charts side-by-side:
  - Cost per request over time (Variant A vs B lines)
  - Latency P50/P95 (Variant A vs B)
  - Error rate (Variant A vs B)
  - Request volume distribution

  Statistical significance:
  "67% confidence that Variant B is cheaper. Need 95% to declare winner."
  Progress bar to significance threshold.

  Auto-switch settings:
  "Automatically promote Variant B if: cost savings > 30% AND error rate < 1% AND confidence > 95%"
  [Edit thresholds]

CREATE EXPERIMENT MODAL:
  Name: [_______________________]
  Traffic to test:  [All traffic ▼] or [Specific team ▼]
  Variant A model:  [gpt-4o ▼]        Traffic: [50%]
  Variant B model:  [claude-sonnet ▼] Traffic: [50%]
  Success metrics:  [✓] Cost  [✓] Latency  [ ] Error rate
  Auto-promote:     [✓] Enable  Threshold: [95% confidence]
  [Start Experiment]
```

---

## 17. Settings

```
Route: /settings
Tabs: [General] [Security] [Billing] [Integrations] [Data & Privacy] [Advanced]

─── GENERAL ───────────────────────────────────────────────────
  Organization name
  Default currency
  Default timezone
  Default model (fallback if no routing rule matches)
  Default monthly reset day

─── SECURITY ──────────────────────────────────────────────────
  SSO Configuration:
    [+ Configure SAML SSO]  or  [Manage existing]
    [+ Configure OIDC]

  Two-factor authentication:
    Enforce 2FA for: [Admins only ▼]

  Session management:
    Session timeout: [8 hours ▼]
    [Revoke all active sessions]

  IP allowlist:
    [ ] Enable IP allowlist
    [Add IP range]

─── BILLING ───────────────────────────────────────────────────
  Current plan: Growth — $1,999/month
  Managed spend this month: $31,420 of included $200K
  Next invoice: March 1, 2026 — est. $1,999

  [Upgrade plan]  [Download invoice]  [Billing history]

  Payment method: Visa ****4242  [Update]

─── INTEGRATIONS ──────────────────────────────────────────────

  CONNECTED:
  ┌──────────────────────────────────────────────────────────────┐
  │  [Slack logo]  Slack                              ● Connected │
  │  Workspace: Acme Corp   Channel: #ai-alerts       [Configure]│
  │                                                              │
  │  [Datadog logo] Datadog                           ● Connected │
  │  API key: ••••••4f2a                              [Configure]│
  └──────────────────────────────────────────────────────────────┘

  AVAILABLE:
  Grid of integration tiles:
  [Slack] [MS Teams] [Okta] [Snowflake] [Datadog] [PagerDuty]
  [SAP] [Oracle] [LaunchDarkly] [GitHub Actions] [+ More]

  Each tile: Logo + Name + "Connect" button or "Connected ✓"

─── DATA & PRIVACY ────────────────────────────────────────────
  Store prompt content: [○ Off] (off by default)
  Audit log retention: [365 days ▼]
  Data residency region: [US (us-east-1) ▼]
  [Request data export]  [Delete organization data]

─── ADVANCED ──────────────────────────────────────────────────
  API rate limits (override defaults)
  Custom domain for gateway (gateway.yourdomain.com)
  Webhook secret rotation
  [Download organization config as JSON]
```

---

## 18. Admin / Super-Admin Panel

```
Route: /admin  (internal staff only, separate from customer dashboard)
Access: AI Orchestrator team only

Sections:
- All organizations list + usage + plan + MRR
- Organization detail (impersonate, support, override)
- Global provider health status
- System metrics (total req/s, global error rate, p95 latency)
- Feature flag management (enable/disable per org)
- Billing override + manual credits
- Audit of admin actions (separate log)
```

---

## 19. Shared Components Library

### 19.1 Metric Card

```tsx
// Usage: KPI summary cards on dashboard and analytics pages

interface MetricCardProps {
  title: string
  value: string           // "$ 31,420"
  change?: string         // "+12%" or "-8%"
  changeDirection?: 'up' | 'down'   // for color coding
  changePositive?: boolean          // up=good or up=bad context
  subtitle?: string       // "vs last month"
  icon?: LucideIcon
  loading?: boolean
  onClick?: () => void
}

// Visual spec:
// Card: white bg, rounded-xl, shadow-md, p-6
// Title: text-sm, text-slate-500, font-medium
// Value: text-3xl, font-bold, text-slate-900
// Change: text-sm badge — green if positive, red if negative
// Icon: top-right corner, 24px, color matches change direction
// Loading: skeleton shimmer on value and change
```

### 19.2 Progress Bar (Budget)

```tsx
// Usage: wallet utilization displays

interface BudgetBarProps {
  spent: number
  limit: number
  size?: 'sm' | 'md' | 'lg'
  showLabels?: boolean
  showPercentage?: boolean
}

// Color rules:
// 0–79%:   bg-blue-500 (normal)
// 80–89%:  bg-amber-500 (warning)
// 90–99%:  bg-orange-500 (danger approaching)
// 100%+:   bg-red-500 (exceeded)

// Animation: smooth width transition on mount (500ms ease-out)
```

### 19.3 Status Badge

```tsx
// Usage: status indicators everywhere

type Status = 'active' | 'inactive' | 'healthy' | 'degraded' | 'down' |
              'pending' | 'blocked' | 'approved' | 'rejected' | 'warning'

// Spec:
// rounded-full, px-2.5 py-0.5, text-xs, font-medium
// Includes colored dot (●) before text
// Color: see status color system in Design System section
```

### 19.4 Data Table

```tsx
// Usage: all tabular data (request logs, audit logs, team members, etc.)

// Must include:
// - Column sorting (click header)
// - Server-side pagination (prev/next + page size selector)
// - Row selection (checkboxes + bulk actions)
// - Row hover highlight
// - Empty state slot
// - Loading skeleton (show correct number of skeleton rows)
// - Mobile: horizontal scroll, pinned first column

// Standard pagination footer:
// "Showing 1–25 of 4,821 results"  [← Prev] [1] [2] ... [193] [Next →]
```

### 19.5 Command Palette

```tsx
// Triggered by: Cmd+K (Mac) / Ctrl+K (Win)
// Global search + navigation

// Features:
// - Type to search any page, team, provider, prompt, or request
// - Recent pages shown by default
// - Keyboard navigation (↑↓ arrows, Enter to select, Esc to close)
// - Categories: Pages, Teams, Providers, Recent requests
// - Fuzzy search with highlighted match characters
```

### 19.6 Confirmation Dialog

```tsx
// Usage: for destructive actions (delete, revoke, block)

// Always require:
// - Clear description of what will be deleted/affected
// - Number of affected records if applicable
// - Type-to-confirm for irreversible actions (type org name)
// - Explicitly labeled Cancel and Confirm buttons
// - Confirm button: red for destructive, blue for neutral
```

### 19.7 Toast Notifications

```tsx
// Library: sonner
// Position: bottom-right

// Types:
// success — green icon, "Wallet limit updated"
// error   — red icon,   "Failed to save — try again"
// warning — amber icon, "Routing rule conflicts with rule #3"
// info    — blue icon,  "Provider pricing updated"

// Duration: 4s for success/info, 6s for warning, 8s for error (or manual dismiss)
// Always include: actionable text, not just "Error occurred"
```

### 19.8 Empty States

See Section 20 for complete empty state specs.

### 19.9 Loading Skeletons

```tsx
// Every data-loaded section must have a skeleton state
// Use Tailwind animate-pulse class
// Match skeleton dimensions to actual content layout exactly
// Never show spinner for known-layout content (use skeleton instead)
// Spinner only for: button loading states, full-page transitions
```

### 19.10 Cost Display

```tsx
// All monetary values must follow this format:

// < $0.001:   "$0.0008"    (4 decimal places)
// $0.001–$1:  "$0.0042"    (4 decimal places)
// $1–$1,000:  "$42.30"     (2 decimal places, no comma)
// $1,000+:    "$1,240.00"  (2 decimal places, comma separator)
// $10,000+:   "$12,240"    (0 decimal places, comma separator)
// $1M+:       "$1.2M"      (abbreviated)

// Savings always shown in green with downward arrow: ↓ $2,400 saved
// Cost increases shown in red with upward arrow:     ↑ $1,200 increase
```

### 19.11 Token Count Display

```tsx
// < 1,000:      "847 tokens"
// 1K–1M:        "12.4K tokens"
// 1M+:          "2.1M tokens"
// Always show both input + output when applicable:
// "450 in / 280 out"
```

---

## 20. Empty States

Every list view needs a thoughtful empty state. Never show a blank page.

### 20.1 Empty State Spec

```
Every empty state must have:
1. Relevant illustration (use simple SVG, not stock photos)
2. Clear heading: what is missing
3. One-line explanation: why it's empty / what it means
4. Primary action: what to do next
5. Optional: secondary link to docs
```

### 20.2 Empty States by Screen

```
DASHBOARD — No requests yet:
  Illustration: Gateway icon with dashed connection lines
  Heading: "No AI traffic yet"
  Body: "Connect your first application to start tracking cost and usage"
  Action: [Connect your app →]  [View quick start guide]

WALLETS — No wallets configured:
  Illustration: Empty wallet
  Heading: "No budget limits set"
  Body: "Set wallet limits to prevent bill surprises and track team spend"
  Action: [Create your first wallet]

ROUTING RULES — No rules:
  Illustration: Branching path icon
  Heading: "No routing rules configured"
  Body: "Smart routing rules automatically reduce costs by sending requests to the right model"
  Action: [Create first rule]  [Browse templates]

AUDIT LOG — No events yet:
  Illustration: Empty scroll
  Heading: "No audit events yet"
  Body: "System events will appear here as your team uses AI Orchestrator"
  Action: (none — informational only)

PROMPT REGISTRY — No prompts:
  Illustration: Document with code
  Heading: "No prompts registered"
  Body: "Version control your team's AI prompts to track cost, quality, and changes over time"
  Action: [Add your first prompt]  [Import from LangChain Hub]

EXPERIMENTS — No experiments:
  Illustration: Flask / beaker
  Heading: "No experiments running"
  Body: "A/B test different models to find the optimal cost-quality tradeoff for your workloads"
  Action: [Start first experiment]

API KEYS — No keys:
  Illustration: Key icon
  Heading: "No API keys created"
  Body: "Create an API key to start routing AI traffic through AI Orchestrator"
  Action: [Create API key]

TEAM — No members invited:
  Illustration: Group of people silhouettes
  Heading: "You're the only one here"
  Body: "Invite your team to give everyone visibility into AI costs and usage"
  Action: [Invite team members]

NOTIFICATIONS — No alerts:
  Illustration: Bell with checkmark
  Heading: "All clear"
  Body: "No active alerts. Your budgets are healthy and providers are operating normally."
  Action: (none — positive empty state)
```

---

## 21. Mobile Responsiveness

```
AI Orchestrator is primarily a desktop product but must be functional on mobile.

MOBILE PRIORITIES (in order):
1. Dashboard — view spend and alerts
2. Wallet balance — check budget from phone
3. Notifications — review and approve alerts
4. Approve budget transfer requests (from Slack → in-app)

MOBILE LAYOUT:
- Sidebar: hidden; hamburger → bottom sheet navigation
- Tables: horizontal scroll with sticky first column
- Cards: single column stack
- Charts: simplified; hide secondary data series
- Modals: full-screen bottom sheet on mobile
- Actions: bottom-fixed action bar for primary CTA

MINIMUM TOUCH TARGETS:
- All buttons: minimum 44×44px
- Table rows: minimum 48px height
- Toggle switches: 44px wide
```

---

## 22. Accessibility Requirements

```
WCAG 2.1 AA compliance required throughout.

COLOR:
- All text: minimum 4.5:1 contrast ratio against background
- Large text (18px+): minimum 3:1 contrast
- Never use color alone to convey status — always pair with icon or text label
- Test all color states: normal, hover, focus, active, disabled

KEYBOARD:
- All interactive elements reachable by Tab
- Logical tab order (left→right, top→bottom)
- Visible focus ring on all focusable elements (never remove outline without replacement)
- Escape closes all modals, dropdowns, side panels
- Arrow keys navigate within components (table rows, sidebar, menu items)
- Enter activates buttons and links
- Space toggles checkboxes and switches
- Cmd+K / Ctrl+K opens command palette

SCREEN READERS:
- All images have descriptive alt text
- Icons that convey meaning have aria-label
- Decorative icons have aria-hidden="true"
- Charts have text summary alternatives
- Loading states announce via aria-live="polite"
- Error messages announced via role="alert"
- Modal: focus trapped inside; aria-modal="true"; return focus on close
- Tables: proper thead, th scope, caption where helpful
- Status badges: include full text (not just icon)

FORMS:
- All inputs have associated labels (not just placeholder text)
- Error messages linked via aria-describedby
- Required fields marked with aria-required="true"
- Autocomplete attributes on standard fields

MOTION:
- Respect prefers-reduced-motion
- No auto-playing animations
- Transition durations: max 200ms for UI feedback, 300ms for layout changes
```

---

## 23. Performance Requirements

```
PAGE LOAD:
- First Contentful Paint (FCP): < 1.2s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

INTERACTIONS:
- Button feedback: < 100ms
- Navigation between pages: < 500ms (use loading skeletons)
- Chart rendering: < 300ms for datasets up to 90 days
- Table sort/filter: < 200ms

DATA FETCHING:
- Cache GET requests: 30s stale-while-revalidate for analytics
- Real-time data (live feed, wallet balance): WebSocket or 10s polling
- Use React Query (TanStack Query) for all server state
- Optimistic updates for all mutations (update UI immediately, rollback on error)

BUNDLE:
- Initial JS bundle: < 150KB gzipped
- Route-based code splitting (every major section is a separate chunk)
- Lazy load: charts, Monaco editor, Framer Motion
- Images: Next.js Image component; WebP format; lazy loading

LARGE DATA:
- Tables: virtual scrolling for > 100 rows
- Charts: aggregate/downsample data server-side for ranges > 90 days
- Audit log: cursor-based pagination (not offset)
```

---

## 24. AI-Specific UX Patterns

These patterns are unique to AI cost and governance products. Apply them consistently.

### 24.1 Cost Always Visible

```
Principle: Cost should be visible in context, not buried in analytics.

Apply to:
- Request log rows: show cost per request inline
- Model selector dropdowns: show estimated cost per 1K tokens next to each model
- Routing rule creation: show "estimated savings/month" as user configures conditions
- Prompt editor: show token count + estimated cost per call in real time
- IDE extension: show cost before AND after each request

Format in dropdowns:
  gpt-4o           $0.005/1K out   ←
  gpt-4o-mini      $0.0006/1K out  ← clearly cheaper
  claude-haiku     $0.00025/1K out ← cheapest
```

### 24.2 Savings Framing

```
Principle: Always frame optimization as savings, never as restriction.

DO:
  "Smart routing saved your team $2,400 this month"
  "Switching to gpt-4o-mini for this task type saves ~$1,200/month"
  "Cache hit — saved $0.0089 on this request"

DON'T:
  "gpt-4o is blocked for your team"
  "You've used 80% of your budget"
  "Request denied — insufficient funds"

INSTEAD:
  "gpt-4o-mini used instead — 86% cheaper for this task"
  "Heads up: 80% of budget used — 8 days remaining"
  "Budget reached — request a top-up to continue"
```

### 24.3 Latency Awareness

```
Always pair cost data with latency data.
Users optimize for cost/quality/speed — they need all three.

Model comparison table format:
  Model            Cost/1K   Latency P50   Quality Score
  gpt-4o           $0.005    842ms         94/100
  claude-sonnet    $0.003    961ms         93/100
  gpt-4o-mini      $0.0006   412ms         87/100  ← sweet spot callout

Callout: "Best value: gpt-4o-mini — 87% quality at 12% of gpt-4o cost, and 2x faster"
```

### 24.4 Provider Health Transparency

```
Always show provider health in context where provider matters.

In provider selector dropdown:
  ● OpenAI    Healthy    842ms avg
  ● Anthropic Healthy    961ms avg
  ⚠ Gemini   Degraded   4,120ms avg  ← visual callout

On dashboard: provider health strip (like a status bar)
On routing rules page: show which providers are currently healthy
On any failover event: toast notification with explanation
```

### 24.5 Request Context

```
When showing individual requests in logs, always include:
1. Cost (what it cost)
2. Model used vs model requested (show if routing changed it)
3. Cache hit/miss (was this a fresh call or served from cache?)
4. Latency (how fast)
5. Team + feature attribution (why was this called?)
6. Policy actions taken (if any security or budget action fired)

Example request row in log:
  [gpt-4o-mini] $0.0012  412ms  Cache MISS  Engineering / email-summarizer
  (Requested: gpt-4o — rerouted by "Premium Gating" rule)
```

### 24.6 Budget Psychology

```
Progress bars should trigger appropriate urgency at the right thresholds.
Never cry wolf — only surface alerts that require action.

0–79%:   Normal — blue bar, no alert icon
80–89%:  Soft warning — amber bar, amber dot on nav icon, optional digest mention
90–99%:  Warning — orange bar, badge on nav, proactive Slack message
100%:    Blocked — red bar, persistent banner, Slack message, email
>100%:   Overdraft — red bar extended beyond end, explicit overdraft badge

Progress bar labels:
  "63% used — $18,580 remaining — resets in 11 days"
  Never just show a percentage without context of what it means.
```

### 24.7 Model Selection UX

```
Anywhere a model is selected, provide context:

Model picker dropdown structure:
  ── OpenAI ────────────────
  gpt-4o          [Best quality]  $0.005/1K  842ms
  gpt-4o-mini     [Best value]    $0.0006/1K  412ms  ★ Recommended
  ── Anthropic ─────────────
  claude-sonnet   [Strong reason] $0.003/1K   961ms
  claude-haiku    [Fastest]       $0.00025/1K 280ms
  ── Current routing ───────
  Smart routing (let AI Orchestrator decide) ← default option

  Selecting "Smart routing" shows: "Will automatically choose the best model
  based on your routing rules. Estimated avg cost: $0.00082/request"
```

---

## Screen Index

| Screen | Route | Priority | Section |
|--------|-------|----------|---------|
| Sign In | /auth/signin | 🔴 P0 | §3.1 |
| Sign Up | /auth/signup | 🔴 P0 | §3.2 |
| Onboarding | /onboarding | 🔴 P0 | §4 |
| Dashboard Home | / | 🔴 P0 | §5 |
| Cost Analytics | /analytics/cost | 🔴 P0 | §6 |
| Wallet Management | /wallets | 🔴 P0 | §7 |
| Budget Transfers | /wallets/transfers | 🟠 P1 | §7 |
| Routing Rules | /routing | 🟠 P1 | §8 |
| Routing Test | /routing/test | 🟠 P1 | §8 |
| Security & Policies | /security | 🟠 P1 | §9 |
| Audit Log | /audit | 🟠 P1 | §10 |
| Prompt Registry | /prompts | 🟡 P2 | §11 |
| Provider Management | /providers | 🔴 P0 | §12 |
| Team Management | /team | 🔴 P0 | §13 |
| API Key Management | /keys | 🔴 P0 | §14 |
| Notifications | /notifications | 🟠 P1 | §15 |
| Experiments | /experiments | 🟡 P2 | §16 |
| Settings | /settings | 🟠 P1 | §17 |
| Admin Panel | /admin | 🟡 P2 | §18 |

---

## Build Order for Developers

```
WEEK 1-2: Auth + Shell
  /auth/signin → /auth/signup → /onboarding → Layout + Sidebar

WEEK 3-4: Core MVP Screens
  / (Dashboard) → /wallets → /providers → /keys → /team

WEEK 5-6: Analytics + Control
  /analytics/cost → /routing → /notifications → /settings

WEEK 7-8: Governance
  /security → /audit → /routing/test

WEEK 9-10: Power Features
  /prompts → /experiments → /wallets/transfers

WEEK 11-12: Polish + Admin
  Empty states → Mobile → Accessibility → /admin
```

---

*AI Orchestrator UI/UX Spec v1.0 — February 2026*
*Reference: AI_Orchestrator_PRD_MASTER.md + AI_Orchestrator_TASKS.md*
*This document is the source of truth for all frontend decisions.*
*When a design decision is not covered here, default to: Datadog-level precision, Linear-level polish.*