# Attorney Joke Bot — Post Generation Instructions

## Purpose
Generate the weekly LinkedIn post for the attorney joke bot series.
The goal is NOT to document what I built. The goal is to make lawyers
and developers want to build something themselves.

## Audience
- Lawyers / attorneys curious about AI
- Developers and legal tech builders
- Both should finish the post thinking: "I could try that."

## Post Structure
1. HOOK (2 lines, ~55 chars each — see hook rules below)
2. JOKE OF THE WEEK (verbatim from bot output)
3. CHUCKLE SCORE (as rated by the bot)
4. BODY (reader-focused insight — see body rules below)
5. FIXES THIS WEEK (if any — technical, plain English)
6. CLOSING QUESTION (one question directed at the reader)
7. HASHTAGS: #LegalTech #LawyerHumor #AttorneyLife #LegalEngineering

## Hook Rules
- Exactly 2 short sentences, ~55 characters each
- Must break a scrolling pattern — unexpected, counterintuitive, or
  uncomfortably specific
- Never opens with "I" or a personal achievement
- No emojis as openers, no hashtags
- Creates an open loop the reader must click to close

Before selecting a hook technique, read state.json and avoid the
technique listed in `last_hook_technique`. After drafting the post,
update `last_hook_technique` in state.json with the technique you used.

### Hook techniques (rotate weekly):
1. Contradiction — say something that sounds wrong
   e.g. "Your first AI build should be stupid. Mine posts lawyer jokes."
2. Specific number + unexpected context
   e.g. "1 weekend. 1 bot. 0 serious use cases."
3. Direct accusation — call the reader out
   e.g. "You're waiting for a brilliant AI idea. That's why you haven't built anything."
4. Stolen thought — say what reader secretly thinks
   e.g. "You think AI projects need to be impressive. They don't."
5. Absurd reframe — make something mundane dramatic
   e.g. "A joke bot taught me more about AI than any course I paid for."

## Body Rules
- Never leads with "I built" or personal achievement framing
- Reframe the bot's output as something the READER can learn from
- The joke and score are evidence, not the point
- End with: what does this mean for someone who hasn't built yet?
- Tone: warm, a little self-deprecating, technically credible

## Fixes Section (include only if fixes happened this week)
- Plain English only — no jargon without explanation
- Frame each fix as a lesson, not a changelog
- Format: what broke → why → what fixed it → what to watch for

## Closing Question
- Directed at the reader, not rhetorical
- Should be answerable by both a lawyer and a developer
- e.g. "What's the dumbest useful thing you could automate this weekend?"

## What to Avoid
- "I'm so excited to share..."
- Leading with personal milestones
- Passive calls to action ("let me know in the comments")
- Explaining what LinkedIn is or how hooks work
