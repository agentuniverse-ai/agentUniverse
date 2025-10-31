#!/bin/bash

PROJECT_NAME=$(basename $(cd ../ && pwd))
IMAGE_NAME=${PROJECT_NAME}
IMAGE_TAG="latest"

echo "Project name detected: $PROJECT_NAME"

rm -rf ./project_files
mkdir -p ./project_files

cd ../
find . -mindepth 1 -maxdepth 1 -not -name "image_build" -exec cp -r {} image_build/project_files/ \;
cd image_build

docker build --no-cache --platform linux/amd64 --build-arg PROJECT_NAME=$PROJECT_NAME --tag=${IMAGE_NAME}:${IMAGE_TAG} .

rm -rf ./project_files