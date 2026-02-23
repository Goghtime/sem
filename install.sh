#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.local/bin"
LINK_NAME="sem"

mkdir -p "$INSTALL_DIR"

if [[ -e "${INSTALL_DIR}/${LINK_NAME}" ]]; then
  echo "already installed: ${INSTALL_DIR}/${LINK_NAME} → $(readlink "${INSTALL_DIR}/${LINK_NAME}")"
  exit 0
fi

ln -s "${SCRIPT_DIR}/sem" "${INSTALL_DIR}/${LINK_NAME}"
echo "installed: ${INSTALL_DIR}/${LINK_NAME} → ${SCRIPT_DIR}/sem"
