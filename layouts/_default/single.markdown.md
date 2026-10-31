{{- /* The Markdown copy of a page, at <page URL>index.md (output format
       "markdown" in hugo.toml). It is the page's source with shortcodes
       rendered and site-relative links made absolute, under a short
       header. The "Copy" button (partials/page-markdown.html) and
       /llms.txt point here. */ -}}
{{- $base := strings.TrimSuffix "/" site.BaseURL -}}
{{- $meta := slice "By Saurabh Kumar" -}}
{{- if eq .Section "blog" }}{{ $meta = $meta | append (.Date.Format "Jan 2, 2006") }}
{{- else if eq .Section "til" }}{{ $meta = $meta | append (printf "TIL note, %s" (.Date.Format "Jan 2, 2006")) }}
{{- else }}{{ with .Params.eyebrow }}{{ $meta = $meta | append . }}{{ end }}{{ end -}}
{{- with .GetTerms "tags" }}{{ $t := slice }}{{ range . }}{{ $t = $t | append .Data.Term }}{{ end }}{{ $meta = $meta | append (printf "Tags: %s" (delimit $t ", ")) }}{{ end -}}
{{- $sub := .Description | default .Params.lede | default (cond (ne .Params.tagline .Title) .Params.tagline "") -}}
{{- $body := .RenderShortcodes | string -}}
{{- if eq .Layout "projects" }}{{ $body = printf "%s%s" (strings.TrimRight "\n" $body) (partial "projects-markdown.md" .) }}{{ end -}}
{{- $body = replaceRE `\]\(/` (printf "](%s/" $base) $body -}}
{{- $body = replaceRE `(?m)^(\[[^\]]+\]:\s*)/` (printf "${1}%s/" $base) $body -}}
# {{ .Title }}

{{ delimit $meta " · " }}

Source: {{ .Permalink }}
{{- with $sub }}

> {{ . }}
{{- end }}

{{ trim $body "\n" }}
