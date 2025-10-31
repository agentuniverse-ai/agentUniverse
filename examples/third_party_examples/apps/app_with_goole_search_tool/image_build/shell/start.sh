#!/bin/bash


TARGET_DIR="/usr/local/etc/workspace/project"

if [ -z "$(ls -A "$TARGET_DIR")" ]; then
    mv /usr/local/etc/workspace/${PROJECT_NAME} $TARGET_DIR
    echo "use default project"
else
    rm -rf /usr/local/etc/workspace/${PROJECT_NAME}
fi

DIR_COUNT=$(find "$TARGET_DIR" -maxdepth 1 -type d | wc -l)
if [ "$DIR_COUNT" -eq 2 ]; then
    UNIQUE_DIR=$(find "$TARGET_DIR" -maxdepth 1 -type d | tail -n 1)
    cd "$UNIQUE_DIR"
else
    echo "please only place one directory under project"
fi


cd ./bootstrap/platform

nohup python3 -u product_application.py &

cd ../intelligence
python3 -u server_application.py
