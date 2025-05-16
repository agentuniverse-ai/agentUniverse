#!/usr/bin/env bash

set -euo pipefail

TOOLS=("duckduckgo-mcp-server" "mcp-server-office")
UV_INSTALL_URL_UNIX="https://astral.sh/uv/install.sh"
UV_INSTALL_URL_WIN="https://astral.sh/uv/install.ps1"

# ---------- 1. install uv --------------------------------------------------------
if command -v uv >/dev/null 2>&1; then
    echo "[✔] uv already exists：$(command -v uv)"
else
    case "$(uname -s)" in
        Linux|Darwin)
            echo "[→] Installing uv (Unix)…"
            curl -LsSf "$UV_INSTALL_URL_UNIX" | sh
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "[→] Installing uv (Windows, via PowerShell)…"
            powershell -NoProfile -ExecutionPolicy Bypass \
              -Command "irm $UV_INSTALL_URL_WIN | iex"
            ;;
        *)
            echo "[✖] Unknown system，please install uv manually！"; exit 1 ;;
    esac
fi

# ---------- 2. update PATH ---------------------------------------------------
case "$(uname -s)" in
    Linux|Darwin) export PATH="$HOME/.local/bin:$PATH" ;;
    *)            export PATH="$HOME/.local/bin:$PATH" ;;
esac

echo "[✔] Current uv version：$(uv --version)"

# ---------- 3. Install tools ---------------------------------------------------
for tool in "${TOOLS[@]}"; do
    echo "[→] Install tool: $tool"
    uv tool install "$tool"
done

echo "[✓] Accomplished！Installed tools: ${TOOLS[*]}"
