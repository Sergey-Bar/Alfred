{{/*
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Helm template helpers for Alfred chart.
Root Cause:  Sprint task T189 — Helm chart.
Context:     Standard Helm helper functions.
Suitability: L2 — Standard Helm patterns.
──────────────────────────────────────────────────────────────
*/}}

{{/*
Expand the name of the chart.
*/}}
{{- define "alfred.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "alfred.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "alfred.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "alfred.labels" -}}
helm.sh/chart: {{ include "alfred.chart" . }}
{{ include "alfred.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "alfred.selectorLabels" -}}
app.kubernetes.io/name: {{ include "alfred.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "alfred.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "alfred.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "alfred.backend.labels" -}}
{{ include "alfred.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "alfred.backend.selectorLabels" -}}
{{ include "alfred.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Gateway labels
*/}}
{{- define "alfred.gateway.labels" -}}
{{ include "alfred.labels" . }}
app.kubernetes.io/component: gateway
{{- end }}

{{/*
Gateway selector labels
*/}}
{{- define "alfred.gateway.selectorLabels" -}}
{{ include "alfred.selectorLabels" . }}
app.kubernetes.io/component: gateway
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "alfred.frontend.labels" -}}
{{ include "alfred.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "alfred.frontend.selectorLabels" -}}
{{ include "alfred.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "alfred.postgresql.host" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "alfred.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "alfred.redis.host" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "alfred.fullname" .) }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}
