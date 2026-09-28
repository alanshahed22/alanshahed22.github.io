#!/bin/bash
# Simple script to deploy blog updates to GitHub Pages

set -e

# Change directory to the blog folder
cd "$(dirname "$0")"

# Commit message (default: "Update blog" if none provided)
COMMIT_MSG="${1:-Update blog}"

echo "Adding changes..."
git add .

echo "Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || { echo "No new changes to commit."; exit 0; }

echo "Pushing to GitHub..."
git push origin main

echo ""
echo "✓ Successfully deployed! Changes will be live on your GitHub Pages site in ~1 minute."
