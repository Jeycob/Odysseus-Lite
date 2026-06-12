#!/usr/bin/env bash
set -euo pipefail

TOOLS_DIR="${ODYSSEUS_TOOLS_DIR:-/share/odysseus-tools}"
INSTALL_DIR="${DOTNET_INSTALL_DIR:-${TOOLS_DIR}/dotnet}"
BIN_DIR="${TOOLS_DIR}/bin"
CHANNEL="${DOTNET_CHANNEL:-LTS}"

mkdir -p "${INSTALL_DIR}" "${BIN_DIR}"

SCRIPT="${TOOLS_DIR}/dotnet-install.sh"
curl -fsSL https://dot.net/v1/dotnet-install.sh -o "${SCRIPT}"
chmod +x "${SCRIPT}"

"${SCRIPT}" --channel "${CHANNEL}" --install-dir "${INSTALL_DIR}" --no-path "$@"
ln -sf "${INSTALL_DIR}/dotnet" "${BIN_DIR}/dotnet"

echo "dotnet installed at ${INSTALL_DIR}"
echo "Use: export PATH=${BIN_DIR}:${INSTALL_DIR}:\$PATH"
dotnet --info || "${INSTALL_DIR}/dotnet" --info
