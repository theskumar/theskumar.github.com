+++
title = "Redis’s License Change and the Valkey Fork"
date = "2026-01-12"
description = "The story of Redis's controversial license change in March 2024 and how the open-source community responded by creating Valkey—a fork that's now outperforming the original on speed and efficiency."
tags = [
    "open-source",
    "databases",
    "redis",
    "valkey",
    "performance"
]
+++

## The License Change

On March 20, 2024, Redis Inc. announced a switch from the BSD 3-clause license to dual source-available licensing: RSALv2 and SSPLv1. The new licensing takes effect with Redis 7.4 and restricts how the code can be offered as a service.

I see this as a loss for the open-source community, even if Redis Inc. considers it a business necessity.

## The Thing About Open Source

Redis was created by Salvatore Sanfilippo in 2009, known as "antirez" in the community. He built Redis to solve a simple problem: web applications were slow because databases couldn't keep up. What if, instead of storing data on disk, you kept everything in memory? What if you made it blazingly fast?

Redis became legendary. By 2024, it was everywhere—caching layers for social media platforms, session stores for e-commerce sites, real-time analytics for financial systems. Developers loved it. Not just because it was fast, but because it was _theirs_. They could use it, modify it, deploy it however they wanted.

Then Redis Inc. changed the rules.

## The Rebellion

Kyle Davis, a longtime Redis contributor, said something interesting after the split: "From this point forward, Redis and Valkey are two different pieces of software." Not just different licenses—different software.

**Just eight days later, on March 28, 2024**, something remarkable happened. The Linux Foundation announced Valkey, a fork starting from Redis 7.2.4, the last truly open version. But this wasn't some ragtag group of angry developers. This was AWS, Google Cloud, Oracle, Ericsson, and Snap Inc.—companies with deep pockets and deeper technical expertise.

They weren't just copying Redis and giving it a new name. They were going to _improve_ it.

## The Performance Revolution

Here's where the story gets interesting, because it stops being about philosophy and starts being about engineering.

Redis, for all its speed, had a design constraint: it was single-threaded. Salvatore made this choice deliberately. Single-threading avoids all the complexity of concurrent programming—no locks, no race conditions, no debugging nightmares. For years, this was fine. Processors were getting faster, and Redis was fast enough.

But by 2024, we're not making processors faster anymore—we're making them wider. Your laptop has eight cores, maybe sixteen. Your cloud server has dozens. And Redis, with its elegant single-threaded design, was using... one.

The Valkey team saw their opportunity.

**Valkey 8.0, released on September 15, 2024**, introduced enhanced multi-threaded I/O. Not for the core data operations—those stayed single-threaded to preserve Redis's simplicity and safety—but for network operations, for handling connections, for moving data in and out.

The results were dramatic. In benchmarks on AWS hardware, Valkey 8.0 hit 1.19 million requests per second. That's 230% more than Valkey 7.2. That's the kind of improvement that makes CTOs take notice.

But the engineers didn't stop there.

## The Memory Game

**Valkey 8.1, released on March 31, 2025**, arrived with something even more impressive: a complete redesign of how data is stored in memory.

The team rebuilt the hash table—the fundamental data structure at the heart of any key-value store—using modern algorithms inspired by Google's "Swiss Tables" design. Every key-value pair now uses about 20-30 bytes less memory. That might not sound like much, but scale it up.

When researchers tested Valkey 8.1 against Redis 8.2 with 50 million entries, Valkey consumed 3.77 GB while Redis used 4.83 GB. That's a 28% reduction. For a company running terabytes of cached data across hundreds of servers, that's not just impressive—it's millions of dollars in annual savings.

## The Feature Race

Of course, efficiency isn't everything. Redis Inc. didn't just sit back and watch. **In May 2025, Redis released version 8.0**, bundling their enterprise features—JSON support, vector search for AI applications, time series databases—directly into the core product. These are sophisticated capabilities that took years to develop.

Valkey's roadmap is playing catch-up here. Version 8.1 added JSON and Bloom filters. Vector search support became available through the valkey-search module. Time series support is planned. But there's still a gap.

This is the classic innovator's dilemma: Redis has more features _today_. Valkey has better fundamentals and a trajectory that suggests they'll have those features _tomorrow_—and they'll run faster when they do.

## The Cloud Complication

Here's where it gets messy. When you go to AWS and spin up what was formerly called "Redis," you might now get Valkey. Same with Google Cloud's Memorystore.

These managed services have their own quirks and limitations, shaped by what the cloud providers choose to support. The result? More fragmentation.

Managed Redis-compatible services now include both projects, with different feature sets and provider support.

## The Choice

So where does this leave developers in 2026?

If you're starting a new project, Valkey offers true open-source freedom, better performance on multi-core systems, and superior memory efficiency. You sacrifice some advanced features, but its BSD license permits use, modification, and redistribution under its terms.

If you need those advanced features _right now_—vector search for AI applications, sophisticated time series analysis, enterprise support—Redis has them. But you're accepting the terms Redis Inc. sets, and those terms have already changed once.

For existing Redis deployments, the calculation is harder. Migration costs are real. But so is the risk of depending on a vendor that rewrote the rules mid-game.

## My Take

Valkey started with an established codebase and backing from major companies, including AWS, Google Cloud, Oracle, Ericsson, and Snap Inc. Its performance and memory work give developers reasons to evaluate it beyond the license.

I prefer Valkey’s permissive licensing and foundation governance. To me, the fork shows why the ability to keep developing an existing open-source codebase matters when a vendor changes terms. Both projects continue to evolve, and the choice still depends on features, migration costs, and workload measurements.
