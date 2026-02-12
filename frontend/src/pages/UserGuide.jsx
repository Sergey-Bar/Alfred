import {
    BookOpenIcon,
    UserPlusIcon,
    UserGroupIcon,
    ArrowsRightLeftIcon,
    KeyIcon,
    CogIcon,
    CheckCircleIcon,
    ExclamationTriangleIcon,
    LinkIcon,
} from '@heroicons/react/24/outline';

const sections = [
    {
        id: 'getting-started',
        title: 'Getting Started',
        icon: BookOpenIcon,
        content: [
            {
                title: 'What is Alfred?',
                description: 'Alfred is an enterprise AI Credit Governance Platform for B2B organizations managing shared API credit pools. When companies purchase bulk API quotas from OpenAI, Azure, Anthropic, or Google, Alfred provides the missing governance layer: user quotas, team budgets, vacation reallocation, approval workflows, and efficiency tracking.'
            },
            {
                title: 'Why B2B Only?',
                description: 'Alfred requires enterprise/API-level accounts with shared credit pools. Consumer subscriptions ($20/month ChatGPT Plus, etc.) cannot be managed\u2014they are identity-locked with no transferable credits. Only organizations with API access have the "shared bucket" architecture that Alfred governs.'
            },
            {
                title: 'Key Features',
                list: [
                    'Credit pool governance with per-user quotas',
                    'Real-time usage tracking and cost analytics',
                    'Admin-controlled credit reallocation',
                    'Automatic vacation release to team pool',
                    'Priority overrides for critical projects',
                    'Privacy mode for sensitive requests',
                    'Multi-provider support via LiteLLM (100+ providers)',
                    'Integrations with Make, Slack, Teams, Telegram, WhatsApp',
                    'Manager approval workflow for quota requests'
                ]
            },
            {
                title: 'Supported LLM Providers',
                list: [
                    'Public APIs: OpenAI (GPT-4o, o1), Anthropic (Claude 3.5), Google (Gemini)',
                    'Enterprise Cloud: Azure OpenAI, AWS Bedrock, Google Vertex AI',
                    'Self-Hosted: vLLM (Llama 3.1, Mixtral), TGI, Ollama'
                ]
            }
        ]
    },
    {
        id: 'authentication',
        title: 'Authentication',
        icon: KeyIcon,
        content: [
            {
                title: 'API Keys',
                description: 'Each user receives a unique API key when their account is created. This key is used to authenticate all API requests. API keys start with "tp-" prefix.'
            },
            {
                title: 'Using Your API Key',
                code: `# Set your API key as an environment variable
export ALFRED_API_KEY="tp-your-api-key-here"

# Or use it directly in requests
curl https://your-alfred-server/v1/chat/completions \\
  -H "Authorization: Bearer $ALFRED_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "Hello"}]}'`
            },
            {
                title: 'Dashboard Access',
                description: 'Administrators can access this dashboard using their API key. Enter it on the login page to manage users, teams, and view analytics.'
            }
        ]
    },
    {
        id: 'users',
        title: 'Managing Users',
        icon: UserPlusIcon,
        content: [
            {
                title: 'Creating Users',
                steps: [
                    'Navigate to "Manage Users" in the sidebar',
                    'Click "Add User" button',
                    'Fill in the user details (name, email, quota)',
                    'Click "Create User" - an API key will be generated',
                    'Share the API key securely with the user'
                ]
            },
            {
                title: 'User Quotas',
                description: 'Each user has a personal quota measured in tokens. When a user makes an API request, their quota is reduced by the token count. When quota reaches zero, requests are blocked until the quota resets or additional tokens are allocated.'
            },
            {
                title: 'User Status',
                list: [
                    'Active - User can make API requests normally',
                    'On Vacation - User shares quota with their team',
                    'Suspended - User cannot make API requests'
                ]
            }
        ]
    },
    {
        id: 'teams',
        title: 'Managing Teams',
        icon: UserGroupIcon,
        content: [
            {
                title: 'Creating Teams',
                steps: [
                    'Navigate to "Manage Teams" in the sidebar',
                    'Click "Add Team" button',
                    'Enter team name, description, and pool quota',
                    'Click "Create Team"'
                ]
            },
            {
                title: 'Team Pools',
                description: 'Teams have a shared pool quota that members can draw from when their personal quota is exhausted. This enables flexible resource sharing within teams. The pool is shared equally among all active members.'
            },
            {
                title: 'Adding Members',
                steps: [
                    'Open the team details',
                    'Click "Add Member" button',
                    'Select users to add to the team',
                    'Optionally grant admin privileges'
                ]
            }
        ]
    },
    {
        id: 'transfers',
        title: 'Credit Reallocation',
        icon: ArrowsRightLeftIcon,
        content: [
            {
                title: 'How Reallocation Works',
                description: 'Admins and authorized users can reallocate credits from their allocated quota to other users. This enables dynamic budget management when project needs change or when team members need additional capacity.'
            },
            {
                title: 'Reallocating Credits via API',
                code: `curl -X POST https://your-alfred-server/v1/users/me/transfer \\
  -H "Authorization: Bearer $ALFRED_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "recipient_email": "colleague@company.com",
    "amount": 500,
    "reason": "Project deadline support"
  }'`
            },
            {
                title: 'Reallocation Rules',
                list: [
                    'You can only reallocate from your allocated quota',
                    'Cannot reallocate more than your available balance',
                    'All reallocations are logged for audit compliance',
                    'Recipients receive notification of incoming credits'
                ]
            }
        ]
    },
    {
        id: 'api-usage',
        title: 'API Usage',
        icon: CogIcon,
        content: [
            {
                title: 'Making Requests',
                description: 'Alfred is compatible with the OpenAI API format. Simply point your existing code to your Alfred server instead of OpenAI directly.',
                code: `from openai import OpenAI

# Point to your Alfred server
client = OpenAI(
    api_key="tp-your-api-key",
    base_url="https://your-alfred-server/v1"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)`
            },
            {
                title: 'Special Headers',
                list: [
                    'X-Privacy-Mode: strict - Prevents message logging',
                    'X-Priority: critical - Bypasses quota limits for urgent requests',
                    'X-Project-ID: <id> - Associates request with a project for tracking'
                ]
            },
            {
                title: 'Checking Your Quota',
                code: `curl https://your-alfred-server/v1/users/me/quota \\
  -H "Authorization: Bearer $ALFRED_API_KEY"

# Response:
# {
#   "personal_quota": 10000,
#   "used_tokens": 3500,
#   "available_quota": 6500,
#   "team_pool_available": 15000
# }`
            }
        ]
    },
    {
        id: 'integrations',
        title: 'Integrations',
        icon: LinkIcon,
        content: [
            {
                title: 'Available Integrations',
                description: 'Alfred supports connecting with external services for notifications and automation. Configure integrations through the Integrations page in the sidebar.',
                list: [
                    'Make (Integromat) - Workflow automation via webhooks',
                    'Slack - Send notifications to Slack channels',
                    'Microsoft Teams - Teams channel notifications',
                    'Telegram - Bot-based notifications',
                    'WhatsApp - Business API notifications'
                ]
            },
            {
                title: 'Setting Up an Integration',
                steps: [
                    'Navigate to "Integrations" in the sidebar',
                    'Click on the service you want to connect',
                    'Enter the required credentials (webhook URL, API key, etc.)',
                    'Click "Add Integration"',
                    'Use the "Test Connection" button to verify it works'
                ]
            },
            {
                title: 'Managing Integrations',
                list: [
                    'Enable/disable integrations with the toggle switch',
                    'Test connections anytime with the refresh button',
                    'Remove integrations by clicking the trash icon',
                    'Green badge = Connected, Yellow = Pending test, Red = Error'
                ]
            }
        ]
    }
];

export default function UserGuide() {
    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">User Guide</h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                    Learn how to use Alfred to manage your AI token quotas
                </p>
            </div>

            {/* Quick Navigation */}
            <div className="card dark:bg-gray-800 mb-8">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Navigation</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {sections.map((section) => (
                        <a
                            key={section.id}
                            href={`#${section.id}`}
                            className="flex items-center p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                        >
                            <section.icon className="h-5 w-5 text-[#1d3557] dark:text-blue-400 mr-2" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{section.title}</span>
                        </a>
                    ))}
                </div>
            </div>

            {/* Sections */}
            <div className="space-y-8">
                {sections.map((section) => (
                    <div key={section.id} id={section.id} className="card dark:bg-gray-800 scroll-mt-4">
                        <div className="flex items-center mb-4">
                            <div className="p-2 bg-[#1d3557] rounded-lg mr-3">
                                <section.icon className="h-6 w-6 text-white" />
                            </div>
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{section.title}</h2>
                        </div>

                        <div className="space-y-6">
                            {section.content.map((item, index) => (
                                <div key={index} className="border-l-2 border-gray-200 dark:border-gray-600 pl-4">
                                    <h3 className="font-semibold text-gray-800 dark:text-gray-100 mb-2">{item.title}</h3>

                                    {item.description && (
                                        <p className="text-gray-600 dark:text-gray-300 text-sm">{item.description}</p>
                                    )}

                                    {item.list && (
                                        <ul className="list-disc list-inside text-gray-600 dark:text-gray-300 text-sm space-y-1">
                                            {item.list.map((li, i) => (
                                                <li key={i}>{li}</li>
                                            ))}
                                        </ul>
                                    )}

                                    {item.steps && (
                                        <ol className="list-decimal list-inside text-gray-600 dark:text-gray-300 text-sm space-y-1">
                                            {item.steps.map((step, i) => (
                                                <li key={i}>{step}</li>
                                            ))}
                                        </ol>
                                    )}

                                    {item.code && (
                                        <pre className="mt-2 p-3 bg-gray-900 text-gray-100 rounded-lg text-xs overflow-x-auto">
                                            <code>{item.code}</code>
                                        </pre>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {/* Help Section */}
            <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start">
                    <CheckCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                    <div>
                        <h3 className="font-medium text-blue-800 dark:text-blue-200">Need More Help?</h3>
                        <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                            Check the project documentation on{' '}
                            <a
                                href="https://github.com/your-org/alfred"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-semibold underline hover:text-blue-500 dark:hover:text-blue-200"
                            >
                                GitHub
                            </a>
                            {' '}or contact your system administrator for additional support.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
