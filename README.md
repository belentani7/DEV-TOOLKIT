# DEV TOOLKIT — Herramientas, Scripts y Patterns Open Source
## Curado de GitHub, docs oficiales y mejores prácticas 2026

> Colección de soluciones reales, scripts funcionales y configuraciones listas para usar.
> Todo open-source. Sin productos propios. Sin CLIs de empresas externas.

---

## Contenido

| Sección | Qué hay |
|---------|---------|
| [scripts/](#scripts) | PowerShell + Bash + Python para automatización |
| [security/](#seguridad) | Checklists, patterns, hardening |
| [ai-patterns/](#ai-patterns) | Optimización LLM, routing, costos |
| [web-patterns/](#web-patterns) | CSS, animaciones, performance |
| [configs/](#configs) | Templates de configuración |
| [docs/](#docs) | Guías de referencia rápida |

---

## Scripts

### Windows
| Script | Función | Ejecutar |
|--------|---------|----------|
| `scripts/windows/cleanup.ps1` | Limpieza profunda Windows 11 | `.\cleanup.ps1` |
| `scripts/windows/harden.ps1` | Hardening de seguridad | `.\harden.ps1 -Level medium` |
| `scripts/windows/backup-configs.ps1` | Backup de configs importantes | `.\backup-configs.ps1` |
| `scripts/windows/monitor-resources.ps1` | Monitor de CPU/RAM/disk | `.\monitor-resources.ps1` |
| `scripts/windows/git-sync-all.ps1` | Sync todos los repos locales | `.\git-sync-all.ps1` |

### Linux/Mac
| Script | Función | Ejecutar |
|--------|---------|----------|
| `scripts/linux/setup-dev.sh` | Setup entorno desarrollo | `bash setup-dev.sh` |
| `scripts/linux/docker-cleanup.sh` | Limpiar Docker muerto | `bash docker-cleanup.sh` |
| `scripts/linux/ssl-check.sh` | Verificar certificados SSL | `bash ssl-check.sh dominio.com` |

### Python
| Script | Función | Ejecutar |
|--------|---------|----------|
| `scripts/python/api-racer.py` | Racing entre 2 providers LLM | `python api-racer.py` |
| `scripts/python/bulk-rename.py` | Renombrar archivos con regex | `python bulk-rename.py` |
| `scripts/python/find-secrets.py` | Buscar secrets en archivos | `python find-secrets.py .` |
| `scripts/python/simple-server.py` | Servidor HTTP rápido | `python simple-server.py 8000` |

---

## Seguridad

### OWASP Top 10 — Checklist Rápido
`security/owasp-checklist.md`

### Windows Hardening
`security/windows-hardening.md`
- Defender config
- Firewall rules
- BitLocker
- Audit policies
- Service hardening

### Git Security
`security/git-security.md`
- Pre-commit hooks para secret detection
- .gitignore patterns
- Branch protection rules
- Signed commits setup

### API Key Management
`security/api-key-management.md`
- Env vars vs vault vs keychain
- Rotation strategy
- Least privilege patterns

---

## AI Patterns

### Token Optimization
`ai-patterns/token-optimization.md`
- Compresión de contexto (60-90% ahorro)
- Routing por complejidad de tarea
- Cache de prompts
- Subagent delegation patterns

### Multi-Provider Routing
`ai-patterns/multi-provider-routing.md`
- Fallback chains
- Cost-based routing
- Latency-based routing
- Free tier maximization

### Prompt Engineering
`ai-patterns/prompt-engineering.md`
- System prompts efectivos
- Few-shot patterns
- Chain-of-thought
- Structured output

---

## Web Patterns

### CSS Architecture
`web-patterns/css-architecture.md`
- Design tokens system
- BEM methodology
- Utility-first vs component CSS
- Responsive patterns

### Animation Patterns
`web-patterns/animation-patterns.md`
- GSAP ScrollTrigger recipes
- CSS-only animations
- WebGL/Three.js starters
- Performance tips

### Performance
`web-patterns/performance.md`
- Core Web Vitals checklist
- Image optimization pipeline
- Font loading strategies
- Caching patterns

---

## Configs

| Archivo | Para qué |
|---------|----------|
| `configs/.editorconfig` | Formato consistente |
| `configs/.prettierrc` | Code style |
| `configs/.gitignore` | Git ignore completo |
| `configs/lighthouserc.json` | Performance audit |
| `configs/pyproject.toml` | Python project base |
| `configs/tsconfig.json` | TypeScript base |

---

## Docs

| Documento | Contenido |
|-----------|-----------|
| `docs/AWESOME-TOOLS.md` | 100+ herramientas open-source curadas |
| `docs/CHEATSHEETS.md` | Cheatsheets de Git, Docker, Python, JS |
| `docs/ERROR-PATTERNS.md` | Errores comunes y soluciones |
| `docs/PERFORMANCE-BUDGET.md` | Targets de performance |

---

## Fuentes

Todo curado de:
- GitHub Topics (developer-tools, security-tools, automation-scripts)
- OWASP Top 10 2025
- web.dev (Google)
- MDN Web Docs
- GreenSock (GSAP) docs
- Three.js docs
- Python docs
- PowerShell docs

---

*Toolkit generado: 2026-07-28*
*Licencia: MIT — usar libremente*
