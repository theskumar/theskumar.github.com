+++
title = "How I Optimized My Zsh Startup Time"
date = "2026-05-11"
description = "An audit of my zsh config turned up shell forks, redundant plugins, and eager evals. Here are the eight fixes that shaved an estimated 400-700 ms off cold start."
tags = [
    "zsh",
    "shell",
    "performance",
    "dotfiles",
    "macos"
]
+++

My zsh prompt was taking close to a second on a fresh terminal. Not catastrophic, but you feel it every time tmux spawns a new pane, which for me is constantly. The config had been growing for years and nobody had been auditing it.

What follows is the audit, and the eight things I changed.

## Measure first

```zsh
# Cold-start benchmark (run a few times, watch the variance):
for i in {1..5}; do time zsh -i -c exit; done

# In-shell flamegraph:
#   1. Uncomment `zmodload zsh/zprof` at the top of .zshrc
#   2. Add `zprof` at the bottom
#   3. Open a new shell
zprof | head -40
```

`zprof` is the one that helped most. It prints which function calls and `eval`s are burning time, sorted by self-time and call count.

## 1. Stop forking `brew --prefix` five times per shell

My macOS config had this:

```zsh
export PATH=$(brew --prefix coreutils)/libexec/gnubin:$PATH
export PATH=$(brew --prefix findutils)/libexec/gnubin:$PATH
export PATH=$(brew --prefix gnu-sed)/libexec/gnubin:$PATH
export PATH=$(brew --prefix grep)/libexec/gnubin:$PATH
export PATH=$(brew --prefix curl)/bin:$PATH
```

Five forks of `brew` (a Ruby program) on every shell, just to resolve paths that always end up under `${HOMEBREW_PREFIX}/opt/<formula>` anyway. Each fork is about 35 ms on Apple Silicon, so that's roughly 180 ms gone before I've typed anything.

Fix:

```zsh
_brew_opt="${HOMEBREW_PREFIX:-/opt/homebrew}/opt"
[ -d "$_brew_opt" ] || _brew_opt="/usr/local/opt"
export PATH="$_brew_opt/coreutils/libexec/gnubin:$_brew_opt/findutils/libexec/gnubin:$_brew_opt/gnu-sed/libexec/gnubin:$_brew_opt/grep/libexec/gnubin:$_brew_opt/curl/bin:$PATH"
unset _brew_opt
```

Path-prefix lookup costs nothing. The `/usr/local/opt` fallback is there for Intel macOS where `HOMEBREW_PREFIX` may be unset (e.g. bash without `brew shellenv`).

Saves about 180 ms.

## 2. Defer plugins with zinit's `wait` ice

If you use a plugin manager, this is probably the biggest single win available. Syntax highlighting, autosuggestions, history-substring-search, completion add-ons. None of these need to load before the first prompt renders; they only need to be there by the time you type something.

With [zinit](https://github.com/zdharma-continuum/zinit)'s `wait` ice, you defer them until after the first prompt:

```zsh
zinit wait lucid light-mode for \
    atinit"ZINIT[COMPINIT_OPTS]=-C; zicompinit; zicdreplay" \
        zdharma-continuum/fast-syntax-highlighting \
    atload"_zsh_autosuggest_start" \
        zsh-users/zsh-autosuggestions \
    blockf atpull'zinit creinstall -q .' \
        zsh-users/zsh-completions \
    atload"bindkey '^[[A' history-substring-search-up; bindkey '^[[B' history-substring-search-down" \
        zsh-users/zsh-history-substring-search \
    wfxr/forgit
```

The `atinit` ice on the first plugin runs `compinit` once and replays cached completions via `zicdreplay`. One `compinit` covers every turbo-loaded plugin. The `atload"_zsh_autosuggest_start"` line re-initializes autosuggestions after deferred loading. Without it the plugin silently no-ops, which took me an embarrassing amount of time to figure out.

Saves 100-300 ms.

## 3. Compile `.zcompdump` to bytecode

`compinit` parses thousands of completion functions on every startup. Compiling its dump file means subsequent shells skip the parser:

```zsh
zcompdump="${ZDOTDIR:-$HOME}/.zcompdump"
[[ -s "$zcompdump" && (! -s "${zcompdump}.zwc" || "$zcompdump" -nt "${zcompdump}.zwc") ]] \
    && zcompile "$zcompdump"
```

Recompiles only when the source is newer than the cached `.zwc`. 30-80 ms saved.

## 4. Pick one version manager

I had both `fnm` and `mise` active. Mise manages everything I actually use (Node, Python, Go); `fnm env` in `.zshrc` was a leftover nothing depended on. Deleting it saved another 30-80 ms per shell.

Mise itself has a second optimization, `--shims` mode:

```zsh
eval "$(~/.local/bin/mise activate zsh --shims)"
```

Default `mise activate` installs a `precmd` hook that runs on every prompt to keep tool versions in sync with `.mise.toml`. Shim mode replaces that hook with symlinks on `PATH` that resolve the right version the first time you call each tool. About 17 ms saved at shell startup, paid back as 10-30 ms on the first invocation per shell. Fine trade for interactive use.

## 5. Cache the slow `eval`s

A lot of tools want you to do `eval "$(tool init zsh)"` at startup. Each one forks the tool, runs its setup, pipes the result back. That cost is paid every shell, even though the output rarely changes between runs.

A small helper:

```zsh
_cache_eval() {
  local name=$1; shift
  local cache=~/.zsh/cache/$name.zsh
  [[ -s $cache && $cache -nt ${commands[$1]:-/dev/null} ]] \
    || { mkdir -p ~/.zsh/cache; "$@" > $cache; }
  source $cache
}
_cache_eval zoxide zoxide init zsh --cmd j
_cache_eval uv     uv generate-shell-completion zsh
```

The `$cache -nt ${commands[$1]:-/dev/null}` test compares mtimes. When brew or mise upgrades the binary, the cache invalidates on its own. No stale-cache surprises after a `brew upgrade`.

Keep `starship init zsh` eager; you need it for the prompt anyway, and it's already fast.

Saves 50-100 ms.

## 6. Audit plugins; cut what you don't use

I was loading the [Oh My Zsh git plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git) via zinit's snippet feature. The plugin ships roughly 150 aliases.

I grepped my last few months of shell history against its alias list. Five OMZ-only aliases came back: `gsw`, `glo`, `gf`, `gclean`, `gss`. Everything else I either didn't use or had already redefined to my own taste. So I copied those five into `shell/.aliases` and dropped the `OMZP::git` snippet from zinit.

There's a second reason to do this beyond startup time. Because the OMZ plugin loaded in turbo mode (after my eager `shell/.aliases`), it was quietly overwriting aliases I'd defined myself. My `gc='git commit -m'` was getting clobbered to `git commit --verbose`, and `gg='lazygit'` to `git gui`. The plugin "worked" because turbo-loaded aliases land before you type, but the behavior wasn't what I'd configured. Dropping the plugin put my own aliases back in charge.

While I was at it I noticed `zsh/.zsh/plugins/git/git.plugin.zsh` in my dotfiles, 150 lines of git aliases, wasn't sourced from anywhere. Years of dead code I'd been carrying around. Gone.

## 7. Move PATH and env to `.zshenv`

`.zshrc` runs only for interactive shells. If you set `PATH` there, then cron jobs, `zsh -c "command"` invocations, and IDE-spawned non-interactive shells don't see your tools. That's how you end up burning half a day on "works in my terminal, breaks in CI."

The right home is `.zshenv`, which runs for every zsh invocation:

```zsh
# ~/.zshenv
export PNPM_HOME="$HOME/Library/pnpm"

typeset -U path PATH    # auto-dedupe
path=(
  "$HOME/.local/bin"
  "$PNPM_HOME"
  $path
)

[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
```

`typeset -U path PATH` ties the `path` array to the `PATH` scalar and deduplicates automatically. No more 8 KB `PATH` strings with the same entry six times because nested shells kept prepending.

This isn't a cold-start win (`.zshenv` still runs), but it's a correctness fix. A shorter `PATH` does mean faster command lookups too.

## 8. Fix the things you didn't know were broken

While I was in there, `zprof` and a slow re-read of the config surfaced a stack of small bugs that had nothing to do with cold start, but were just wrong:

- `~/.profile` was being sourced twice, once from `.zshrc` and once from `.zshenv`. 20-80 ms of pure waste.
- `compinit`'s cache-staleness check had inverted-looking logic and a misleading comment. It happened to do the right thing, but only by accident.
- `zsh/.zsh/lib/completions.zsh` referenced `$ZSH`, an Oh My Zsh leftover that was unset in my setup. The completion cache-path was silently expanding to `/cache/`, i.e. the filesystem root. Nothing got written there because the directory wasn't writable, so completions had no cache at all. Caching had quietly been off the entire time.
- `compdef` calls from eager tool initializations were arriving _before_ turbo-mode `compinit` had run, so completions for those tools weren't registering. Fixed with a small shim that queues calls until `compinit` is ready:

```zsh
if ! (( ${+functions[compdef]} )); then
  typeset -ga __deferred_compdefs
  compdef() { __deferred_compdefs+=("${(j: :)@}") }
fi
```

Then in the turbo block's `atinit`, after `zicompinit; zicdreplay`:

```zsh
(( ${#__deferred_compdefs} )) && \
  for c in "${__deferred_compdefs[@]}"; do eval "compdef $c"; done
unset __deferred_compdefs
```

None of those moved the startup number. They were still bugs, and now they aren't.

## Doing this on your own config

Measure before you touch anything. `time zsh -i -c exit` for cold start, `zprof` for the in-shell breakdown. Otherwise you'll spend an afternoon optimizing the wrong thing; I've done that.

Then grep your shell history against the alias and function lists of whatever plugins you load. You'll usually find you're loading hundreds of definitions to use a handful.

Defer what can be deferred. First-prompt latency is what you feel, and almost nothing actually has to load before you can type. Cache expensive `eval`s whose output only changes when the binary changes, and key the cache on the binary's mtime so upgrades invalidate it for you. Hardcode constants: `brew --prefix coreutils` is always `${HOMEBREW_PREFIX}/opt/coreutils`. Forking a Ruby program to ask is silly.

And keep environment variables in `.zshenv`, not `.zshrc`. Future-you, debugging why something works in iTerm but not in a cron job, will appreciate it.

## Estimated total

| Change | Savings |
| --- | --- |
| Stop forking `brew --prefix` × 5 | ~180 ms |
| Defer plugins with `zinit wait` | 100-300 ms |
| Cache remaining `eval`s | 50-100 ms |
| Compile `.zcompdump` | 30-80 ms |
| Drop `fnm` (mise covers it) | 30-80 ms |
| **Total** | **~400-700 ms** |

Estimates, not measurements. Your actual numbers depend on your hardware, plugin set, and how much cruft you'd accumulated over the years. Under 200 ms on Apple Silicon is doable with stock zsh and a small, well-deferred plugin set.

My dotfiles, with all of this applied, are at [github.com/theskumar/dotfiles](https://github.com/theskumar/dotfiles). The `zsh/OPTIMIZATION.md` file there is the running log of what's done and what's still open.
