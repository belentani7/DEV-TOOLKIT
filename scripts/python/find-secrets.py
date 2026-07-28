"""
find-secrets — Busca secrets/keys/API tokens en archivos
Detecta patrones comunes: API keys, passwords, tokens, connection strings.

Uso:
    python find-secrets.py .
    python find-secrets.py ./src --exclude node_modules
    python find-secrets.py . --format json
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

# Patrones de detección
PATTERNS = {
    "API Key (generic)": r"(?:api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?:aws_secret_access_key|secret_access_key)\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})['\"]?",
    "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
    "GitHub Fine-grained": r"github_pat_[A-Za-z0-9_]{82,}",
    "GitLab Token": r"glpat-[A-Za-z0-9\-_]{20,}",
    "Slack Token": r"xox[baprs]-[a-zA-Z0-9\-]{10,}",
    "Slack Webhook": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+",
    "Google API Key": r"AIza[0-9A-Za-z_\-]{35}",
    "Google OAuth": r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "OpenAI Key": r"sk-[a-zA-Z0-9]{20,}",
    "Anthropic Key": r"sk-ant-[a-zA-Z0-9\-]{20,}",
    "Azure Connection String": r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{44}",
    "Private Key BEGIN": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
    "Password in URL": r"://[^:]+:([^@]{8,})@",
    "Generic Secret": r"(?:secret|password|passwd|pwd)\s*[:=]\s*['\"]([^'\"]{8,})['\"]",
    "Bearer Token": r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
    "JWT Token": r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+",
    "Connection String": r"(?:mongodb|postgres|mysql|redis):\/\/[^\s]+",
    "IP with Port": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d{1,5}\b",
}

# Archivos a excluir
EXCLUDE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage",
    ".mimocode", ".claude", ".codex"
}

EXCLUDE_FILES = {
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe",
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp",
    "*.mp3", "*.mp4", "*.wav", "*.flac",
    "*.zip", "*.tar", "*.gz", "*.7z",
    "*.woff", "*.woff2", "*.ttf", "*.otf",
    "*.lock", "*.sum"
}

def should_exclude(path):
    """Verifica si un archivo/directorio debe ser excluido."""
    parts = Path(path).parts
    
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        if any(part.endswith(ext) for ext in EXCLUDE_FILES):
            return True
    
    return False

def scan_file(filepath):
    """Escanea un archivo buscando secrets."""
    findings = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            for pattern_name, regex in PATTERNS.items():
                matches = re.finditer(regex, line, re.IGNORECASE)
                for match in matches:
                    # No reportar en archivos de ejemplo/config
                    if ".example" in filepath or ".sample" in filepath:
                        continue
                    
                    findings.append({
                        "file": str(filepath),
                        "line": line_num,
                        "type": pattern_name,
                        "match": match.group()[:80],
                        "context": line.strip()[:120]
                    })
    except Exception:
        pass
    
    return findings

def scan_directory(root):
    """Escanea un directorio recursivamente."""
    all_findings = []
    scanned = 0
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Filtrar directorios excluidos
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            if should_exclude(filepath):
                continue
            
            # Solo archivos de texto
            try:
                size = os.path.getsize(filepath)
                if size > 1_000_000:  # Skip >1MB
                    continue
            except OSError:
                continue
            
            findings = scan_file(filepath)
            all_findings.extend(findings)
            scanned += 1
    
    return all_findings, scanned

def print_findings(findings, format="text"):
    """Imprime los findings."""
    if format == "json":
        print(json.dumps(findings, indent=2, ensure_ascii=False))
        return
    
    if not findings:
        print("\n✅ No se encontraron secrets")
        return
    
    print(f"\n⚠️  {len(findings)} secrets potenciales encontrados:\n")
    
    # Agrupar por tipo
    by_type = {}
    for f in findings:
        by_type.setdefault(f["type"], []).append(f)
    
    for secret_type, items in sorted(by_type.items()):
        print(f"📋 {secret_type} ({len(items)} ocurrencias)")
        for item in items[:3]:  # Max 3 por tipo
            print(f"   {item['file']}:{item['line']}")
            print(f"   → {item['context'][:100]}")
        if len(items) > 3:
            print(f"   ... y {len(items)-3} más")
        print()

def main():
    parser = argparse.ArgumentParser(description="Buscar secrets en archivos")
    parser.add_argument("path", nargs="?", default=".", help="Directorio a escanear")
    parser.add_argument("--exclude", default="", help="Dirs adicionales a excluir")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--no-git", action="store_true", help="Excluir .git")
    
    args = parser.parse_args()
    
    if args.exclude:
        for d in args.exclude.split(","):
            EXCLUDE_DIRS.add(d.strip())
    
    print(f"\n🔍 Escaneando: {os.path.abspath(args.path)}\n")
    
    findings, scanned = scan_directory(args.path)
    
    print(f"Archivos escaneados: {scanned}")
    
    print_findings(findings, args.format)
    
    # Exit code
    sys.exit(1 if findings else 0)

if __name__ == "__main__":
    main()
