+++
title = "Thoughts on Astral's ty: The Lightning-Fast Python Type Checker & Language Server"
date = "2025-05-09"
description = "An overview of Ty, Astral's blazingly fast Python type checker that promises to revolutionize Python development with performance that makes existing solutions look slow in comparison."
tags = [
    "python",
    "type-checking",
    "tools"
]
+++

Python developers have long suffered from painfully slow type checkers. Running mypy on a large codebase? Time to grab a coffee. Need real-time type checking in your editor? Prepare for frustrating lag and occasional crashes. But what if type checking could be nearly instantaneous?

Enter `ty` ([gh:astral-sh/ty](https://github.com/astral-sh/ty)), the latest tool from Astral—the team behind the wildly successful Ruff linter and `uv` package manager. Still in pre-alpha, `ty` is already turning heads with performance that makes existing solutions look like they're running in slow motion.

## Lightning Fast: The Need for Speed

The performance numbers are nothing short of stunning:

- One user reported `mypy` taking 18 seconds while `ty` completed the same check in just 0.5 seconds
- Another compared `ty` (2.5 seconds) to Pyright (13.6 seconds) on a 100k LOC codebase
- Some users initially thought `ty` had failed to check their entire project because it finished so quickly!

Just as Ruff revolutionized Python linting with speeds up to 100x faster than `flake8`, `ty` appears poised to do the same for type checking. And for large codebases where type checking can take minutes, this isn't just a convenience—it's a game-changer for productivity.

## Current Status: Fast but Still Maturing

Astral developers are quick to point out that `ty` is pre-alpha software (`version 0.0.0a6`) and not ready for production use. Many of the errors it reports may be incorrect, and its feature set is limited. Currently, it only supports diagnostics and go-to-type-definition, with more features planned.

One user found 1,599 diagnostics from `ty` on a codebase where Pyright found only 10 (all correct), indicating that type inference is still maturing. But given Astral's track record with Ruff and uv, there's good reason to believe these issues will be ironed out quickly.

## The Python Type Checking Landscape

`ty` isn't entering an empty field. It joins established tools like `mypy`, Microsoft's Pyright/Pylance, and Facebook's recently released Pyrefly (which, interestingly, also uses Ruff's parser despite being developed independently).

What makes the Python type checking landscape particularly challenging is the nature of Python's type system itself. Unlike TypeScript, which was designed with static typing in mind, Python's type hints evolved somewhat chaotically as a "bolted-on adhoc solution." with inconsistencies and limitations.

Moreover, popular libraries like Django and SQLAlchemy present significant challenges for type checking due to their extensive use of metaprogramming and runtime code generation.

## Astral's Unique Approach

Unlike mypy, which offers a plugin system to support libraries with complex type requirements, Ty won't support plugins. Astral sees it as a feature that type checking works interchangeably across tools and projects, and aims to implement support for popular libraries directly in the tool.

The Astral team is also focusing on making error messages more helpful, drawing inspiration from Rust's compiler for their diagnostic model and aiming for a similar quality bar. They plan to provide an LSP server and VS Code plugin, though there are no concrete release announcements for those features yet.

## The Business Model Question

As with Astral's other tools, a pertinent question remains regarding the long-term business model. The code is open source with an active community of external contributors, but as a VC-backed company, Astral will eventually need to monetize its impressive toolchain.

Speculation ranges from CI/CD products to private repositories or enterprise services, but the team appears focused on building excellent tools first and figuring out monetization later. This approach has built tremendous goodwill in the Python community, though some remain cautious about potential future changes.

## Looking Forward: The Future of Python Development

If `ty` follows the trajectory of Ruff and `uv`, it could fundamentally change how Python developers interact with their code. Real-time type checking that's actually real-time would eliminate one of the major pain points for Python development at scale.

The combination of `uv` (package management), Ruff (linting and formatting), and `ty` (type checking) represents a comprehensive overhaul of Python's developer tooling ecosystem—all created in just a few years by a single company.

For a language that's often criticized for slow tooling, this renaissance comes at a critical time as Python continues to grow in popularity, particularly in data science and machine learning where large codebases are common.

## Conclusion: A New Era for Python Tooling?

Though it's still early days for `ty`, the excitement in the Python community is palpable. The blistering speed improvements alone would be noteworthy, but coming from the team behind Ruff and uv, `ty` carries high expectations.

If you're eager to try it out yourself, you can install it with:

```
uv tool install ty
```

Or run it without installing:

```
uvx ty check
```

Just remember it's pre-alpha software, so expect some rough edges.

Whether `ty` ultimately becomes the go-to Python type checker remains to be seen, but one thing is clear: Astral is rapidly reshaping the Python development experience, and the future looks very fast indeed.

---

*What's your experience with Python type checking? Are you excited about `ty`? Let's discuss*
