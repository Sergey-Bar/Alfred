# Alfred Notifications Setup Guide

Complete setup instructions for all notification integrations.

## 📋 Table of Contents

- [Overview](#overview)
- [Slack Setup](#-slack-setup)
- [Microsoft Teams Setup](#-microsoft-teams-setup)
- [Telegram Setup](#-telegram-setup)
- [WhatsApp Business Setup](#-whatsapp-business-setup)
- [Configuration Reference](#-configuration-reference)
- [Event Types](#-event-types)
- [Testing Notifications](#-testing-notifications)
- [Troubleshooting](#-troubleshooting)

---

## Overview

Alfred supports sending notifications to multiple platforms when important events occur:

| Event | Description |
|-------|-------------|
| Quota Warning | User reaches 80%+ of their quota |
| Quota Exceeded | Request denied due to insufficient quota |
| Credit Reallocation | Credits reallocated between users |
| Approval Requested | New quota increase request submitted |
| Approval Resolved | Request approved or rejected |
| Vacation Status | User starts/ends vacation mode |

### Supported Platforms

| Platform | Method | Rich Formatting |
|----------|--------|-----------------|
| Slack | Webhooks | Block Kit |
| Microsoft Teams | Webhooks | Adaptive Cards |
| Telegram | Bot API | MarkdownV2 |
| WhatsApp | Business Cloud API | Templates |

---

## 💬 Slack Setup

### Step 1: Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name it (e.g., "Alfred Alerts") and select your workspace
4. Click **Create App**

### Step 2: Enable Incoming Webhooks

1. In your app settings, go to **Incoming Webhooks**
2. Toggle **Activate Incoming Webhooks** to **On**
3. Click **Add New Webhook to Workspace**
4. Select the channel for notifications (e.g., `#ai-usage-alerts`)
5. Click **Allow**
6. Copy the **Webhook URL** (looks like: `https://hooks.slack.com/services/T00.../B00.../xxx...`)

### Step 3: (Optional) Create Alerts Channel

For critical alerts, repeat Step 2 for a separate channel (e.g., `#ai-critical-alerts`).

### Step 4: Configure Alfred

Add to your `.env` file:

```env
# Required - paste your webhook URL from Step 2
SLACK_WEBHOOK_URL=<paste-your-webhook-url-here>

# Optional: Separate channel for critical alerts
SLACK_ALERTS_WEBHOOK_URL=<paste-alerts-webhook-url-here>

# Optional: Bot token for advanced features (user mentions)
SLACK_BOT_TOKEN=xoxb-your-bot-token
```

### Slack Message Preview

```
🚫 Quota Exceeded

John Developer's request was denied due to insufficient quota

👤 User: John Developer
👥 Team: Engineering

Details:
• Requested Credits: 15.50
• Available Credits: 2.30
• Shortfall: 13.20

⚠️ ERROR | 2026-02-11 15:30 UTC
Alfred | Event: a1b2c3d4
```

---

## 👥 Microsoft Teams Setup

### Step 1: Add Incoming Webhook Connector

1. Open Microsoft Teams
2. Go to the channel where you want notifications
3. Click the **⋯** (three dots) next to the channel name
4. Select **Connectors** (or **Manage Channel** → **Connectors**)
5. Search for **Incoming Webhook**
6. Click **Configure**

### Step 2: Create Webhook

1. Enter a name (e.g., "Alfred Alerts")
2. Optionally upload an icon
3. Click **Create**
4. Copy the **Webhook URL**
5. Click **Done**

### Step 3: (Optional) Create Alerts Webhook

Repeat for a separate channel for critical alerts.

### Step 4: Configure Alfred

Add to your `.env` file:

```env
# Required
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/IncomingWebhook/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy/zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz

# Optional: Separate webhook for critical alerts
TEAMS_ALERTS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### Teams Message Preview

Messages appear as rich Adaptive Cards with:
- Color-coded headers (green/orange/red based on severity)
- Fact sets for metadata
- Event details in organized sections

---

## 📱 Telegram Setup

### Step 1: Create a Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name (e.g., "Alfred Alerts")
4. Choose a username (must end in `bot`, e.g., `alfred_alerts_bot`)
5. Save the **HTTP API token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

#### For Personal Chat:
1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message to it
3. It will reply with your **Chat ID** (a number like `123456789`)

#### For Group Chat:
1. Add your bot to the group
2. Send a message in the group
3. Open: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find the `"chat":{"id":-XXXXXXXXXX}` - that negative number is your group chat ID

#### For Channel:
1. Add your bot as an admin to the channel
2. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
3. The forwarded message info contains the channel ID (starts with `-100`)

### Step 3: Test the Bot

Run this command to verify (replace with your values):

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<CHAT_ID>", "text": "Alfred test message!"}'
```

### Step 4: Configure Alfred

Add to your `.env` file:

```env
# Required
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890

# Optional: Separate chat for critical alerts
TELEGRAM_ALERTS_CHAT_ID=-1009876543210
```

### Telegram Message Preview

```
🚫 *Quota Exceeded*

John Developer's request was denied due to insufficient quota

👤 *User:* John Developer
👥 *Team:* Engineering

*Details:*
• Requested Credits: `15.50`
• Available Credits: `2.30`
• Shortfall: `13.20`

_⚠️ ERROR | 2026-02-11 15:30 UTC_
_Alfred | Event: a1b2c3d4_
```

---

## 📲 WhatsApp Business Setup

> ⚠️ **Important**: WhatsApp Business API requires a Meta Business account and approved message templates for business-initiated messages.

### Step 1: Create Meta Business Account

1. Go to [business.facebook.com](https://business.facebook.com)
2. Create a Business Account if you don't have one
3. Complete business verification (may take 1-3 days)

### Step 2: Set Up WhatsApp Business API

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app or use existing
3. Add **WhatsApp** product to your app
4. Go to **WhatsApp** → **Getting Started**
5. Note your:
   - **Phone Number ID** (e.g., `123456789012345`)
   - **WhatsApp Business Account ID**

### Step 3: Generate Access Token

1. In Meta Developer Console, go to **WhatsApp** → **Configuration**
2. Under **Temporary Access Token**, click **Generate**
3. Copy the token (valid for 24 hours)

For permanent tokens:
1. Go to **Business Settings** → **System Users**
2. Create a System User with `whatsapp_business_messaging` permission
3. Generate a token for that user

### Step 4: Create Message Template (Required for Business-Initiated Messages)

> WhatsApp requires pre-approved templates when messaging users who haven't messaged you in the last 24 hours.

1. Go to [business.facebook.com/wa/manage/message-templates](https://business.facebook.com/wa/manage/message-templates)
2. Click **Create Template**
3. Choose **Utility** category
4. Create a template like:

**Template Name:** `alfred_alert`

**Header:** None (or Text: "Alfred Alert")

**Body:**
```
{{1}}

{{2}}

User: {{3}}
Time: {{4}}
```

**Variables:**
- `{{1}}` = Title (e.g., "Quota Exceeded")
- `{{2}}` = Message
- `{{3}}` = User name
- `{{4}}` = Timestamp

5. Submit for approval (usually takes minutes to hours)

### Step 5: Add Test Phone Number

1. In WhatsApp Developer Console, go to **Getting Started**
2. Under **To**, add phone numbers you want to message
3. Verify each number with the code sent via WhatsApp

### Step 6: Configure Alfred

Add to your `.env` file:

```env
# Required
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WHATSAPP_RECIPIENT_NUMBER=14155551234

# Optional: Separate recipient for critical alerts
WHATSAPP_ALERTS_RECIPIENT_NUMBER=14155559999

# Optional: Template for business-initiated messages
WHATSAPP_TEMPLATE_NAME=alfred_alert
```

### Phone Number Format

- Include country code
- No `+`, spaces, or dashes
- Example: `14155551234` for +1 (415) 555-1234

### WhatsApp Message Preview

```
🚫 *Quota Exceeded*

John Developer's request was denied due to insufficient quota

👤 *User:* John Developer
👥 *Team:* Engineering

• *Requested Credits:* 15.50
• *Available Credits:* 2.30
• *Shortfall:* 13.20

_⚠️ ERROR | 2026-02-11 15:30 UTC_
_Alfred_
```

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| **Global** | | |
| `NOTIFICATIONS_ENABLED` | No | Enable/disable all notifications (default: `true`) |
| `NOTIFY_QUOTA_WARNING_THRESHOLD` | No | Percentage to trigger warning (default: `80`) |
| `NOTIFY_ON_QUOTA_EXCEEDED` | No | Notify when quota exceeded (default: `true`) |
| `NOTIFY_ON_APPROVAL_REQUEST` | No | Notify on new approvals (default: `true`) |
| `NOTIFY_ON_VACATION_CHANGE` | No | Notify on vacation status (default: `true`) |
| **Slack** | | |
| `SLACK_WEBHOOK_URL` | Yes* | Primary webhook URL |
| `SLACK_ALERTS_WEBHOOK_URL` | No | Webhook for critical alerts |
| `SLACK_BOT_TOKEN` | No | Bot token for advanced features |
| **Teams** | | |
| `TEAMS_WEBHOOK_URL` | Yes* | Primary webhook URL |
| `TEAMS_ALERTS_WEBHOOK_URL` | No | Webhook for critical alerts |
| **Telegram** | | |
| `TELEGRAM_BOT_TOKEN` | Yes* | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes* | Target chat/group/channel ID |
| `TELEGRAM_ALERTS_CHAT_ID` | No | Chat for critical alerts |
| **WhatsApp** | | |
| `WHATSAPP_PHONE_NUMBER_ID` | Yes* | Business phone number ID |
| `WHATSAPP_ACCESS_TOKEN` | Yes* | Meta Graph API token |
| `WHATSAPP_RECIPIENT_NUMBER` | Yes* | Recipient phone number |
| `WHATSAPP_ALERTS_RECIPIENT_NUMBER` | No | Recipient for critical alerts |
| `WHATSAPP_TEMPLATE_NAME` | No | Approved template name |

*Required only if using that provider

---

## 📨 Event Types

| Event | Trigger | Severity |
|-------|---------|----------|
| `QUOTA_WARNING` | User at 80%+ of quota | Warning |
| `QUOTA_EXCEEDED` | Request denied | Error |
| `QUOTA_RESET` | Quota refilled | Info |
| `TOKEN_TRANSFER_SENT` | User sent tokens to another | Info |
| `TOKEN_TRANSFER_RECEIVED` | User received tokens from another | Info |
| `APPROVAL_REQUESTED` | New approval request | Info |
| `APPROVAL_APPROVED` | Request approved | Info |
| `APPROVAL_REJECTED` | Request rejected | Warning |
| `USER_VACATION_START` | User starts vacation | Info |
| `USER_VACATION_END` | User ends vacation | Info |
| `USER_SUSPENDED` | Account suspended | Error |
| `TEAM_POOL_WARNING` | Team pool at threshold | Warning |
| `TEAM_POOL_DEPLETED` | Team pool empty | Error |
| `SYSTEM_ERROR` | Provider/system error | Critical |
| `HIGH_LATENCY` | API latency high | Warning |

---

## 🧪 Testing Notifications

### Test via Python

```python
import asyncio
from app.integrations import (
    get_notification_manager,
    setup_notifications,
    NotificationEvent,
    EventType
)
from app.config import settings

# Setup providers
setup_notifications(
    slack_webhook_url=settings.slack_webhook_url,
    teams_webhook_url=settings.teams_webhook_url,
    telegram_bot_token=settings.telegram_bot_token,
    telegram_chat_id=settings.telegram_chat_id,
    whatsapp_phone_number_id=settings.whatsapp_phone_number_id,
    whatsapp_access_token=settings.whatsapp_access_token,
    whatsapp_recipient_number=settings.whatsapp_recipient_number,
)

# Create test event
event = NotificationEvent(
    event_type=EventType.QUOTA_WARNING,
    title="Test Notification",
    message="This is a test from Alfred!",
    user_name="Test User",
    severity="info",
    data={"test": "value"}
)

# Send
async def test():
    manager = get_notification_manager()
    results = await manager.emit(event)
    print(results)

asyncio.run(test())
```

### Test via API

```bash
# Trigger a quota warning by making requests until 80% used
# Or manually call the emit functions in your code
```

---

## 🔧 Troubleshooting

### Slack

| Issue | Solution |
|-------|----------|
| 404 Not Found | Webhook URL is invalid or deleted. Recreate the webhook. |
| 403 Forbidden | App not installed in workspace. Reinstall the app. |
| Messages not appearing | Check the channel in webhook settings. |

### Teams

| Issue | Solution |
|-------|----------|
| 400 Bad Request | Adaptive Card may have invalid format. Check for JSON errors. |
| Webhook not working | Connectors may be disabled by admin. Check org settings. |

### Telegram

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Invalid bot token. Regenerate via @BotFather. |
| 400 chat not found | Bot not added to chat, or wrong chat ID. |
| Messages not in group | Enable "Group Privacy" in @BotFather → /mybots → Bot Settings. |

### WhatsApp

| Issue | Solution |
|-------|----------|
| 400 Error | Phone number not verified, or outside 24h window without template. |
| Template not found | Template not approved yet, or name misspelled. |
| 403 Forbidden | Access token expired or insufficient permissions. |

---

## 🔗 Quick Links

- [Slack API Documentation](https://api.slack.com/messaging/webhooks)
- [Teams Webhooks Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

---

**Need help?** [Open an issue](https://github.com/your-org/alfred/issues) on GitHub!

