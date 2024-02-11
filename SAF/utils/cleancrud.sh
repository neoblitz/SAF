#!/bin/bash
echo "Deleting all pyc"
find ./ -name "*.pyc" -print -exec rm -f {} \;
find ./ -name "*.pyo" -print -exec rm -f {} \;
echo "Removing logs/ directory"
rm -rf logs/