# Git Security — Pre-commit Hooks y Patrones

## Pre-commit Hook: Secret Detection

### Instalar
```bash
# Opción 1: gitleaks (recomendado)
brew install gitleaks  # Mac
scoop install gitleaks  # Windows

# Opción 2: trufflehog
pip install trufflehog
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: no-commit-to-branch
        args: ['--branch', 'main']
```

### git hooks/pre-commit (manual)
```bash
#!/bin/bash
# Secret detection before commit

echo "🔍 Running secret detection..."

# Check for common secrets
if git diff --cached --name-only | xargs grep -l -E "(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][a-zA-Z0-9]{20,}" 2>/dev/null; then
    echo "❌ Potential secret detected! Review staged changes."
    exit 1
fi

# Check for private keys
if git diff --cached --name-only | xargs grep -l "BEGIN.*PRIVATE KEY" 2>/dev/null; then
    echo "❌ Private key detected in staged files!"
    exit 1
fi

echo "✅ No secrets found"
```

## .gitignore Patterns Seguros

```gitignore
# Environment variables
.env
.env.local
.env.*.local
.env.production

# Secrets
*.pem
*.key
*.cert
*.p12
*.pfx
credentials.json
service-account*.json

# IDE
.vscode/settings.json
.idea/workspace.xml
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Dependencies
node_modules/
vendor/
.venv/
venv/

# Build
dist/
build/
*.min.js
*.min.css

# Logs
*.log
npm-debug.log*

# Cache
.cache/
.parcel-cache/
.nuxt/
.next/

# Testing
coverage/
.pytest_cache/
htmlcov/
```

## Branch Protection Rules

### GitHub Settings
```yaml
Branch: main
Protection rules:
  - Require pull request reviews (1 approval)
  - Require status checks to pass
  - Require branches to be up to date
  - Require signed commits
  - Restrict force pushes
  - Restrict deletions
```

## Signed Commits

### Setup
```bash
# Generar key GPG
gpg --full-generate-key

# Listar keys
gpg --list-secret-keys --keyid-format=long

# Configurar git
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# En GitHub: agregar GPG key
# Settings > SSH and GPG keys > New GPG key
```

### Verificar
```bash
git log --show-signature
git verify-commit HEAD
```
