# OWASP Top 10 2025 — Checklist Rápido

## A01: Broken Access Control
- [ ] Principio de mínimo privilegio
- [ ] Denegar por defecto
- [ ] Revisar CORS en todos los endpoints
- [ ] Proteger rutas admin con role check
- [ ] No exponer IDs secuenciales (usar UUIDs)
- [ ] Rate limiting en endpoints sensibles

## A02: Cryptographic Failures
- [ ] No guardar passwords en texto plano (usar bcrypt/argon2)
- [ ] HTTPS forzado (HSTS preload)
- [ ] TLS 1.2+ únicamente
- [ ] No hardcodear secrets en código
- [ ] Usar env vars o vault para secrets
- [ ] Rotación periódica de keys

## A03: Injection
- [ ] Parameterized queries (nunca concatenar SQL)
- [ ] Input validation en todos los endpoints
- [ ] Output encoding para XSS
- [ ] No usar eval() o exec() con input del usuario
- [ ] Sanitizar HTML (DOMPurify, bleach)
- [ ] Content-Type validation

## A04: Insecure Design
- [ ] Threat modeling antes de implementar
- [ ] Separación de entornos (dev/staging/prod)
- [ ] Rate limiting por usuario e IP
- [ ] Circuit breaker para servicios externos
- [ ] Graceful degradation

## A05: Security Misconfiguration
- [ ] Headers de seguridad (CSP, X-Frame-Options, etc.)
- [ ] CORS restrictivo (no wildcard *)
- [ ] Deshabilitar directorio listing
- [ ] Cambiar credenciales default
- [ ] Revisar permisos de archivos (644/755)
- [ ] Deshabilitar debug en producción

## A06: Vulnerable Components
- [ ] npm audit / pip audit regular
- [ ] Dependabot/Renovate habilitado
- [ ] SBOM generado
- [ ] Versiones pinned
- [ ] Sin dependencias deprecated

## A07: Authentication Failures
- [ ] MFA habilitado
- [ ] Rate limiting en login (brute force protection)
- [ ] Session timeout configurado
- [ ] Password policy (mín 12 chars, complexity)
- [ ] Account lockout después de N intentos
- [ ] Invalidación de sesión al cambiar password

## A08: Software and Data Integrity
- [ ] Signed commits
- [ ] CI/CD pipeline protegido
- [ ] Code review obligatorio
- [ ] Verified downloads (checksums)
- [ ] No usar `npm install` sin lockfile

## A09: Logging Failures
- [ ] Log de intentos de login (fallo y éxito)
- [ ] Log de accesos a datos sensibles
- [ ] Log de cambios de permisos
- [ ] No loggear passwords o tokens
- [ ] Alertas para patrones sospechosos
- [ ] Retención de logs definida

## A10: Server-Side Request Forgery (SSRF)
- [ ] Validar URLs de input del usuario
- [ ] Whitelist de dominios permitidos
- [ ] No seguir redirects de URLs del usuario
- [ ] Aislar servicios internos
- [ ] Network segmentation

---

## Headers de Seguridad (Copy-paste)

### Apache (.htaccess)
```apache
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "DENY"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

### Nginx
```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com; img-src 'self' data:" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Express.js
```javascript
const helmet = require('helmet');
app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"],
    styleSrc: ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
    fontSrc: ["fonts.gstatic.com"],
    imgSrc: ["'self'", "data:"],
  }
}));
```
