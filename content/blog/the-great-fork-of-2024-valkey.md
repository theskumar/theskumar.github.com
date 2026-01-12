+++
title = "The Great Fork: How Redis Lost Its Soul and Valkey Found It"
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

## The Moment Everything Changed

Picture this: It's March 2024, and somewhere in a conference room, executives at Redis Inc. are making a decision. They're looking at their balance sheets, watching cloud giants like AWS and Google profit from offering managed Redis services, and they're thinking: _This isn't fair. We built this. Why are they making all the money?_

So they pull the trigger. **On March 20, 2024**, after fifteen years of operating under the BSD 3-clause license—one of the most permissive licenses in open source—they announce a switch to dual source-available licensing: RSALv2 and SSPLv1. The new licensing takes effect with Redis 7.4. The message is simple: you can still see our code, but if you want to build a business with it, we need our cut.

It's a reasonable position from a business perspective. It's also, in the eyes of the open-source community, a betrayal.

## The Thing About Open Source

Here's what most people don't understand about open source: it's not just a licensing model. It's a social contract. When you release code under a permissive license, you're making a promise. You're saying: "I trust you with this. Build whatever you want. Make it better. Make money if you can. Just keep it free for everyone else."

Redis didn't invent this contract—it inherited it. The database was created by Salvatore Sanfilippo in 2009, a brilliant Italian developer known as "antirez" in the community. He built Redis to solve a simple problem: web applications were slow because databases couldn't keep up. What if, instead of storing data on disk, you kept everything in memory? What if you made it blazingly fast?

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

Think about what this means: Redis chose restrictive licensing to capture more value. Valkey responded by making their product so efficient that users would need _less_ infrastructure to run it.

## The Feature Race

Of course, efficiency isn't everything. Redis Inc. didn't just sit back and watch. **In May 2025, Redis released version 8.0**, bundling their enterprise features—JSON support, vector search for AI applications, time series databases—directly into the core product. These are sophisticated capabilities that took years to develop.

Valkey's roadmap is playing catch-up here. Version 8.1 added JSON and Bloom filters. Vector search support became available through the valkey-search module. Time series support is planned. But there's still a gap.

This is the classic innovator's dilemma: Redis has more features _today_. Valkey has better fundamentals and a trajectory that suggests they'll have those features _tomorrow_—and they'll run faster when they do.

## The Cloud Complication

Here's where it gets messy. When you go to AWS and spin up what was formerly called "Redis," you might now get Valkey. Same with Google Cloud's Memorystore.

These managed services have their own quirks and limitations, shaped by what the cloud providers choose to support. The result? More fragmentation.

Redis wanted to stop cloud providers from free-riding on their work. Instead, they accelerated the diversification they were trying to prevent. Now "Redis" no longer means one thing—it's like trying to define "Linux" when every major company has its own distribution.

## What This Really Means

Step back from the technical details for a moment. What we're watching is a fundamental question being answered in real time: **Can you take back open source?**

Redis Inc. believed the answer was yes. They thought they could change the rules, monetize their position, and the community would follow because the switching costs were too high.

They were wrong.

The switching costs _were_ high—high enough that major tech companies invested millions in Valkey rather than accept Redis's new terms. And those companies didn't just fork the code; they poured engineering resources into making Valkey genuinely better.

This is the hidden power of open source. It's not just that the code is free. It's that betrayal is expensive. When you break the social contract, you don't just lose users—you lose the collective goodwill that made your project valuable in the first place.

## The Choice

So where does this leave developers in 2026?

If you're starting a new project, Valkey offers true open-source freedom, better performance on multi-core systems, and superior memory efficiency. You sacrifice some advanced features, but you gain certainty: Valkey will always be yours to use however you need.

If you need those advanced features _right now_—vector search for AI applications, sophisticated time series analysis, enterprise support—Redis has them. But you're accepting the terms Redis Inc. sets, and those terms have already changed once.

For existing Redis deployments, the calculation is harder. Migration costs are real. But so is the risk of depending on a vendor that rewrote the rules mid-game.

## The Lesson

Malcolm Gladwell wrote in "David and Goliath" that disadvantages can become advantages when you're forced to think differently. Redis had every advantage: market dominance, name recognition, years of development, a mature ecosystem.

Valkey started with nothing but the code and a principle.

Less than two years later, Valkey is faster, more efficient, and governed by a foundation that can't unilaterally change its license. The fork is outperforming the original on the metrics that matter most for production systems.

This is what happens when you forget that in technology, loyalty isn't purchased with licensing terms—it's earned with trust. Redis Inc. spent fifteen years building that trust, then tested it severely in a single decision.

The great fork of 2024 wasn't just about software. It was a reminder that in open source, the community doesn't just contribute code. The community _is_ the moat. Lose them, and you lose everything that made you valuable.

Valkey succeeded not because they had better lawyers or smarter business strategies, but because they remembered what Redis momentarily forgot: **the code was never the point. The promise was.**

And when that promise breaks, the community doesn't just complain—they build something better.

---

_As of January 2026, both projects continue to evolve. Valkey gains adoption while Redis Inc. pursues its enterprise strategy. The next chapter is being written in pull requests, benchmark comparisons, and architecture decisions happening in companies around the world. The outcome isn't certain, but the lesson already is: in open source, trust is your most valuable asset—and once broken, it's nearly impossible to fully rebuild._
