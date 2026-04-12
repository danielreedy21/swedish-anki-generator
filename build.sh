#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "==> Building Flask server with PyInstaller..."
python3 -m PyInstaller flask-server.spec --distpath flask-dist --noconfirm

echo "==> Building Electron app..."
cd electron
npm run build

echo ""
echo "Done! App is at: electron/release/Swedish Anki-*.dmg"
