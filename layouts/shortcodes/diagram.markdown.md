{{- /* The diagram shortcode in a page's Markdown copy (index.md): the alt
       text stands in for the drawing, then the caption. */ -}}
**Figure:** {{ .Get "alt" }}{{ with .Inner | strings.TrimSpace }} {{ . }}{{ end }}
