#!/bin/zsh
python3 src/pr4.py --vfs-path vfs/several.json --script tests_pr4/start_vfs_command.txt
echo "//////////////////////////////////////////"
echo "//////////////////////////////////////////"
echo "//////////////////////////////////////////"
python3 src/pr4.py --vfs-path vfs/several.json --script tests_pr4/start_vfs_err.txt