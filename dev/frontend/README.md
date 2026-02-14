# Dashboard & Admin UI

Alfred includes a React-based admin dashboard for monitoring and governing enterprise AI credit usage.

## Features

### Dashboard (KPIs)
- **Overview Stats**: Total users, credits consumed, costs, pending approvals
- **Credit Usage Trends**: Area chart showing daily credit consumption
- **Cost Trends**: Daily cost visualization
- **Model Usage Distribution**: Pie chart of requests by model
- **Efficiency Leaderboard**: Top users ranked by efficiency score
- **Approval Statistics**: Pending, approved, denied requests

### Admin Pages
- **Users**: View and manage user accounts, allocate quotas, set admin status
- **Teams**: Create and manage team pools, member management
- **Credit Reallocation**: View credit reallocation history between users

## Tech Stack

- **React 19** + **Vite** - Modern frontend framework
- **TailwindCSS** - Utility-first styling
- **Recharts** - Data visualization
- **React Router** - Client-side routing
- **Heroicons** - Icon library

## Development

### Prerequisites
- Node.js 18+
- npm

### Setup

```bash
cd frontend
npm install
```

### Development Mode

Run the frontend in dev mode with hot reload:

```bash
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies API requests to `http://localhost:8000`.

### Building for Production

```bash
npm run build
```

This builds the frontend into `../static/` directory, which is served by FastAPI in production.

## API Endpoints

The dashboard uses these backend endpoints:

### Dashboard KPIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/dashboard/overview` | GET | Overview statistics |
| `/v1/dashboard/users` | GET | User usage stats |
| `/v1/dashboard/teams` | GET | Team pool stats |
| `/v1/dashboard/trends?days=30` | GET | Cost/usage trends |
| `/v1/dashboard/models` | GET | Model usage breakdown |
| `/v1/dashboard/leaderboard?limit=10` | GET | Efficiency leaderboard |
| `/v1/dashboard/approvals` | GET | Approval statistics |
| `/v1/dashboard/transfers?limit=50` | GET | Recent credit reallocations |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/admin/users` | GET | List all users |
| `/v1/admin/users` | POST | Create user |
| `/v1/admin/users/{id}` | PUT | Update user |
| `/v1/admin/users/{id}` | DELETE | Delete user |
| `/v1/teams` | GET | List all teams |
| `/v1/teams` | POST | Create team |
| `/v1/teams/{id}` | PUT | Update team |
| `/v1/teams/{id}` | DELETE | Delete team |
| `/v1/teams/{id}/members` | POST | Add team member |
| `/v1/teams/{id}/members/{user_id}` | DELETE | Remove member |

## Authentication

The dashboard currently uses role-based access:

- **Admin Users**: Full access to all dashboard features
- **Regular Users**: View own stats only

Users with `is_admin=True` have global admin privileges for dashboard access.

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.jsx      # Main layout with sidebar
│   ├── pages/
│   │   ├── Dashboard.jsx   # KPI dashboard
│   │   ├── Users.jsx       # User management
│   │   ├── Teams.jsx       # Team management
│   │   └── Transfers.jsx   # Transfer history
│   ├── services/
│   │   └── api.js          # API client service
│   ├── App.jsx             # Router configuration
│   ├── main.jsx            # Entry point
│   └── index.css           # Tailwind styles
├── vite.config.js          # Vite configuration
└── package.json
```

## Customization

### Styling

Modify `src/index.css` for custom Tailwind classes:

```css
.card { @apply bg-white rounded-lg shadow-md p-6; }
.btn-primary { @apply bg-blue-600 text-white hover:bg-blue-700; }
```

### Charts

Charts use Recharts. Modify colors in `src/pages/Dashboard.jsx`:

```javascript
const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];
```

### Adding Pages

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add nav link in `src/components/Layout.jsx`

## Production Deployment

When deployed, FastAPI serves the built frontend:

1. Build the frontend: `npm run build`
2. Files are placed in `../static/`
3. FastAPI automatically serves these files
4. SPA routing is handled by the fallback route

The backend detects if `static/index.html` exists and switches between:
- **SPA Mode**: Serves React app at `/`, APIs at `/v1/`
- **API Mode**: Returns JSON info at `/`, APIs at `/v1/`

# Frontend Visual Regression Testing

## Visual Regression Testing Implementation

### 1. Playwright Screenshot Comparison
- Add Playwright screenshot assertions to E2E tests:
  ```js
  // Example in a Playwright test
  await page.goto('/dashboard');
  expect(await page.screenshot()).toMatchSnapshot('dashboard.png');
  ```
- Store baseline images in `frontend/playwright/tests/__screenshots__`.
- Review diffs in CI and update baselines as needed.

### 2. Storybook + Chromatic (Recommended)
- Install and configure Storybook for all major components:
  ```sh
  npx storybook init
  ```
- Add Chromatic for automated visual testing:
  ```sh
  npx chromatic --project-token=<your-token>
  ```
- Each PR triggers a Chromatic build and visual diff check.
- Review and approve/reject UI changes in the Chromatic dashboard.

### 3. CI Integration
- Add Playwright and Chromatic steps to your CI pipeline (GitHub Actions example):
  ```yaml
  - name: Run Playwright E2E Tests
    run: npx playwright test
  - name: Publish to Chromatic
    run: npx chromatic --project-token=${{ secrets.CHROMATIC_TOKEN }}
  ```
- Fail the build on unapproved visual diffs.

### 4. Documentation & Review
- Document the process for updating and reviewing visual baselines in the frontend README.
- Require visual review for all major UI changes as part of the PR process.

---

For more details, see the Playwright and Chromatic documentation.
