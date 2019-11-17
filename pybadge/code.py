import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
from adafruit_pybadger import PyBadger 
import neopixel

OFF = (0,0,0)
BLUE = (32,32,255)
pybadger = PyBadger()
pixels = pybadger.pixels
pixels.brightness = 0.005
pixels.fill(OFF)
pixels.show()


def show_badge():
    pybadger.show_badge(name_string="Mark", hello_scale=1, my_name_is_scale=1, name_scale=1)


def show_wildcat():
    pybadger.show_business_card(image_name="wildcat.bmp",email_string_two="fischerm@email.arizona.edu")


def aws_announcements():
    pybadger.aws_announcements(name_string="38", 
                                hello_scale=1, 
                                my_name_is_scale=1, 
                                name_scale=1
                                )


aws_announcements()

while True:
    pybadger.auto_dim_display(delay=50) # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        board.DISPLAY.brightness = 1
        show_wildcat()
    elif pybadger.button.b:
        board.DISPLAY.brightness = 1
        pybadger.show_qr_code(data="https://www.arizona.edu")
    elif pybadger.button.start:
        board.DISPLAY.brightness = 1
        show_badge()
    elif pybadger.button.up:
        board.DISPLAY.brightness = 1
        aws_announcements()
