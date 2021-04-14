#!/bin/bash
#####
#Usage:
#   `./setup_service_dependencies.sh -d 1` to install dev dependencies
#   `./setup_service_dependencies.sh -d 0` to install dev dependencies
#####
DEV=0
PYTHON_PATH=`which python`
while getopts ":d:p:" opt; do
  case $opt in
    d)
      echo "dev to be installed" >&2
      DEV=${OPTARG}
      ;;
    p)
      PYTHON_PATH=${OPTARG}
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

$PYTHON_PATH -m pip install -r requirements.txt
if [ "$DEV" = "1" ]; then
    $PYTHON_PATH -m pip install -r requirements-dev.txt
fi

mkdir -p ./dependencies/ImageServiceGRPCModules/src

$PYTHON_PATH -m grpc_tools.protoc -I ./dependencies --python_out=./dependencies/ImageServiceGRPCModules/src --grpc_python_out=./dependencies/ImageServiceGRPCModules/src ./dependencies/ImageService.proto

cp ./dependencies/setup.py ./dependencies/ImageServiceGRPCModules
