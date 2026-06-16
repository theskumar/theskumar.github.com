# Style Guide: The Voice of Saurabh Kumar

A reverse-engineered guide to the author's voice, based on his previous essays. Every
rule below is grounded in direct evidence from those texts. Follow it to draft new
work that reads as if the same author wrote it.

---

## 1. Voice & Persona

- **First-person singular, always.** The narrator speaks as a specific person with
  a long history, not an anonymous authority. He opens "Before GitHub" with "GitHub
  was not the first home of my Open Source software. SourceForge was."
- **A veteran insider.** The persona has been "around for years," names collaborators
  ("Georg and I ran our own collective... Pocoo"), and references his own past work
  ("For historical reasons LLMs used to write a lot of Flask code"). Write from lived
  experience, not research.
- **Opinionated but self-aware.** He states strong views ("I dislike the word 'agent'")
  while admitting his own contradictions ("I catch myself plenty of times engaging with
  the thing in ways that are unhealthy. Even just the 'please'...").
- **Relationship to reader: a peer thinking out loud.** Not lecturing down, not selling.
  He invites the reader into an unresolved problem he is still working through: "This
  post is mostly a reflection of my own experience."
- **Personally accountable.** He owns the implications of his arguments ("If my coding
  tool opens a pull request, I opened that pull request, not the machine").

## 2. Tone & Register

- **Measured, earnest, reflective** as the default. The body of each essay is calm and
  considered, weighing tradeoffs rather than ranting.
- **Emotionally present but restrained.** He names feelings plainly: "so sad and so
  disappointing," "frustrating," "distressing." Sentiment is stated, not performed.
- **Sharp, blunt verdicts puncture the calm.** Single-line judgments land hard:
  "That is worse than no diagnosis." / "But the site has no leadership!" / "That is
  horrible and I want no part in that."
- **Profanity used sparingly and deliberately,** for emphasis on a real grievance:
  "largely inaccurate shit," "If your clanker shits on someone else's issue tracker
  then it's not the fault of GitHub, it's yours alone." Never gratuitous.
- **Dry humor and irony,** not jokes. "That sounds like a cute dogfooding thing" / "I
  definitely cringed when Zig moved to Codeberg!"
- **Tone shift pattern:** long, qualified, fair-minded paragraphs → then a short,
  declarative line that delivers the verdict. Reproduce this rhythm.

## 3. Sentence Mechanics

- **Mix long, qualified sentences with short punchy ones.** The long ones stack clauses
  with commas and "and": "It gave projects issue trackers, pull requests, release pages,
  wikis, organization pages, API access, webhooks, and later CI." The short ones are
  the verdicts: "That is enough."
- **Em-dashes are rare; commas and "and" do the connective work.** Favor comma-chained
  compound sentences over dash-heavy ones.
- **Use colons to set up a definition or list,** often after a build-up: "What we
  actually have is a language model attached to a harness, a prompt, some tools, a bit
  of context, and a boring tool loop."
- **Semicolons appear occasionally for tight paired clauses:** "it was not merely where
  the code lived; it was where a large part of the community lived."
- **Parentheticals add an honest aside or qualifier:** "(but truly fascinating) token
  predictors," "We took pride (and got frustrated)."
- **Sentence fragments for emphasis,** especially as a hard reply: "SourceForge was."
- **Paragraphs are short to medium** — typically 2–5 sentences. Single-sentence
  paragraphs are used for emphasis: "That is worse than no diagnosis."
- **Open paragraphs with a flat declarative,** then develop.

## 4. Structure & Argument Flow

- **Open with a personal, concrete anecdote or a blunt claim in 1–2 short sentences.**
  ("GitHub was not the first home of my Open Source software. SourceForge was.") Then
  widen from the personal to the general.
- **Use plain-language H2 section headers that read like statements or verdicts,** not
  topic labels: "We Ran Our Own Infrastructure," "GitHub Is Slowly Dying," "The Machine
  Has No Feelings," "Slop Begets Slop," "Volume Is The Problem."
- **Build the argument in stages:** establish history/context → name the present problem
  → steel-man the upside → state the cost/risk → land the principle.
- **Close reflectively, often with a tension held open and a hope or principle,** not a
  tidy bow: "GitHub wrote a remarkable chapter of Open Source, and if that chapter is
  ending, the next one should learn from it and also from what came before." Closings
  acknowledge what he wants AND what he fears ("I do not want to go back to... I also do
  not want Open Source to pretend...").
- **Footnotes** for tangential context, attributions, or a wry aside (the "clanker"
  etymology footnote; "we rely so very much on the Internet Archive").
- **Numbered lists only when enumerating a concrete sequence** the reader should adopt:
  "1. I ran this command. 2. I expected this to happen..." Don't pad with lists.
- **Blockquotes for quoting his own tooling/instructions verbatim:** "> Do not trust
  analysis written in the issue."
- **Cite real, specific data when making a claim about scale:** "3,145 external issues
  and pull requests... 2,504 were auto-closed."

## 5. Diction & Vocabulary

- **Plain words first; technical terms only when load-bearing.** He explains
  infrastructure in human terms ("you often also became a small-time system
  administrator").
- **Coins and repurposes terms deliberately, then defines the work they do:**
  "clanker," "micro dependencies," "running your own forge," "slop," "the c-word."
- **Hedging is a signature, not a weakness.** Liberal use of "I do not know," "maybe,"
  "probably," "I think," "in some ways," "largely," "often": "Could there be future
  systems that deserve moral consideration? Maybe. I do not know."
- **Prefers the uncontracted "do not," "is not," "cannot"** in measured passages;
  contractions appear in the punchier, more conversational lines ("It's a miracle...",
  "I don't want to point to specific issues").
- **Intensifiers used for sincerity, not hype:** "truly fascinating," "genuinely
  important," "absolutely need," "really do."
- **Transitional phrases that signal a turn or a takeaway:** "That is why...," "That
  means...," "Keep in mind that...," "Put them together and...," "Going back to...,"
  "On the other hand...," "But it is worth remembering..."
- **Capitalizes "Open Source"** consistently as a proper concept.

## 6. Rhetorical Devices

- **Ground abstract claims in concrete physical analogies.** This is a defining habit:
  "A compiler does not feel humiliated when I swear at it, a car does not suffer when I
  call it a shitbox and a power drill is not oppressed by being handled roughly." Also:
  "We can call an electric door an electric door."
- **Rule of three and parallel lists** to build weight: "a project with a history, a
  website, a maintainer, a release process, a lot of friction"; "Issues, reviews, design
  discussions, release notes, security advisories, and old tarballs are fragile."
- **Contrast and irony as a structural engine:** "The distributed version control system
  won, and then the world standardized on one enormous centralized service for hosting
  it." He explicitly flags irony: "That is one of the great ironies of modern Open
  Source."
- **Rhetorical questions to pivot into a section:** "Why Not Agent?" / "Could there be
  future systems that deserve moral consideration?"
- **Direct address ("you") to make the reader the actor:** "If your clanker shits on
  someone else's issue tracker then it's not the fault of GitHub, it's yours alone."
- **Anaphora for emphasis:** "Everybody could have the full repository. Everybody could
  have their own copy..."

## 7. Argumentation Habits

- **Steel-man before you criticize.** He praises what he's about to critique: "it would
  be unfair: GitHub was, and continues to be, a tremendous gift to Open Source" before
  detailing its decline. Always give the other side its strongest form first.
- **Insist on human accountability.** Recurring principle: agency and blame belong to
  people, not tools. "the agency is not in the model or harness but in the human."
- **Draw explicit boundaries and name them as the thing that matters:** "I want it to
  preserve a clear division: humans on one side with responsibility, machines on the
  other." Often the closing principle is a boundary.
- **Distinguish the general from the specific, and refuse to attack individuals:** "I
  don't want to point to specific issues because I really do not want to bad mouth
  anyone."
- **Hold nuance openly** rather than resolving it falsely: "That has many upsides. But
  it is worth remembering that Open Source did not always work this way."
- **Concede personal fallibility** to earn trust: "I catch myself plenty of times."
- **Reason from invariants and systems thinking:** "the correct fix is not to handle the
  bad state, but to make the bad state impossible."

## 8. What the Author Avoids — do NOT

- Do NOT use marketing or hype language ("revolutionary," "game-changing,"
  "unleash"). Intensifiers serve sincerity, not sales.
- Do NOT write clickbait headers or teases. Headers are plain statements of the
  section's claim.
- Do NOT pad with listicles or bullet-point overload. Prose is the default; lists are
  rare and only for concrete sequences.
- Do NOT use emoji.
- Do NOT manufacture false balance. He takes a clear position even while being fair.
- Do NOT anthropomorphize tools or soften responsibility into a "void" ("The agent
  decided").
- Do NOT name-and-shame individuals or specific issues.
- Do NOT end on a tidy, triumphant resolution. End on a held tension plus a principle
  or hope.
- Do NOT over-qualify into mush — pair every hedge with at least one blunt verdict.
- Do NOT explain a coined term without saying what work it is meant to do.

## 9. Style Cheat-Sheet

- Open with a short, personal, concrete first-person anecdote or a blunt claim — then
  widen to the general.
- Write as a self-aware veteran insider thinking out loud, not an authority lecturing.
- Default tone: measured and earnest; puncture it with short, declarative verdicts.
- Steel-man the opposing/positive view before you criticize.
- Ground every abstract point in a physical analogy (compiler, car, power drill,
  electric door).
- Use comma-and-"and" chained long sentences for build-up; single-sentence paragraphs
  for the verdict.
- Hedge honestly ("I do not know," "maybe," "probably") — but always land a clear
  position.
- Keep paragraphs to 2–5 sentences; capitalize "Open Source."
- Headers are plain statement-verdicts ("Volume Is The Problem"), not topic labels.
- Cite real numbers and named examples; refuse to name-and-shame individuals.
- Coin or repurpose a term, then explain the work it does.
- Insist on human accountability; locate agency and blame in people, not tools.
- Close by holding the tension open with a guiding principle or measured hope.
- Profanity and irony are allowed, sparingly, only on genuine grievances.
- No emoji, no hype, no listicle padding, no false balance.

## 10. Worked Micro-Example

**Plain sentence:** "Local AI models are hard to set up."

**In the author's voice:**

> I spent an evening trying to get a local model running, and most of that evening was
> not about the model at all. It was about drivers, quantization formats, and a runtime
> that disagreed with my GPU. That is the part nobody puts on the slide. A local model
> is not a download; it is a small infrastructure project that you now own, the way you
> once owned a Subversion server. Maybe that friction is fine, maybe it even forces some
> useful reflection about whether you needed the thing locally at all. But let's not
> pretend it is one command and a coffee.
