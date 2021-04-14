from concurrent import futures
import os
import io
from collections import defaultdict
import logging

import requests
import grpc

import ImageService_pb2 as service
import ImageService_pb2_grpc as rpc

from domain.image_googlyeyz import GooglyEyezer

class ImageServiceServer(rpc.ImageServiceServicer):

    def __init__(self):
        self.images = defaultdict(io.BytesIO)
        logging.info("successfuly created the images store")
        self.googlyeyezer = GooglyEyezer()

    def Upload(self, request_iterator, context):
        i = 0
        for request in request_iterator:
            logging.info(f"Iteration: {i}")
            if request.StatusCode == service.ImageUploadStatusCode.InProgress:
                logging.info(f"bytes: {request.Content[0:10]}...")
                logging.info(f'> Req {request.Id} - receiving image')
                self.images[request.Id].write(request.Content)
                
                result = service.ImageUploadResponse(Id=request.Id, StatusCode=service.ImageUploadStatusCode.Ok, Message='waiting for more')

            if request.StatusCode == service.ImageUploadStatusCode.Ok and not request.Content:
                logging.info(f'> {request.Id} - received image')
                logging.info(f'> {request.Id} - googlyeyezing')
                image = self.images[request.Id].getvalue()
                logging.info(f"bytes: {image[0:10]}...")
                image_googlyeyezed = self.googlyeyezer.apply(io.BytesIO(image), "jpg")

                del self.images[request.Id]

                logging.info(f'> {request.Id} - googlyeyezed')
                result = service.ImageUploadResponse(Content= image_googlyeyezed.read(), Id=request.Id, StatusCode=service.ImageUploadStatusCode.Ok, Message="Processed")
                return result
            i+=1


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    port = 22223
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ImageServiceServicer_to_server(ImageServiceServer(), grpc_server)
    logging.info(f'Starting server. Listening at {port}...')
    grpc_server.add_insecure_port(f'[::]:{port}')
    grpc_server.start()
    grpc_server.wait_for_termination()
