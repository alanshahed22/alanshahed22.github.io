#!/bin/bash
# Resolve directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

clear
echo "=========================================================="
echo "         ✍️  Alan's Minimal Blog Editor & Publisher       "
echo "=========================================================="
echo " Starting local editor server..."
echo " Opening http://127.0.0.1:4321 in your browser..."
echo ""
echo " Keep this terminal window open while writing."
echo " When done, close this window or press Ctrl+C."
echo "=========================================================="

/usr/bin/python3 "$DIR/server.py"
