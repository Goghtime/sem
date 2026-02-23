#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${HOME}/.local/bin"
LINK_NAME="sem"

if [[ ! -L "${INSTALL_DIR}/${LINK_NAME}" ]]; then
  echo "not installed: ${INSTALL_DIR}/${LINK_NAME} does not exist or is not a symlink"
  exit 0
fi

rm "${INSTALL_DIR}/${LINK_NAME}"
echo "uninstalled: removed ${INSTALL_DIR}/${LINK_NAME}"
