import anthropic
import requests
import json
import os
import sys
from datetime import date


JOKES_FILE = os.path.join(os.path.dirname(__file__), "jokes.json")


def load_backlog():
    if not os.path.exists(JOKES_FILE):
        print("jokes.json not found. Run generate_batch.py first.")
        sys.exit(1)
    with open(JOKES_FILE, "r") as f:
        return json.load(f)


def save_backlog(backlog):
    with open(JOKES_FILE, "w") as f:
        json.dump(backlog, f, indent=2)


def get_next_joke(backlog):
    for joke in backlog:
        if not joke["posted"] and joke["rating"] is not None:
            return joke
    return None


def generate_reaction(client, score):
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=30,
        messages=[
            {
                "role": "user",
                "content": (
                    f"The chuckle score for an attorney dad joke is {score}/5. "
                    "Write one short deadpan reaction to this score. "
                    "Under 6 words. Dry, self-aware, never a cliche. "
                    "Examples: 'It's trying.' / 'Progress.' / 'We'll get there.' / 'The bot is not sorry.' "
                    "Return only the reaction line, nothing else."
                ),
            }
        ],
    )
    return message.content[0].text.strip()


def get_reaction(client, entry):
    if entry.get("commentary"):
        return entry["commentary"]
    return generate_reaction(client, entry["rating"])


def build_post(joke, rating, reaction):
    reaction = reaction[0].upper() + reaction[1:] if reaction else reaction
    return (
        f"I built an attorney joke bot. Here's what it served up this week:\n\n"
        f"{joke}\n\n"
        f"---\n\n"
        f"Chuckle score: {rating}/5\n"
        f"{reaction}\n\n"
        f"Anyone else building weird little things for lawyers? Share in the comments!\n\n"
        f"#LegalTech #LawyerHumor #AttorneyLife"
    )


def get_person_id(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("sub")
    else:
        print(f"Failed to fetch person ID: {response.status_code} {response.text}")
        sys.exit(1)


def post_to_linkedin(text, person_id, access_token):
    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202504",
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
        print(f"Failed to post: {response.status_code}")
        print(response.text)
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

    print("Getting reaction line...")
    reaction = get_reaction(client, entry)

    post = build_post(entry["joke"], entry["rating"], reaction)
    print(f"\nFull post:\n{post}\n")

    print("Fetching LinkedIn person ID...")
    person_id = get_person_id(access_token)

    print("Posting to LinkedIn...")
    post_to_linkedin(post, person_id, access_token)

    entry["posted"] = True
    entry["date_posted"] = date.today().isoformat()
    save_backlog(backlog)
    print(f"Marked joke #{entry['id']} as posted.")
