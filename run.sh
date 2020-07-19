#!/bin/sh

if [ $# -eq 0 ]
then
    echo "Usage: bash run.sh <terminal>"
    echo "Options: xterm, macos, konsole, git (for git bash)"
    exit 1
fi

script_full_path=$(pwd)
term=$1

if [ $term == "xterm" ]
then
    xterm -title "Redis Server" -e "bash $script_full_path/run-redis.sh" 
    xterm -title "Celery" -e "cd $script_full_path; celery worker -A main.celery -loglevel=info" 
    xterm -title "Web App" -e "python3 $script_full_path/main.py"
elif [ $term == "macos" ]
then
    osascript -e 'tell application "Terminal" to do script "bash '$script_full_path'/run-redis.sh"' 
    osascript -e 'tell application "Terminal" to do script "cd '$script_full_path';celery worker -A main.celery --loglevel=info"' 
    osascript -e 'tell application "Terminal" to do script "python3 '$script_full_path'/main.py"' 
elif [ $term == "konsole" ]
then
    konsole -e "bash $script_full_path/run-redis.sh"
    konsole -e "cd $script_full_path; celery worker -A main.celery -loglevel=info" 
    konsole -e "python3 $script_full_path/main.py"
elif [ $term == "git" ]
then
    # Found this below but idk how it works
    # (cd C:$script_full_path && start sh --login) &
    # (cd D:/path/to/dir2 && start sh --login) &
    echo "use git bash"
fi 

