import board
import busio
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests
from adafruit_pybadger import PyBadger 
import neopixel
import json
from secrets import secretsAWS, secretsPhone
import time


OFF = (0,0,0)
BLUE = (32,32,255)
pybadger = PyBadger()
pixels = pybadger.pixels
pixels.brightness = 0.005
pixels.fill(OFF)
pixels.show()

# Store number of service globally
services_count = 79

# Setup WiFi
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset, debug=True)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])


def connect_to_wifi(location="phone"):
    wifi_not_connected = True
    wifi_connect_attempts = 0

    print("trying to connect to " + location)
    pybadger.show_badge(name_string="WiFi", hello_string="Connecting", my_name_is_string=location, hello_scale=1, my_name_is_scale=1, name_scale=1)

    if location == "phone":
        user = secretsPhone['wifi_user']
        password = secretsPhone['wifi_pass']
    elif location == "aws":
        user = secretsAWS['wifi_user']
        password = secretsAWS['wifi_pass']

    while wifi_connect_attempts < 3 or wifi_not_connected:
        try:
            esp.connect_AP(user, password)
            wifi_not_connected = False
        except Exception as e:
            print(e)
            wifi_connect_attempts = wifi_connect_attempts + 1
            pass

    print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
    print("My IP address is", esp.pretty_ip(esp.ip_address))

    time.sleep(2)


def show_badge():
    pybadger.show_badge(name_string="Mark", hello_scale=1, my_name_is_scale=1, name_scale=1)


def show_wildcat():
    pybadger.show_business_card(image_name="wildcat.bmp",email_string_two="fischerm@email.arizona.edu")


def update_aws_count(incriment=0):
    global services_count
    services_count = services_count + incriment


def aws_announcements():
    global services_count
    # pybadger.aws_announcements(name_string="000", 
    #                             hello_scale=1, 
    #                             my_name_is_scale=1, 
    #                             name_scale=1
    #                             )

    try:
        # def request(method, url, data=None, json=None, headers=None, stream=False, timeout=1):
        # stats_resp = requests.get("https://f3m81lupa9.execute-api.us-west-2.amazonaws.com/dev/stats", timeout=5)
        # stats = stats_resp.json()
        # services_count = stats['count']
        pybadger.aws_announcements(name_string=str(services_count), 
                                    hello_scale=1, 
                                    my_name_is_scale=1, 
                                    name_scale=1
                                    )
    except Exception as e:
        print("failed to fetch stats")
        print(e)
        pass

show_badge()

while True:
    pybadger.auto_dim_display(delay=10) # Remove or comment out this line if you have the PyBadge LC
    if pybadger.button.a:
        board.DISPLAY.brightness = 1
        show_wildcat()
    elif pybadger.button.b:
        board.DISPLAY.brightness = 1
        pybadger.show_qr_code(data="https://github.com/estranged42/pybadge-reinvent-2019")
    elif pybadger.button.start:
        board.DISPLAY.brightness = 1
        show_badge()
    elif pybadger.button.right:
        board.DISPLAY.brightness = 1
        aws_announcements()
    elif pybadger.button.up:
        update_aws_count(1)
        aws_announcements()
    elif pybadger.button.down:
        update_aws_count(-1)
        aws_announcements()
