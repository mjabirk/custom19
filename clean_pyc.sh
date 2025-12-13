#!/bin/bash
#
# This script finds and deletes all .pyc files and __pycache__ directories
# from the current directory and all subdirectories.

echo "Finding and deleting .pyc files..."
# The -delete flag is efficient for just deleting files
find . -type f -name "*.pyc" -delete

echo "Finding and deleting __pycache__ directories..."
# For directories, we must use -exec rm -rf
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Cleanup complete."

