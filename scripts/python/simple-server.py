"""
Simple HTTP Server — Sirve archivos estáticos rápido
Útil para testing local de HTML/CSS/JS.

Uso:
    python simple-server.py
    python simple-server.py 8000
    python simple-server.py --cors
    python simple-server.py --ssl
"""

import http.server
import socketserver
import argparse
import os
import sys
import ssl
import json
from pathlib import Path
from datetime import datetime

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Handler silencioso con CORS y headers de seguridad."""
    
    def __init__(self, *args, enable_cors=False, **kwargs):
        self.enable_cors = enable_cors
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        
        # CORS
        if self.enable_cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        
        # Cache para desarrollo
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Log silencioso pero informativo."""
        status = args[1] if len(args) > 1 else ""
        color = "\033[32m" if str(status).startswith("2") else "\033[31m"
        reset = "\033[0m"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"  {color}{timestamp} {args[0]} {status}{reset}")

def get_local_ip():
    """Obtiene la IP local."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    parser = argparse.ArgumentParser(description="Simple HTTP server")
    parser.add_argument("port", nargs="?", type=int, default=3000, help="Puerto (default: 3000)")
    parser.add_argument("--cors", action="store_true", help="Habilitar CORS")
    parser.add_argument("--ssl", action="store_true", help="Usar HTTPS (auto-signed)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--dir", default=".", help="Directorio a servir")
    
    args = parser.parse_args()
    
    # Cambiar al directorio
    os.chdir(args.dir)
    
    # Crear handler
    handler = lambda *a, **kw: QuietHandler(*a, enable_cors=args.cors, **kw)
    
    # Server
    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        httpd.allow_reuse_address = True
        
        # SSL opcional
        if args.ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain("cert.pem", "key.pem")
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        
        protocol = "https" if args.ssl else "http"
        local_ip = get_local_ip()
        
        print(f"\n🚀 Servidor activo:")
        print(f"   Local:    {protocol}://localhost:{args.port}")
        print(f"   Network:  {protocol}://{local_ip}:{args.port}")
        print(f"   Dir:      {os.path.abspath('.')}")
        print(f"   CORS:     {'✅ Habilitado' if args.cors else '❌ Deshabilitado'}")
        print(f"\n   Presiona Ctrl+C para detener\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Servidor detenido")
            httpd.shutdown()

if __name__ == "__main__":
    main()
