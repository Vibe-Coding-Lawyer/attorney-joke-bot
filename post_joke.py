import anthropic
import requests
import json
import os
import sys
from datetime import date


JOKES_FILE = os.path.join(os.path.dirname(__file__), "jokes.json")
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")


def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, "r") as f:
        return json.load(f)


def append_post_log(entry, post_text):
    posts = load_posts()
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
    next_id = posts[-1]["id"] + 1 if posts else 1
    posts.append({
        "id": next_id,
        "date": entry["date_posted"],
        "joke_id": entry["id"],
        "hook_technique": state.get("last_hook_technique", ""),
        "chuckle_score": entry["rating"],
        "post": post_text,
    })
    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=2)


def load_backlog():
    if not os.path.exists(JOKES_FILE):
        print("jokes.json not found. Run generate_batch.py first.")
        sys.exit(1)
    with open(JOKES_FILE, "r") as f:
        return json.load(f)


def save_backlog(backlog):
    with open(JOKES_FILE, "w") as f:
        json.dump(backlog, f, indent=2)


def verify_posted(joke_id):
    with open(JOKES_FILE, "r") as f:
        backlog = json.load(f)
    for joke in backlog:
        if joke["id"] == joke_id:
            if not joke["posted"] or not joke["date_posted"]:
                print(f"ERROR: Joke #{joke_id} was not saved as posted. Halting.")
                sys.exit(1)
            return
    print(f"ERROR: Joke #{joke_id} not found in jokes.json after save. Halting.")
    sys.exit(1)


def get_next_joke(backlog):
    for joke in backlog:
        if not joke["posted"] and joke["rating"] is not None:
            return joke
    return None


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_hook_technique": ""}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def generate_post(client, entry):
    state = load_state()
    last_technique = state.get("last_hook_technique", "")
    commentary = entry.get("commentary", "")
    if commentary:
        commentary = commentary[0].upper() + commentary[1:]
        if not commentary.endswith("."):
            commentary += "."

    prompt = f"""You are generating a weekly LinkedIn post for an attorney joke bot series.

AUDIENCE: Lawyers curious about AI, and developers/legal tech builders. Both should finish reading thinking "I could try that."

POST FORMAT — use exactly this structure, including spacing:

[HOOK LINE 1]
[HOOK LINE 2]

I built an attorney joke bot. Here's what it served up this week:

"{entry['joke']}"

--
Chuckle score: {entry['rating']}/5. {commentary}
--

[BODY: 2-3 short paragraphs, reader-focused]

[CLOSING QUESTION]

#LegalTech #LawyerHumor #AttorneyLife #LegalEngineering

HOOK RULES:
- Exactly 2 short sentences, ~55 characters each
- Never opens with "I" or a personal achievement
- No emojis, no hashtags
- Creates an open loop the reader must close
- Last technique used: "{last_technique}" — do NOT reuse it
- Pick one of these techniques:
  1. Contradiction — say something that sounds wrong
  2. Specific number + unexpected context
  3. Direct accusation — call the reader out
  4. Stolen thought — say what the reader secretly thinks
  5. Absurd reframe — make something mundane dramatic

BODY RULES:
- Never leads with "I built" or personal achievement framing
- Reframe the joke and score as something the READER can learn from
- Tone: warm, self-deprecating, technically credible
- 2-3 short paragraphs max

ATTRIBUTION:
- The bot only generates jokes
- The chuckle score and commentary are Veronica's — never attribute them to the bot

CLOSING QUESTION:
- One line, directed at the reader
- Answerable by both a lawyer and a developer
- Not rhetorical

Your response must start with: TECHNIQUE: [name of technique used]
Then a blank line, then the full post. Nothing else."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )

    response = message.content[0].text.strip()
    lines = response.split("\n", 2)
    technique = lines[0].replace("TECHNIQUE:", "").strip()
    post = lines[2].strip() if len(lines) > 2 else response

    state["last_hook_technique"] = technique
    save_state(state)

    return post


def get_person_id(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sub")
    else:
        print(f"Failed to fetch person ID: HTTP {response.status_code}")
        sys.exit(1)


def post_to_linkedin(text, person_id, access_token):
    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202601",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": f"urn:li:person:{person_id}",
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in (200, 201):
        print("Successfully posted to LinkedIn!")
    else:
        print(f"Failed to post: HTTP {response.status_code}")
        sys.exit(1)


if __name__ == "__main__":
    access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("Loading joke backlog...")
    backlog = load_backlog()

    entry = get_next_joke(backlog)
    if not entry:
        print("No rated jokes available in the backlog. Run generate_batch.py and add ratings.")
        sys.exit(1)

    print(f"Using joke #{entry['id']}: {entry['joke'][:80]}...")
    print(f"Your rating: {entry['rating']}/5")

    print("Generating post...")
    post = generate_post(client, entry)

    print("Fetching LinkedIn person ID...")
    person_id = get_person_id(access_token)

    print("Posting to LinkedIn...")
    post_to_linkedin(post, person_id, access_token)

    entry["posted"] = True
    entry["date_posted"] = date.today().isoformat()
    save_backlog(backlog)
    verify_posted(entry["id"])
    print(f"Marked joke #{entry['id']} as posted.")

    append_post_log(entry, post)
    print("Post logged to posts.json.")
