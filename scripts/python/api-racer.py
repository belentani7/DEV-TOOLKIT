"""
API Racer — Racing entre 2+ providers LLM
Lanza request al mismo tiempo, usa la respuesta más rápida.

Uso:
    python api-racer.py "Tu prompt aquí"
    python api-racer.py --providers groq,gemini "Tu prompt"
    python api-racer.py --timeout 10 "Tu prompt"

Requiere: pip install requests
"""

import sys
import os
import time
import json
import argparse
import concurrent.futures
import requests

# Providers gratuitos configurados
# Las claves se leen de variables de entorno — NUNCA hardcodeadas (repo publico).
PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": os.environ.get("GROQ_API_KEY", ""),
        "model": "llama-3.3-70b-versatile",
        "headers_key": "Authorization",
        "prefix": "Bearer "
    },
    "nvidia": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key": os.environ.get("NVIDIA_API_KEY", ""),
        "model": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
        "headers_key": "Authorization",
        "prefix": "Bearer "
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": os.environ.get("OPENROUTER_API_KEY", ""),
        "model": "google/gemma-2-9b-it:free",
        "headers_key": "Authorization",
        "prefix": "Bearer "
    }
}

def call_provider(name, config, prompt, timeout):
    """Llama a un provider y retorna tiempo + respuesta."""
    start = time.time()
    try:
        headers = {
            "Content-Type": "application/json",
            config["headers_key"]: f"{config['prefix']}{config['key']}"
        }
        
        payload = {
            "model": config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        resp = requests.post(
            config["url"],
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", "?")
            return {
                "provider": name,
                "model": config["model"],
                "elapsed": round(elapsed, 2),
                "tokens": tokens,
                "content": content,
                "status": "success"
            }
        else:
            return {
                "provider": name,
                "model": config["model"],
                "elapsed": round(elapsed, 2),
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                "status": "error"
            }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "provider": name,
            "model": config["model"],
            "elapsed": round(elapsed, 2),
            "error": str(e),
            "status": "error"
        }

def race(prompt, providers=None, timeout=30):
    """Racea entre providers y retorna el más rápido."""
    if providers is None:
        providers = list(PROVIDERS.keys())
    
    print(f"\n🏁 Racing {len(providers)} providers...\n")
    print(f"Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}\n")
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {}
        for name in providers:
            if name in PROVIDERS:
                futures[executor.submit(call_provider, name, PROVIDERS[name], prompt, timeout)] = name
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result["status"] == "success":
                print(f"  ✅ {result['provider']} ({result['model']}) — {result['elapsed']}s, {result['tokens']} tokens")
            else:
                print(f"  ❌ {result['provider']} — {result['error'][:60]}")
    
    # Ordenar por velocidad
    successful = [r for r in results if r["status"] == "success"]
    if successful:
        successful.sort(key=lambda x: x["elapsed"])
        winner = successful[0]
        
        print(f"\n{'='*60}")
        print(f"🏆 GANADOR: {winner['provider']} ({winner['elapsed']}s)")
        print(f"{'='*60}\n")
        print(winner["content"])
        
        return winner
    else:
        print("\n❌ Todos los providers fallaron")
        return None

def main():
    parser = argparse.ArgumentParser(description="API Racer - LLM provider racing")
    parser.add_argument("prompt", help="Prompt para enviar")
    parser.add_argument("--providers", default="groq,nvidia,openrouter", help="Providers separados por coma")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout por provider (segundos)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    providers = [p.strip() for p in args.providers.split(",")]
    
    result = race(args.prompt, providers, args.timeout)
    
    if args.json and result:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
