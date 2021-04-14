./venv/bin/python3 -m pip install -r requirements.txt
./venv/bin/python3 -m pip install -r requirements-dev.txt

mkdir -p ./service/dependencies/ImageServiceGRPCModules/src

./venv/bin/python3 -m grpc_tools.protoc -I ./service/dependencies --python_out=./service/dependencies/ImageServiceGRPCModules/src --grpc_python_out=./service/dependencies/ImageServiceGRPCModules/src ./service/dependencies/ImageService.proto

cp ./service/dependencies/setup.py ./service/dependencies/ImageServiceGRPCModules
