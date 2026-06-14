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

My zsh prompt was taking close to a second to appear on a fresh terminal. Not catastrophic. But you feel it every time tmux spawns a new pane, and for me that is constantly. The config had grown for years, one `eval` and one plugin at a time, and nobody had been auditing it, least of all me.

What follows is the audit, and the eight things I changed. The numbers are estimates, not measurements, and I will say so again at the end.

## Measure first

Before I touched anything, I measured. Two tools did the work:

```zsh
# Cold-start benchmark (run a few times, watch the variance):
for i in {1..5}; do time zsh -i -c exit; done

# In-shell flamegraph:
#   1. Uncomment `zmodload zsh/zprof` at the top of .zshrc
#   2. Add `zprof` at the bottom
#   3. Open a new shell
zprof | head -40
```

`zprof` is the one that helped most. It prints which function calls and `eval`s are burning time, sorted by self-time and call count. That is enough to stop guessing.

## 1. Stop forking `brew --prefix` five times per shell

My macOS config had this:

```zsh
export PATH=$(brew --prefix coreutils)/libexec/gnubin:$PATH
export PATH=$(brew --prefix findutils)/libexec/gnubin:$PATH
export PATH=$(brew --prefix gnu-sed)/libexec/gnubin:$PATH
export PATH=$(brew --prefix grep)/libexec/gnubin:$PATH
export PATH=$(brew --prefix curl)/bin:$PATH
```

Five forks of `brew`, which is a Ruby program, on every shell, just to resolve paths that always end up under `${HOMEBREW_PREFIX}/opt/<formula>` anyway. Each fork is about 35 ms on Apple Silicon, so that is roughly 180 ms gone before I have typed a single character.

Fix:

```zsh
_brew_opt="${HOMEBREW_PREFIX:-/opt/homebrew}/opt"
[ -d "$_brew_opt" ] || _brew_opt="/usr/local/opt"
export PATH="$_brew_opt/coreutils/libexec/gnubin:$_brew_opt/findutils/libexec/gnubin:$_brew_opt/gnu-sed/libexec/gnubin:$_brew_opt/grep/libexec/gnubin:$_brew_opt/curl/bin:$PATH"
unset _brew_opt
```

A path-prefix lookup costs nothing. The `/usr/local/opt` fallback is there for Intel macOS, where `HOMEBREW_PREFIX` may be unset, for example in bash without `brew shellenv`.

Saves about 180 ms.

## 2. Defer plugins with zinit's `wait` ice

If you use a plugin manager, this is probably the biggest single win on the table. Syntax highlighting, autosuggestions, history-substring-search, completion add-ons: none of these need to load before the first prompt renders. They only need to be there by the time you type something.

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

The `atinit` ice on the first plugin runs `compinit` once and replays cached completions via `zicdreplay`. One `compinit` covers every turbo-loaded plugin. The `atload"_zsh_autosuggest_start"` line re-initializes autosuggestions after deferred loading. Without it the plugin silently no-ops, which took me an embarrassing amount of time to work out.

Saves 100-300 ms.

## 3. Compile `.zcompdump` to bytecode

`compinit` parses thousands of completion functions on every startup. Compiling its dump file to bytecode means subsequent shells skip the parser:

```zsh
zcompdump="${ZDOTDIR:-$HOME}/.zcompdump"
[[ -s "$zcompdump" && (! -s "${zcompdump}.zwc" || "$zcompdump" -nt "${zcompdump}.zwc") ]] \
    && zcompile "$zcompdump"
```

It recompiles only when the source is newer than the cached `.zwc`. Saves 30-80 ms.

## 4. Pick one version manager

I had both `fnm` and `mise` active, which is one more than anyone needs. Mise manages everything I actually use, Node, Python, Go; `fnm env` in `.zshrc` was a leftover that nothing depended on. Deleting it saved another 30-80 ms per shell.

Mise itself has a second optimization, `--shims` mode:

```zsh
eval "$(~/.local/bin/mise activate zsh --shims)"
```

Default `mise activate` installs a `precmd` hook that runs on every prompt to keep tool versions in sync with `.mise.toml`. Shim mode replaces that hook with symlinks on `PATH` that resolve the right version the first time you call each tool. That is about 17 ms saved at startup, paid back as 10-30 ms on the first invocation per shell. For interactive use it is a fine trade.

## 5. Cache the slow `eval`s

A lot of tools want you to run `eval "$(tool init zsh)"` at startup. Each one forks the tool, runs its setup, and pipes the result back. You pay that cost every shell, even though the output rarely changes between runs.

A small helper fixes it:

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

Keep `starship init zsh` eager. You need it for the prompt anyway, and it is already fast.

Saves 50-100 ms.

## 6. Audit plugins; cut what you don't use

I was loading the [Oh My Zsh git plugin](https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git) via zinit's snippet feature. The plugin ships roughly 150 aliases.

So I grepped my last few months of shell history against its alias list. Five OMZ-only aliases came back: `gsw`, `glo`, `gf`, `gclean`, `gss`. Everything else I either did not use or had already redefined to my own taste. I copied those five into `shell/.aliases` and dropped the `OMZP::git` snippet from zinit.

There is a second reason to do this, and it has nothing to do with startup time. Because the OMZ plugin loaded in turbo mode, after my eager `shell/.aliases`, it was quietly overwriting aliases I had defined myself. My `gc='git commit -m'` was getting clobbered to `git commit --verbose`, and `gg='lazygit'` to `git gui`. The plugin "worked" because turbo-loaded aliases land before you type, but the behavior was not the one I had configured. Dropping the plugin put my own aliases back in charge.

While I was at it I found `zsh/.zsh/plugins/git/git.plugin.zsh` in my dotfiles, 150 lines of git aliases, sourced from nowhere. Years of dead code I had been carrying around. Gone.

## 7. Move PATH and env to `.zshenv`

`.zshrc` runs only for interactive shells. If you set `PATH` there, then cron jobs, `zsh -c "command"` invocations, and IDE-spawned non-interactive shells do not see your tools. That is how you end up burning half a day on "works in my terminal, breaks in CI."

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

This is not a cold-start win, since `.zshenv` still runs. It is a correctness fix. A shorter `PATH` does make command lookups faster, so you get a little of both.

## 8. Fix the things you didn't know were broken

While I was in there, `zprof` and a slow re-read of the config surfaced a stack of small bugs that had nothing to do with cold start. They were just wrong:

- `~/.profile` was being sourced twice, once from `.zshrc` and once from `.zshenv`. 20-80 ms of pure waste.
- `compinit`'s cache-staleness check had inverted-looking logic and a misleading comment. It happened to do the right thing, but only by accident.
- `zsh/.zsh/lib/completions.zsh` referenced `$ZSH`, an Oh My Zsh leftover that was unset in my setup. The completion cache-path was silently expanding to `/cache/`, the filesystem root. Nothing got written there because the directory was not writable, so completions had no cache at all. Caching had quietly been off the whole time.
- `compdef` calls from eager tool initializations were arriving _before_ turbo-mode `compinit` had run, so completions for those tools were not registering. I fixed it with a small shim that queues the calls until `compinit` is ready:

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

None of those moved the startup number. They were still bugs, and now they are not.

## Doing this on your own config

Measure before you touch anything. `time zsh -i -c exit` for cold start, `zprof` for the in-shell breakdown. Skip that step and you will spend an afternoon optimizing the wrong thing. I have done exactly that.

Then grep your shell history against the alias and function lists of whatever plugins you load. You will usually find you are loading hundreds of definitions to use a handful.

Defer what can be deferred. First-prompt latency is what you feel, and almost nothing actually has to load before you can type. Cache expensive `eval`s whose output only changes when the binary changes, and key the cache on the binary's mtime so upgrades invalidate it for you. Hardcode the constants: `brew --prefix coreutils` is always `${HOMEBREW_PREFIX}/opt/coreutils`. Forking a Ruby program to ask is silly.

And keep environment variables in `.zshenv`, not `.zshrc`. Future-you, debugging why something works in iTerm but not in a cron job, will be grateful.

## Estimated total

| Change | Savings |
| --- | --- |
| Stop forking `brew --prefix` × 5 | ~180 ms |
| Defer plugins with `zinit wait` | 100-300 ms |
| Cache remaining `eval`s | 50-100 ms |
| Compile `.zcompdump` | 30-80 ms |
| Drop `fnm` (mise covers it) | 30-80 ms |
| **Total** | **~400-700 ms** |

These are estimates, not measurements. Your actual numbers depend on your hardware, your plugin set, and how much cruft you had accumulated over the years. Under 200 ms on Apple Silicon is doable with stock zsh and a small, well-deferred plugin set.

My dotfiles, with all of this applied, are at [github.com/theskumar/dotfiles](https://github.com/theskumar/dotfiles). The `zsh/OPTIMIZATION.md` file there is the running log of what is done and what is still open.

None of this stays fixed. A shell config grows the way mine did, one `eval` and one plugin at a time, each addition reasonable on its own, until a fresh terminal takes a second and nobody remembers why. The fix was never a cleverer `.zshrc`. It is going back through the thing every so often and asking, line by line, what still earns its place.
