{{/* Generate common names for chart */}}
{{- define "alfred.name" -}}{{- "alfred" -}}{{- end -}}
{{- define "alfred.chart" -}}{{- .Chart.Name }}-{{ .Chart.Version }}{{- end -}}
{{- define "alfred.fullname" -}}{{- printf "%s-%s" (include "alfred.name" .) .Release.Name -}}{{- end -}}
