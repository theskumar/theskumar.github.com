+++
title = "Pi's Session Tree Is a Lab Notebook, Not Git Branches"
date = "2026-05-29"
description = "The git branching mental model breaks down when applied to Pi's session tree. A lab notebook is a better way to think about it."
tags = [
    "ai",
    "tools",
    "pi",
    "workflow"
]
+++

[Pi coding agent](https://github.com/badlogic/pi-mono/) stores sessions as trees. Every message has an `id` and `parentId`. You can navigate to any past node with `/tree` and continue from there. It looks a lot like git branching.

It isn't.

## Where the git analogy breaks

If you already think in git, this mapping is tempting:

| Git | Pi Tree |
|-----|---------|
| `branch` | Navigate to a past node, type something new |
| `checkout` | `/tree`, select a node |
| `commit message` | Label (`Shift+L` in tree viewer) |
| `squash` | Branch summarization (automatic) |
| `merge` | ? |
| `rebase` | ? |

The last two rows are the problem. **There is no merge. There is no rebase.** Branches in pi never combine into a unified thread. If you're waiting for the moment where your exploration branches converge back into one timeline, it won't come.

This matters because the entire point of git branching is eventual convergence. You branch to isolate work, then merge it back. That mental model will leave you confused about what pi's tree is actually doing.

## A better model: the lab notebook

Think of a pi session as a lab notebook.

You have a hypothesis. You run an experiment (branch), write up results. If the experiment doesn't pan out, you flip back to the hypothesis page and try a different experiment. The experiments never merge into one experiment. But your write-ups carry forward, so the next experiment benefits from what you already learned.

The mapping:

- **Branch** = run an experiment
- **Summary** = write-up of results (not the raw data)
- **Navigate back** = return to the hypothesis, try another approach
- **Label** = bookmark a promising checkpoint
- **Fork** = results were so interesting they became a separate research project

The notebook tracks your thinking. The actual specimens (files on disk) are managed separately, by git.

## What actually happens when you switch branches

Say you're debugging a bug. You spend 20 messages going deep into the auth module. Dead end.

You open `/tree`, navigate back to the start, and try the database angle instead.

Pi does three things:

1. **Summarizes** the auth branch (what you discussed, what files changed)
2. **Injects** that summary into your new branch's context
3. **Moves the leaf pointer** to the new branch

The auth branch still exists in the session file, fully intact. You can go back anytime. But it doesn't merge into your database investigation. Instead, you get a compressed write-up: "Explored auth module for 20 messages. Ruled out token validation. Noticed the session table has no index on user_id."

That's the lab notebook in action. You carry the insight, not the 20 messages.

```
[start: investigate bug]
├── auth module exploration (20 messages, dead end)
│   └── 📋 summarized when you left
│
└── database investigation (you are here)
    ├── 📋 summary from auth branch injected
    └── found the real bug ✓
```

## When to use `/tree` vs `/fork`

These are different operations with different purposes.

**`/tree`** is for fast branch hopping within one workstream. You stay in the same session file. Use it when you want to try a different direction, test competing hypotheses, or isolate noisy exploration from your main thread.

**`/fork`** creates a new independent session. Use it when a branch becomes its own project, when you're switching to a different working directory, or when the session is getting heavy and you want a fresh start with full history.

Rule of thumb: `/tree` is flipping to a different page in the same notebook. `/fork` is starting a new notebook for a spin-off project.

## The one thing to never forget

**Pi only manages conversation state.** It does not manage files.

If both branches made file changes, that's git's job. Commit before branching. Use git to roll back file changes. The tree is for your thinking, not your code.

## Further reading

- [Pi session architecture](https://pi-handbook.whatsinfor.me/04-sessions/)
- [Tree and context management (StackToHeap)](https://stacktoheap.com/blog/2026/02/26/pi-tree-context-window-management/)
- [Armin Ronacher on pi](https://lucumr.pocoo.org/2026/1/31/pi/)
