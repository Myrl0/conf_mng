#!/bin/zsh
python3 src/pr5.py --vfs-path vfs/several.json --script tests_pr5/start.txt
echo "Скрипт с ошибкой запущен"
echo "////////////////////SEVERALTEST//////////////////////"
echo "////////////////////SEVERALTEST//////////////////////"
echo "////////////////////SEVERALTEST//////////////////////"
python3 src/pr5.py --vfs-path vfs/several.json --script tests_pr5/start_err.txt