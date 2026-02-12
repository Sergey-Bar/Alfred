param([string]$OutDir = "dist")

if (Test-Path $OutDir) { Remove-Item -Recurse -Force $OutDir }
New-Item -ItemType Directory -Path $OutDir | Out-Null

Write-Host "Creating minimal bundle in $OutDir"

# Copy folders
Copy-Item -Recurse -Force -Path app -Destination (Join-Path $OutDir 'app')
Copy-Item -Recurse -Force -Path alembic -Destination (Join-Path $OutDir 'alembic')
Copy-Item -Recurse -Force -Path config -Destination (Join-Path $OutDir 'config')
Copy-Item -Recurse -Force -Path static -Destination (Join-Path $OutDir 'static')

# Copy docker files
Copy-Item -Force docker\Dockerfile $OutDir -ErrorAction SilentlyContinue
Copy-Item -Force docker\docker-compose.yml $OutDir -ErrorAction SilentlyContinue

# Copy requirements
Copy-Item -Force requirements\requirements.txt $OutDir -ErrorAction SilentlyContinue
Copy-Item -Force requirements\requirements-dev.txt $OutDir -ErrorAction SilentlyContinue

# Copy Helm chart
if (Test-Path charts\alfred) { Copy-Item -Recurse -Force charts\alfred (Join-Path $OutDir 'charts\alfred') }

Write-Host "Minimal bundle created: $OutDir"
