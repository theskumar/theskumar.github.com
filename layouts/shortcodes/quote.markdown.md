{{- /* The quote shortcode in a page's Markdown copy (index.md): a plain
       blockquote with the attribution as its last line. */ -}}
{{- $lines := split (.Inner | strings.TrimSpace) "\n" -}}
{{- range $lines }}
{{ trim (printf "> %s" .) " " }}
{{- end }}
>
> — {{ with .Get "url" }}[{{ $.Get "author" }}]({{ . }}){{ else }}{{ .Get "author" }}{{ end }}{{ with .Get "context" }}, {{ . }}{{ end }}
