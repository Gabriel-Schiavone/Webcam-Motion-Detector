import time

from PIL import Image
import cv2
import os
import smtplib
import imghdr
from email.message import EmailMessage
import threading


def calculate_brightness(image):
    greyscale_image = image.convert('L')
    histogram = greyscale_image.histogram()
    pixels = sum(histogram)
    brightness = scale = len(histogram)

    for index in range(0, scale):
        ratio = histogram[index] / pixels
        brightness += ratio * (-scale + index)

    return 1 if brightness == 255 else brightness / scale


def send_mail(image_f, target):
    Sender_Email = THE_BOT'S_EMAIL
    Reciever_Email = target
    Password = THE_BOT'S_EMAIL_PASSWORD

    newMessage = EmailMessage()
    newMessage['Subject'] = "Motion Detected"
    newMessage['From'] = Sender_Email
    newMessage['To'] = Reciever_Email

    with open(image_f, 'rb') as f:
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.name
        f.close()

    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(Sender_Email, Password)
        smtp.send_message(newMessage)
    time.sleep(.5)
    os.remove(image_f)


sens = 0.2
recipient = input('please enter your Email: ')
x = 0
res = 5
vc = cv2.VideoCapture(0)
prev_b_val = []
for num in range(res * res):
    prev_b_val.append(0)

while True:
    rval, frame = vc.read()
    cv2.imwrite("frame.png", frame)
    image = Image.open("frame.png")
    width, height = image.size

    row = 0
    column = 0
    current_pixel = 0
    l = 0
    t = 0
    r = 0
    b = 0
    b_val = []

    while row < res:
        while column < res:
            l = column * (width / res)
            t = row * (height / res)
            r = (column + 1) * (width / res)
            b = (row + 1) * (width / res)

            image_cropped = image.crop((l, t, r, b))

            brightness = calculate_brightness(image_cropped)
            b_val.append(brightness)

            if brightness > prev_b_val[current_pixel]:
                b_diff = brightness - prev_b_val[current_pixel]
            else:
                b_diff = prev_b_val[current_pixel] - brightness
            if b_diff > sens:
                x += 1
                if not x % 5:
                    print(x)
                    print("\nMotion Detected\n")
                    image_f = 'motion' + str(x) + '.png'
                    cv2.imwrite(image_f, frame)
                    foo = threading.Thread(target=send_mail, args=(image_f, recipient))
                    foo.start()

            column += 1
            current_pixel += 1
        row += 1
        column = 0
    os.remove("frame.png")
    print("Cycle Complete")
    prev_b_val = b_val
    time.sleep(.5)
