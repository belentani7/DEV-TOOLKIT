# Cheatsheets — Git, Docker, Python, JS

---

## Git

```bash
# Status
git status
git log --oneline -10
git diff --stat

# Branches
git branch -a
git checkout -b feature/nueva
git branch -d feature/old

# Stash
git stash push -m "description"
git stash list
git stash pop

# Undo
git reset --soft HEAD~1          # Undo commit, keep changes
git reset --hard HEAD~1          # Undo commit + changes
git checkout -- file.txt         # Discard file changes
git revert <commit>             # Create reverse commit

# Rebase
git rebase main
git rebase -i HEAD~5            # Interactive rebase

# Cherry-pick
git cherry-pick <commit>

# Tags
git tag -a v1.0.0 -m "Release"
git push origin v1.0.0

# Aliases útiles
git config --global alias.st "status -sb"
git config --global alias.co "checkout"
git config --global alias.br "branch"
git config --global alias.cm "commit -m"
git config --global alias.last "log -1 HEAD --stat"
git config --global alias.unstage "reset HEAD --"
```

---

## Docker

```bash
# Containers
docker ps                           # Running
docker ps -a                        # All
docker run -d --name app -p 3000:3000 image
docker stop app && docker rm app
docker exec -it app sh              # Shell

# Images
docker images
docker build -t myapp .
docker rmi <image>
docker system prune -af             # Clean all

# Compose
docker compose up -d
docker compose down
docker compose logs -f
docker compose ps

# Volumes
docker volume ls
docker volume rm <volume>

# Networks
docker network ls
docker network inspect <network>

# Multi-stage build pattern
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

---

## Python

```bash
# Package management (uv - recomendado)
uv init myproject
uv add fastapi uvicorn
uv add --dev pytest ruff pyright
uv run python main.py

# Testing
pytest                           # Run all
pytest -x                        # Stop on first fail
pytest -v                        # Verbose
pytest --cov=src                 # Coverage
pytest tests/test_api.py         # Single file

# Linting
ruff check .                     # Lint
ruff format .                    # Format
pyright                          # Type check

# Virtual env
python -m venv .venv
source .venv/bin/activate         # Linux/Mac
.venv\Scripts\activate            # Windows

# FastAPI
uvicorn main:app --reload
```

---

## JavaScript / Node.js

```bash
# Package management
npm init -y
npm install express
npm install -D eslint prettier

# Scripts (package.json)
npm run dev                       # Development
npm run build                     # Production
npm test                          # Tests

# Node
node --watch app.js               # Auto-reload (Node 18+)
node --inspect app.js             # Debugger

# npx
npx create-vite my-app --template react-ts
npx eslint src/
npx prettier --write .

# Yarn / pnpm
yarn add <package>
pnpm add <package>
```

---

## SSH

```bash
# Generate key
ssh-keygen -t ed25519 -C "email@example.com"

# Copy to server
ssh-copy-id user@host

# Config (~/.ssh/config)
Host myserver
    HostName 192.168.1.100
    User deploy
    Port 22
    IdentityFile ~/.ssh/id_ed25519

# Tunnel
ssh -L 3000:localhost:3000 user@host
ssh -R 8080:localhost:3000 user@host
```

---

## Curl

```bash
# GET
curl https://api.example.com/data

# POST JSON
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'

# With auth
curl -H "Authorization: Bearer TOKEN" https://api.example.com

# Download
curl -O https://example.com/file.zip

# Verbose
curl -v https://api.example.com

# Follow redirects
curl -L https://example.com
```
