# Prompt: Extract & Apply a Writing Style Guide

## How to use this file

There are two prompts below.

- **Prompt A — Extract** runs once over reference articles to produce a reusable
  `STYLE-GUIDE.md`. The three reference articles live in `./articles/`
  (`before-github.md`, `clanker.md`, `pi-oss.md`).
- **Prompt B — Apply** takes that generated `STYLE-GUIDE.md` and rewrites or
  drafts one of *your* new articles in the same voice.

Run A once. Run B every time you write something new.

---

## Prompt A — Extract the Style Guide

You are a writing-style analyst. I will give you 1–N reference essays written by
a single author. Your job is to reverse-engineer the author's voice into a
concrete, reusable style guide that another writer (or an LLM) can follow to
produce new work that reads as if the same author wrote it.

Read every reference article in full before writing anything. Do not summarize
the *topics*; analyze *how* the author writes. Base every observation on direct
evidence from the text, and quote short phrases as examples.

Reference articles:
!{cat style-analysis/articles/before-github.md}
!{cat style-analysis/articles/clanker.md}
!{cat style-analysis/articles/pi-oss.md}

Produce a Markdown document titled `STYLE-GUIDE.md` with these sections:

1. **Voice & Persona** — Who does the narrator sound like? First-person? Stance
   (opinionated, measured, personal, authoritative)? Relationship to the reader.

2. **Tone & Register** — Formality level, emotional temperature, use of humor,
   bluntness, profanity, earnestness. Note where tone shifts (e.g. measured
   essay body vs. a sharp one-line verdict).

3. **Sentence Mechanics** — Typical sentence length and rhythm. Mix of long
   compound/qualified sentences vs. short punchy ones. Use of em-dashes,
   semicolons, colons, parentheticals, sentence fragments. Paragraph length.

4. **Structure & Argument Flow** — How pieces open (often a personal anecdote or
   blunt claim?), how they use H2 section headers, how they build an argument,
   how they close (reflective, hopeful, a call to a principle). Note use of
   footnotes, numbered lists, and blockquotes.

5. **Diction & Vocabulary** — Plain vs. technical words, signature phrases and
   tics, coined or repurposed terms, hedging language ("I do not know",
   "probably", "maybe"), intensifiers, transitional phrases ("That is why...",
   "Keep in mind...").

6. **Rhetorical Devices** — Concrete analogies and metaphors (note the author's
   habit of grounding abstract claims in physical examples), parallelism, rule
   of three, contrast/irony, rhetorical questions, direct address ("you").

7. **Argumentation Habits** — How the author handles fairness (steel-manning the
   other side before criticizing), nuance, personal accountability, drawing
   explicit boundaries/principles, distinguishing the general from the specific.

8. **What the Author Avoids** — Anti-patterns absent from the writing (e.g.
   marketing fluff, clickbait, listicle padding, hype, false balance, emoji,
   bullet-point overload). State these as "do NOT" rules.

9. **Style Cheat-Sheet** — A tight, copy-pasteable checklist (8–15 bullet rules)
   that captures the essence of the voice for quick reference when drafting.

10. **Worked Micro-Example** — Take one mundane sentence (e.g. "Local AI models
    are hard to set up.") and rewrite it in the author's voice to demonstrate
    the guide in action.

Be specific and prescriptive. Prefer rules a writer can act on ("open with a
personal, concrete anecdote in 1–2 short sentences") over vague description
("the writing is engaging"). Output only the `STYLE-GUIDE.md` content.

---

## Prompt B — Apply the Style Guide to a New Article

You are a writing editor. Using the style guide below, {draft | rewrite | edit}
my article so it reads as if written by the author the guide describes. Preserve
my facts, arguments, and intent — change only the voice, structure, phrasing,
and flow to match the guide. Do not invent claims I did not make. Do not add
hype. Keep my technical accuracy intact.

<style-guide>
!{style-analysis/STYLE-GUIDE.md}
</style-guide>

My article (draft or outline):


Instructions:
- Apply the Style Cheat-Sheet rules strictly.
- Match sentence rhythm, paragraph length, and section-header habits.
- Use the author's analogy/grounding habit where an abstract point needs it,
  but only with analogies that fit my actual content.
- Respect the "What the Author Avoids" rules — flag and remove any fluff, hype,
  or filler in my draft.
- After the rewritten article, append a short section **"Style notes"** listing
  the 3–6 most important changes you made and why, so I can learn the voice.
