# DEV Toolkit

Colección de herramientas y referencias para desarrollo. El repositorio está configurado como **privado** y actualmente no incluye un manifiesto de dependencias.

## Contenido disponible

### Scripts

- [Limpieza de Windows](scripts/windows/cleanup.ps1)
- [Copia de configuración](scripts/windows/backup-configs.ps1)
- [Comparador de proveedores de API](scripts/python/api-racer.py)
- [Búsqueda de secretos en archivos](scripts/python/find-secrets.py)
- [Servidor HTTP sencillo](scripts/python/simple-server.py)

### Seguridad

- [Checklist OWASP](security/owasp-checklist.md)
- [Seguridad de Git](security/git-security.md)

### Configuración

- [.editorconfig](configs/.editorconfig)
- [Prettier](configs/.prettierrc)
- [Reglas de exclusión de Git](configs/.gitignore)

### Referencias

- [Herramientas curadas](docs/AWESOME-TOOLS.md)
- [Cheatsheets](docs/CHEATSHEETS.md)

Este inventario enlaza solo archivos que existen en `main`. Los nombres de scripts y documentos que aparecían antes en el README pero no estaban en el repositorio se retiraron.

## Verificación

El workflow de GitHub Actions usa Python 3.12 y ejecuta:

```bash
python -m compileall -q .
```

Esto comprueba la sintaxis de los archivos Python; el repositorio no declara una suite de pruebas automatizadas.

## Licencia y acceso

El contenido está bajo [licencia MIT](LICENSE). El repositorio permanece privado; la licencia no cambia su visibilidad.
