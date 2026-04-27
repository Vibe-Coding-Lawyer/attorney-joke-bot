import requests
import json
import os
import sys
from datetime import date


JOKES_FILE = os.path.join(os.path.dirname(__file__), "jokes.json")
POSTS_FILE = os.path.join(os.path.dirname(__file__), "posts.json")


def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, "r") as f:
        return json.load(f)


def append_post_log(entry, post_text):
    posts = load_posts()
    next_id = posts[-1]["id"] + 1 if posts else 1
    posts.append({
        "id": next_id,
        "date": entry["date_posted"],
        "joke_id": entry["id"],
        "hook_technique": entry.get("hook_technique", ""),
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

    print("Loading joke backlog...")
    backlog = load_backlog()

    entry = get_next_joke(backlog)
    if not entry:
        print("No rated jokes available in the backlog. Run generate_batch.py and add ratings.")
        sys.exit(1)

    post_text = entry.get("post_text")
    if not post_text:
        print(f"Joke #{entry['id']} has no post text. Run generate_posts.py locally first.")
        sys.exit(1)

    print(f"Using joke #{entry['id']}: {entry['joke'][:80]}...")
    print(f"Your rating: {entry['rating']}/5")

    print("Fetching LinkedIn person ID...")
    person_id = get_person_id(access_token)

    print("Posting to LinkedIn...")
    post_to_linkedin(post_text, person_id, access_token)

    entry["posted"] = True
    entry["date_posted"] = date.today().isoformat()
    save_backlog(backlog)
    verify_posted(entry["id"])
    print(f"Marked joke #{entry['id']} as posted.")

    append_post_log(entry, post_text)
    print("Post logged to posts.json.")
