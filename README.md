# Attorney Joke Bot

A weekly dose of humor for attorneys, automatically posted to LinkedIn every Monday morning. Powered by Claude AI. Built in the spirit of attorney well-being.

> Lawyers experience some of the highest rates of depression and burnout of any profession. This is a small, lighthearted effort to bring a moment of levity to the legal community each week.

---

## How It Works

Every Monday at 9am ET, a GitHub Actions workflow:
1. Calls the Claude API to generate a fresh, tasteful joke about attorney life
2. Posts it to LinkedIn automatically

No servers. No maintenance. Just jokes.

---

## Setup

### Prerequisites
- A GitHub account
- An [Anthropic API key](https://console.anthropic.com)
- A LinkedIn account with a Developer App (see below)

### 1. Fork or clone this repo

### 2. Get your Claude API key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key under **API Keys**
3. Add ~$5 in credits (will last months at this usage level)

### 3. Set up LinkedIn API access
1. Go to [linkedin.com/developers/apps/new](https://www.linkedin.com/developers/apps/new)
2. Create an app — name it anything, attach your LinkedIn profile
3. Under the **Products** tab, request access to **"Share on LinkedIn"**
4. Under the **Auth** tab, add this redirect URL: `https://oauth.pstmn.io/v1/callback`
5. Go to the [OAuth Token Generator](https://www.linkedin.com/developers/tools/oauth/token-generator)
6. Select your app, check `w_member_social`, `openid`, and `profile` scopes
7. Click **Request access token** and authorize
8. Copy the access token

### 4. Add secrets to GitHub
In your repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Claude API key |
| `LINKEDIN_ACCESS_TOKEN` | Your LinkedIn access token |

### 5. Test it
Go to **Actions → Weekly Attorney Joke → Run workflow** to trigger a manual run and verify everything works.

---

## Maintenance

LinkedIn access tokens expire every **60 days**. When that happens, repeat step 3 (just the token generator part) and update the `LINKEDIN_ACCESS_TOKEN` secret in GitHub. Takes about 2 minutes.

---

## Customizing the Joke Prompt

Want to adjust the tone or style? Edit the prompt in `post_joke.py` inside the `generate_joke()` function.

---

## License

MIT — see [LICENSE](LICENSE)
