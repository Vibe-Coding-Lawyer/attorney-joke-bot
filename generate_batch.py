import anthropic
import json
import os
import sys


JOKES_FILE = os.path.join(os.path.dirname(__file__), "jokes.json")


def generate_jokes(count=10):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"Generating {count} jokes...")
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=200 * count,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Write {count} attorney dad jokes. Rules:\n"
                    "- True dad jokes: short setup, obvious groan-worthy punchline built on a pun or wordplay\n"
                    "- Light and silly — NOT about burnout, suffering, overwork, or dark themes\n"
                    "- Every joke must have a DIFFERENT setup format — no two jokes can start with the same words\n"
                    "- Every joke must cover a DIFFERENT topic from this list: legalese, objections, depositions, "
                    "law school, courtroom, contracts, the bar exam, legal briefs, subpoenas, discovery, "
                    "paralegals, legal fees, motions, the jury, the judge, settlement, appeals, affidavits\n"
                    "- The worse the pun, the better\n"
                    "- Format: number each joke 1. through {count}., joke text only, no extra commentary"
                ),
            }
        ],
    )

    raw = message.content[0].text.strip()
    jokes = []
    for line in raw.split("\n"):
        line = line.strip()
        if line and line[0].isdigit() and ". " in line:
            joke_text = line.split(". ", 1)[1].strip()
            jokes.append(joke_text)
        elif jokes:
            jokes[-1] += "\n" + line

    jokes = [j.strip() for j in jokes if j.strip()]
    for i, joke in enumerate(jokes):
        print(f"  [{i+1}/{len(jokes)}] {joke[:80]}...")

    return jokes


def load_backlog():
    if not os.path.exists(JOKES_FILE):
        return []
    with open(JOKES_FILE, "r") as f:
        return json.load(f)


def save_backlog(backlog):
    with open(JOKES_FILE, "w") as f:
        json.dump(backlog, f, indent=2)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    backlog = load_backlog()
    next_id = max((j["id"] for j in backlog), default=0) + 1

    new_jokes = generate_jokes(count)

    for joke in new_jokes:
        backlog.append({
            "id": next_id,
            "joke": joke,
            "rating": None,
            "commentary": None,
            "posted": False,
            "date_posted": None,
        })
        next_id += 1

    save_backlog(backlog)
    print(f"\nAdded {count} jokes to jokes.json.")
    print("Open jokes.json, read each joke, and set your rating (0.0-5.0) for each one.")
    print("The weekly post will only use jokes that have a rating set.")
