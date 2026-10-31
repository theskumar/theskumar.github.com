{{- /* The project list for /projects/index.md (single.markdown.md). Same data
       and order as layouts/_default/projects.html. */ -}}
{{- range site.Data.projects.themes }}{{ $theme := .id }}

## {{ .title }}

{{ .blurb }}
{{ range where site.Data.projects.projects "theme" $theme }}
- **{{ if .url }}[{{ .name }}]({{ .url }}){{ else }}{{ .name }}{{ end }}**{{ if .unreleased }} (unreleased){{ end }} ({{ .years }}): {{ .one }}{{ with .short }} {{ . }}{{ end }} Role: {{ .role }}.{{ with .outcome }} {{ . }}.{{ end }}
{{- end }}
{{- with .also }}

Also: {{ . }}
{{- end }}
{{- end }}
