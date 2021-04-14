import uuid
import datetime
import logging
import json
from flask import Flask, flash, request, redirect, make_response, render_template_string
from PIL import Image
import requests
from io import BytesIO
import urllib

import grpc
import ImageService_pb2 as service
import ImageService_pb2_grpc as rpc
from google.protobuf.json_format import MessageToJson

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", ".gif"}
CHUNK_SIZE = 1024 * 1024

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        filename = None
        if "selected_files" not in request.files and "image_url" not in request.form:
            flash("No 'selected_files' part nor image url")
            return redirect(request.url)

        if "selected_files" in request.files:

            file = request.files["selected_files"]
            # for i, file in enumerate(selected_files, 1):
            if file.filename == "":
                flash("You must select at least one file")
                return redirect(request.url)
            else:
                filename = file.filename

            if file and allowed_file(filename):
                fileid = f"{datetime.datetime.utcnow().isoformat()}-{uuid.uuid4()}"
        else:
            filename = request.form["image_url"].strip()
            logging.info(filename)
            img_extension = filename.split(".")[-1].strip()
            if img_extension.lower() == "jpg":
                img_extension = "jpeg"
            url = urllib.request.urlopen(filename)
            file = BytesIO(url.read())

            fileid = f"{datetime.datetime.utcnow().isoformat()}-{uuid.uuid4()}"

        # def upload_request_generator():  # this generates our grpc `stream ImageUploadRequest`
        my_result = []
        while True:
            b = file.read(CHUNK_SIZE)
            logging.info(b)
            if b:
                result = service.ImageUploadRequest(
                    Content=b,
                    Id=fileid,
                    StatusCode=service.ImageUploadStatusCode.InProgress,
                )  # noqa
                logging.info("Sending...")
                my_result.append(result)
            else:
                result = service.ImageUploadRequest(
                    Id=fileid, StatusCode=service.ImageUploadStatusCode.Ok
                )  # noqa
                logging.info("...Sent")
                my_result.append(result)
                logging.info(f"len of list is {len(my_result)}")
                break
        my_result = iter(my_result)

        result = stub.Upload(my_result)
        logging.info(result)
        logging.info(f"file {filename} was upload successfully")

        response = make_response(result.Content)
        response.headers.set("Content-Type", "image/jpeg")
        response.headers.set(
            "Content-Disposition", "attachment", filename=f"{filename}_googlyeyzed.jpg"
        )
        return response
    return render_template_string(
        """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=selected_files>
      <input type=submit value=Upload Local Image>
    </form>
    <form method=post enctype=multipart/form-data>
      <input type=text name=image_url>
      <input type=submit value=Upload Image URL>
    </form>
    """,
        json_response=request.args.get("json"),
    )


if __name__ == "__main__":
    channel = grpc.insecure_channel("localhost:22223")
    stub = rpc.ImageServiceStub(channel)
    app.run(host="0.0.0.0")
