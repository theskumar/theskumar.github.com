+++
title = "A Local Coding Agent On A 32 GB M1 Pro"
date = "2026-06-14"
description = "How I adapted an M1 Max guide to half the machine by handing it to pi and letting it grill me first — and the exact, reproducible steps that came out the other end."
tags = [
    "ai",
    "local-llm",
    "macos",
    "pi"
]
+++

I have been paying Anthropic for a `fast` mode in pi that points at Bedrock's Haiku 4.5. It is a good model. It is cheap, it is responsive, and it answers the kind of small, contained question I throw at it twenty times a day without complaining. It is also, of course, not mine. So when Kyle Howells [posted about getting Gemma 4 26B-A4B running locally on an M1 Max at 72 tokens per second](https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos), and the [Hacker News thread](https://news.ycombinator.com/item?id=48507020) filled up with people on smaller Macs reporting the same setup was workable, I wanted to know whether my own laptop could host that slot.

My laptop is an M1 Pro with 32 GB of unified memory. That is half the RAM and roughly half the memory bandwidth of the machine in Kyle's post. Copying his commands verbatim was never going to work. I needed to know what to change, in what order, and what to give up.

So I did not copy the commands. I gave pi the article and asked it to build me a plan for my machine — and to interrogate me before it wrote a line.

## I Handed The Guide To An LLM And Made It Grill Me

The whole thing started with one message. Typos and all, this is what I actually sent:

> Act local AI setup expert working on M1 silicon with 32GB ram. Read though [the article] and also pull all the comments on this article on news.ycombinator.com article id 48507020. I've ollama and muse already installed there are models installed as well. Prep and action plan to set this up in the most performant and maintaibale way. Not sure quite sure if i need to uninstall previous ollama app and it's modetls. Create and write a plan after analysing things. `/grill-me`

The `/grill-me` at the end is a small skill in my pi setup. It is two paragraphs of instructions that tell the model to walk down the decision tree one node at a time, recommend an answer at each step, and wait for my reply before moving on. It is not magic. It is a way of forcing the conversation I would otherwise have with myself in a notebook, except the model will not let me skip a step.

The interview was mostly the model proposing and me confirming in monosyllables. My replies, verbatim, were things like:

> A

> i would prefer ~/code/localLLM

> A, also note i've "llm" cli already installed, and alias would be nice.

> let's go with recommendation, write the plan.

That is the entire texture of it. A simple opening prompt that points at an existing guide and names my constraints, then a handful of one-word answers steering the branches. The model did the reading — the article and the full HN thread — and the arithmetic. I made the calls.

And it pushed back, which is the point. When I leaned toward the 65 K context window from the article, it did the memory math and showed me I would be swapping inside the first generation on 32 GB, so we settled on 32 K. When I waffled on keeping Ollama "just in case," it pointed out I was at 89 % disk with a thirteen-gigabyte Ollama models directory I was not using. When I asked for an alias, it caught that `llm` was already taken by [Simon Willison's tool](https://llm.datasette.io) and proposed `lcl` instead. None of these are insights I lacked. They are checks I would have skipped because I was already mentally on the next step.

By the end there was a written record of every decision and its reason, in the repo, not in my head. That is where it should be.

## The Decisions That Fell Out

The interview converged on a short list, and the reasoning behind each one is worth more than the choice itself.

**Model: Gemma 4 26B-A4B, the MoE, not a dense model.** The single most important fact about local inference on a Mac is not how much RAM you have, it is how fast it can be read. Generation is bottlenecked on memory bandwidth. The M1 Max in Kyle's article runs at 400 GB/s; my M1 Pro at roughly 200. Everything else equal, I should expect about half his throughput — his 72 tokens per second becomes my 36. That is still faster than I read. It is also why a mixture-of-experts model is the right answer here: Gemma 4 26B-A4B holds 26 billion parameters but activates only four billion per token. The full weights sit in RAM, but each forward pass streams a fraction of them. The dense 27B sibling has the same disk footprint and meaningfully worse generation rate. It is probably smarter. It does not matter, because it is too slow for the slot I am filling.

**Speculative decoding, on.** Gemma 4 ships an MTP draft head — a tiny network that predicts the next several tokens cheaply, which the main model accepts or rejects in one pass. When acceptance is high, you get most of those tokens almost for free. Kyle measured +24 % on his machine. The HN thread is full of caveats about acceptance rates and MoE models benefiting less. None of it changes the decision: turn it on, measure, keep what you get.

**Context: 32 K, not 65 K.** The arithmetic the model made me do. A 65 K KV cache plus 16 GB of weights plus a draft model does not leave enough headroom on 32 GB once Chrome and an IDE are open.

**mise, not a shell script.** The article uses `huggingface-cli` to fetch the GGUFs and a hand-written tmux script to launch the server. Both work. Both are also infrastructure you now own and will forget you configured. llama.cpp's `-hf` flag does the download without a Python virtualenv. mise's `github:` backend installs the prebuilt Metal binary and rolls it forward with `mise upgrade`. The tmux script becomes a few named tasks in a `.mise.toml`. The choice is not about elegance, it is about which moving piece you are willing to own. I already own mise.

**Ollama goes.** I had it from earlier experiments, with `gemma4:latest` and a couple of other models taking 13 GB, plus the app idling in the background on port 11434. Ollama is a wrapper around llama.cpp. Once you run `llama-server` directly, the wrapper is in the way. So the app, the models directory, and the port all go, and the 13 GB comes back on a disk that was at 89 %.

## The Setup, Start To Finish

This is the reproducible part. You can follow it by hand, or point an LLM at this section and let it do the work — that is roughly how it got built in the first place. Numbers below are the actual results on my M1 Pro, not estimates.

**1. Decommission Ollama** (skip if you never had it):

```sh
osascript -e 'tell application "Ollama" to quit' 2>/dev/null
pkill -f Ollama
rm -rf ~/.ollama /Applications/Ollama.app   # reclaimed 13 GB
```

**2. Install llama.cpp via mise.** The prebuilt arm64 binary has Metal and Accelerate baked in:

```sh
mise use --global 'github:ggml-org/llama.cpp@latest'
llama-server --help | grep -E -- '--spec-type|-hf'   # confirm MTP + HF download support
```

The one thing worth verifying is that `--spec-type draft-mtp` is present — MTP support landed only recently. On my install (build `b9631`) it was there. If it ever is not, a source build with `-DGGML_METAL=ON` is the five-minute fallback.

**3. A project with mise tasks** at `~/code/localLLM/.mise.toml`. The `[env]` block makes the model cache live with the project; the tasks replace the shell script:

```toml
[env]
LLAMA_CACHE = "{{ config_root }}/models"

[tools]
"github:ggml-org/llama.cpp" = "latest"

[tasks.start]
description = "Start llama-server (Gemma 4 26B-A4B + MTP) in tmux"
run = """
tmux has-session -t llama 2>/dev/null && { echo running; exit 0; }
tmux new-session -d -s llama -c "$PWD" \\
  "llama-server \\
    -hf  unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q4_K_XL \\
    -hfd unsloth/gemma-4-26B-A4B-it-GGUF:Q8_0-MTP \\
    --spec-type draft-mtp --spec-draft-n-max 3 \\
    -ngl 999 -fa on -c 32768 --parallel 1 \\
    --host 127.0.0.1 --port 8082 \\
    2>&1 | tee -a logs/llama-server.log"
"""

[tasks.stop]
run = "tmux kill-session -t llama 2>/dev/null && echo stopped || echo 'not running'"

[tasks.status]
run = "curl -fsS http://127.0.0.1:8082/v1/models >/dev/null && echo up || echo down"
```

A note on the port. The article uses 8080. On my machine 8080 and 8081 were already taken by Google `cloud-run` processes, so the server silently answered on a port that was not mine until I noticed the responses carried a `Server: Google Frontend` header. I moved everything to **8082**. Check `lsof -i :8080` before you assume a port is free.

**4. A one-key alias** in `~/.zshrc`. `llm` was taken, so `lcl` for "local":

```sh
lcl() { mise -C "$HOME/code/localLLM" run "$@"; }
```

```sh
lcl start    # boot the server (first run downloads the model)
lcl status   # is it up?
lcl stop     # free the ~22 GB of RAM
```

**5. First boot and download.** `lcl start` triggers the download through llama.cpp's `-hf`. The real footprint was smaller than the article's "~21 GB" estimate: **18 GB** total — 16 GB for the Q4_K_XL main model, **1.2 GB** for the MTP head (it is an auxiliary head, not a full second model), and a 441 MB multimodal projector that gets pulled automatically even though I do not need images. Add `--no-mmproj` if you want to skip it.

**6. Point pi at it.** A `local` provider in `~/.pi/agent/models.json`:

```json
{
  "providers": {
    "local": {
      "name": "Local llama.cpp",
      "baseUrl": "http://127.0.0.1:8082/v1",
      "api": "openai-completions",
      "apiKey": "local",
      "models": [{
        "id": "gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf",
        "name": "Gemma 4 26B-A4B Q4 + MTP",
        "reasoning": true,
        "input": ["text"],
        "contextWindow": 32768,
        "maxTokens": 8192,
        "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
      }]
    }
  }
}
```

And a `local` mode in `modes.json` pointing at it. Set `"reasoning": true` — Gemma 4 IT thinks by default and returns its working in `reasoning_content`, leaving `content` empty if you cap `max_tokens` before it finishes thinking. That one surprised me during the first benchmark: a tiny token budget produced an empty answer because the model spent all of it reasoning.

**What it actually does**, measured on the M1 Pro:

| Metric | Result |
| --- | --- |
| Generation | **34–36 tok/s** (predicted half of Kyle's 72, got it) |
| Prompt ingestion | 77 tok/s |
| Time to first token | ~376 ms |
| MTP acceptance | **~65 %** (e.g. 1350 of 2090 drafted tokens accepted) |
| Disk after setup | 35 GB free (93 % used) |

Half the bandwidth, half the tokens, exactly as predicted. The MTP acceptance was better than I feared — the article saw +24 % on a dense workload; two thirds of my drafted tokens landed.

## How I Actually Use A Fast Model

A `fast` model in pi is not the thing I have a conversation with. It is the model that does the small, high-volume, latency-sensitive jobs around the edges of the real work, where Opus is overkill and the round-trip cost is what matters. Those are exactly the jobs I want to stop paying for, and exactly where 36 tokens per second is plenty.

Concretely, in my setup:

- **`/answer` and `Ctrl+.`** — a [small pi extension I run](https://github.com/theskumar/agent-stuff/blob/main/extensions/answer.ts) that grabs the last assistant message when it ends on a batch of clarifying questions, extracts them into structured JSON via a side LLM call, and opens a TUI so I can answer them one at a time. The extraction is a contained, schema-shaped task — perfect for a fast model. It defaults to `claude-bridge/claude-haiku-4-5` and is configurable at `~/.pi/agent/extensions/answer.config.json`, which is exactly the line I now point at `local`.
- **Branch summaries on `/tree`.** When I navigate away from a branch of a conversation, pi offers to summarize the work I am leaving and inject it into the new branch. That summary is a fast-model job.
- **Compaction.** When a session outgrows its context window, pi summarizes the old turns to free room. Same shape of work, same model slot.
- **`/mode fast`** for the genuinely small questions — "what's the flag for X", "rename this", a quick grep-and-explain — where I switch the whole session to the fast slot and switch back.

None of these need a frontier model. They need something that responds now and gets the structure right. That is the bar Gemma 4 has to clear to take the slot from Haiku.

## What I Am Not Doing Yet

I am not putting the server behind launchd. At ~22 GB resident on a 32 GB machine, leaving it running alongside Chrome and an IDE is asking for swap. On-demand `lcl start` / `lcl stop` is honest about the cost in a way always-on is not.

I am not repointing the `fast` mode at the local model. The mode that says Haiku-4-5 keeps saying Haiku-4-5. I added `local` alongside it and I am using that for a week. Local models can be brilliant in a chat window and brittle inside an agent loop, and I have not yet watched Gemma 4 drive a real tool loop. If it holds up — on tool calling, on diff quality, on the ten-line edits that fill my day — I will promote it and rename the old one to `fast-cloud`. If it does not, nothing is touched and the rollback is a `git checkout`.

I am not running a second model on a second port. Maybe Qwen 3.6 35B-A3B earns a slot for the cases where Gemma is too weak. Maybe one model is enough. I will know in a week.

## The Smaller Lesson

The bigger story is bandwidth and quantisation and what fits in 32 GB. The smaller one, which I think is more useful, is about the planning. I have spent two years watching people — including me — let agents do work the agent should not be doing, because asking felt cheaper than thinking. Handing a guide to a model and making it interrogate my plan is the opposite move. The model is not making the decisions. It read the article and the comments, did the arithmetic, and asked the awkward questions; I answered "A" and "i would prefer ~/code/localLLM" and kept the wheel. The agency stayed with me. The legwork moved to the model. That trade I am happy with.

The local agent might work or it might not — I will know in a week. The interview transcript is already useful, because it forced me to write down why I made each choice, in a form I can read later when I have forgotten. That part I am keeping regardless of how the Gemma 4 part turns out.
