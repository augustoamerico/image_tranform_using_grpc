from io import BytesIO
import numpy as np
import cv2
import imutils
import random


class GooglyEyezer:
    def __init__(self, googly_eyes_path_image: str = "./googly_eye_tr.png"):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        self.googly_eye_path_image = googly_eyes_path_image
        self.googly_eye = cv2.imread(googly_eyes_path_image, cv2.IMREAD_UNCHANGED)

    def apply(
        self,
        image_stream: BytesIO,
        image_encode: str = "jpg",
        eyes_rotation_randomize_seed=12345,
    ) -> BytesIO:
        image_stream.seek(0)
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 8)

        for (x, y, w, h) in faces:
            roi_gray = gray[y : y + h, x : x + w]
            roi_color = img[y : y + h, x : x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.3, 5)
            for (ex, ey, ew, eh) in eyes:
                eye = cv2.resize(self.googly_eye.copy(), (ew, eh))
                eye = imutils.rotate(eye, int(360 * random.random()))
                rows, cols, channels = eye.shape
                b, g, r, a = cv2.split(eye)
                overlay_color = cv2.merge((b, g, r))

                mask = cv2.medianBlur(a, 5)
                h, w, _ = overlay_color.shape

                img_eye_roi = roi_color[ey : ey + cols, ex : ex + rows]

                img1_bg = cv2.bitwise_and(
                    img_eye_roi.copy(), img_eye_roi.copy(), mask=cv2.bitwise_not(mask)
                )
                img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)

                roi_color[ey : ey + ew, ex : ex + eh] = cv2.add(img1_bg, img2_fg)

        is_success, im_buf_arr = cv2.imencode(f".{image_encode}", img)
        if is_success:
            return BytesIO(im_buf_arr)
        raise Exception("Unable to encode image")


"""
googlyzer = GooglyEyezer('/home/tds/Pictures/googly_eye_tr.png')
raw_url = "https://www.tenhomaisdiscosqueamigos.com/wp-content/uploads/2017/06/dave-grohl-2013-shutterstock.jpg"
img_url = raw_url.strip()
img_pil = Image.open(requests.get(img_url, stream=True).raw)
image_in_bytes = BytesIO(img_pil.tobytes())

#image =  open('/home/tds/Pictures/joao_pedro_antonio.jpg', 'rb')
#f = image.read()
#b = bytearray(f)
#image_in_bytes = BytesIO(b)
response_bytes = googlyzer.apply(image_in_bytes, "jpg")
im = Image.open(image_in_bytes).convert("RGBA")
image_in_bytes.close()
im.show()


raw_url = "https://www.tenhomaisdiscosqueamigos.com/wp-content/uploads/2017/06/dave-grohl-2013-shutterstock.jpg"
img_url = raw_url.strip()

with urllib.request.urlopen(raw_url) as url:
    resp = url.read()
    image = np.asarray(bytearray(resp), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    cv2.imshow("img", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
"""
