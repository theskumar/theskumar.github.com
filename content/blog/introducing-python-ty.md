+++
title = "ty: Astral's Take on Python Type Checking"
date = "2025-05-09"
description = "Notes on ty, the pre-alpha type checker from the team behind Ruff and uv, and what its speed, its missing plugin system, and its open business model actually mean."
tags = [
    "python",
    "type-checking",
    "tools"
]
+++

Anyone who has run `mypy` on a real codebase knows the workarounds. You enable the daemon, you keep the incremental cache warm, you scope the check to the files you touched, and you still wait a few seconds for the editor to catch up after a rename. In CI it is worse, because the cache is cold and the full run can stretch into the minutes. None of this is broken, exactly. It is just the cost you learn to pay. So when a new checker says the wait can mostly go away, I pay attention, but I also want to know what it costs.

That checker is `ty` ([gh:astral-sh/ty](https://github.com/astral-sh/ty)), from Astral, the same people who built the Ruff linter and the `uv` package manager. It is pre-alpha, version `0.0.0a6`, and not something you should put in production. But it is already worth talking about, partly for what it does and partly for what it deliberately leaves out.

## Speed Is The Headline

The numbers people are reporting are large. One user saw mypy take 18 seconds where `ty` finished the same check in about half a second. Another compared `ty` at 2.5 seconds against Pyright at 13.6 seconds on a 100k line codebase. Some users assumed it had failed, because nothing that finishes that fast could have actually looked at their whole project.

Ruff did the same thing to linting a few years ago. It was fast enough that the linter stopped being a separate step you ran and became something that just happened while you wrote code. `ty` looks like it wants to do that for type checking. That matters more than it sounds. A check that takes a minute is a thing you run in CI and forget about. A check that runs in milliseconds is a thing your editor can run on every save, and that changes how it feels to write Python at all.

## Fast And Frequently Wrong, For Now

Speed is the easy part. Being correct is the hard part, and here `ty` is still young.

The Astral developers say this plainly: it is pre-alpha, many of the errors it reports may be wrong, and the feature set is small. Right now it does diagnostics and go-to-type-definition, and not much else. One user ran it on a codebase where Pyright reported 10 diagnostics, all correct, and `ty` reported 1,599. That is not a small gap. Type inference is the thing that takes years to get right, and `ty` has not had years.

I would not read those 1,599 diagnostics as a verdict on the project. A count like that is rarely 1,599 distinct bugs; it is usually a handful of inference patterns the checker gets wrong, multiplied across every file that hits them. Fix the pattern and the count collapses. What you are looking at is a checker that is fast first and accurate later. Given what Astral did with Ruff and uv, betting against the accuracy catching up seems unwise. But it has not caught up yet, and you should treat the output accordingly.

## It Is Entering A Crowded Field

`ty` is not arriving to an empty room. It joins mypy, Microsoft's Pyright and Pylance, and Facebook's Pyrefly, which also builds on Ruff's parser despite being a separate project.

What makes all of these hard is Python itself. TypeScript was built with static typing in mind. Python's type hints arrived later and grew unevenly, bolted onto a dynamic language, with the inconsistencies you would expect from something added after the fact. On top of that, the libraries people actually use are the hardest cases. Django and SQLAlchemy lean heavily on metaprogramming and runtime code generation, which is exactly the kind of thing a static checker cannot see. The ecosystem mostly papered over this with type stubs and plugins: SQLAlchemy 2.0 added real typed mappings, and Django users lean on `django-stubs`, which is a mypy plugin. Hold onto that detail, because it runs straight into the next decision.

## No Plugins, On Purpose

This is where Astral makes a real choice rather than a faster one. mypy lets libraries ship plugins so the checker can understand their metaprogramming. `ty` will not have plugins. Astral treats the interchangeability of type checking as a feature: a check should mean the same thing across tools and projects, and it should not depend on a plugin that one checker has and another does not. Instead they plan to support the popular libraries directly in the tool.

That is a trade, not a free win. The Django user relying on `django-stubs` today is relying on exactly the plugin mechanism `ty` is choosing not to have, so until Astral supports those libraries directly, that user has no escape hatch. More work falls on Astral, and the libraries they have not reached yet are simply not understood. But it also means you do not end up with type checking that only works inside one vendor's setup, and that division is worth defending.

They are also borrowing from Rust's compiler for their diagnostics, aiming for error messages that explain rather than just flag. An LSP server and a VS Code plugin are planned, though there is no release date for either.

## The Question That Always Comes Back

Astral is a VC-backed company, and the same question hangs over `ty` as over Ruff and uv: how does this get paid for. The code is open source and has outside contributors, but at some point the money has to come from somewhere.

People guess at CI products, private repositories, or enterprise services. Astral, for now, seems to be building the tools first and leaving monetization for later. That has earned them a lot of goodwill in the Python community, and it should also keep you a little cautious, because the terms you adopt a tool under are not always the terms you keep it under.

## Trying It

If you want to look at it yourself:

```
uv tool install ty
```

Or without installing anything:

```
uvx ty check
```

Keep in mind that it is pre-alpha. Expect rough edges, and do not trust a red diagnostic until you have checked it by hand.

I do not know yet whether `ty` becomes the type checker people reach for. The speed is real, the missing plugin system is a deliberate stance and not an oversight, and the accuracy is not there yet. What I want from it is the thing Ruff already delivered: a tool fast enough to disappear into the edit loop, honest enough to trust, and open enough that adopting it does not quietly hand someone a lever over my workflow. The first of those is here. The other two are still being written.
