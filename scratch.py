import time
from datetime import datetime
import pytz
import paho.mqtt.client as mqtt
import logging

shabbat_dict = [
    "02-jan 16:21",
    "09-jan 16:35",
    "16-jan 16:48",
    "23-jan 17:01",
    "30-jan 17:13",
    "06-feb 17:25",
    "13-feb 17:36",
    "20-feb 17:47",
    "27-feb 17:58",
    "06-mar 18:09",
    "13-mar 18:20",
    "20-mar 18:31",
    "27-mar 18:42",
    "03-apr 18:52",
    "10-apr 19:01",
    "17-apr 19:10",
    "24-apr 19:18",
    "01-may 19:26",
    "08-may 19:34",
    "15-may 19:42",
    "22-may 19:50",
    "29-may 19:57",
    "05-jun 20:04",
    "12-jun 20:10",
    "19-jun 20:15",
    "26-jun 20:19",
    "03-jul 20:21",
    "10-jul 20:21",
    "17-jul 20:18",
    "24-jul 20:11",
    "31-jul 20:01",
    "07-aug 19:49",
    "14-aug 19:36",
    "21-aug 19:23",
    "28-aug 19:08",
    "04-sep 18:52",
    "11-sep 18:36",
    "18-sep 18:20",
    "25-sep 18:03",
    "02-oct 17:47",
    "09-oct 17:31",
    "16-oct 17:14",
    "23-oct 16:58",
    "30-oct 16:42",
    "06-nov 16:27",
    "13-nov 16:14",
    "20-nov 16:03",
    "27-nov 15:55",
    "04-dec 15:51",
    "11-dec 15:51",
    "18-dec 15:55",
    "25-dec 16:02"
]

# logger instellingen
logger = logging.getLogger()
logger.setLevel("DEBUG")
formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setLevel("DEBUG")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

MQTT_BROKER = "192.168.2.11"
MQTT_PORT = 1883
MQTT_TOPIC = "homeassistant"
MQTT_USERNAME = "mqtt-user"
MQTT_PASSWORD = "mqtt-user"

# MQTT callback functies
def on_connect(client, userdata, flags, rc):
    logger.info(f"Verbonden met de broker! Code: {rc}")

# MQTT client instellen
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

tz_netherlands = pytz.timezone("Europe/Amsterdam")

currentDateTime = datetime.now(tz_netherlands).replace(second=0, microsecond=0)
# currentDateTime = datetime(2026, 10, 16, 16, 2)

def shabbat_check():
    for entry in shabbat_dict:
        parsedDateTime = datetime.strptime(entry, "%d-%b %H:%M").replace(year=currentDateTime.year)
        parsedDateTime = tz_netherlands.localize(parsedDateTime)

        if parsedDateTime.date() == currentDateTime.date():
            client.publish(MQTT_TOPIC, f"{parsedDateTime.time()}", qos=2)

shabbat_check()

while True:
    if currentDateTime.date() != datetime.now().date():
        currentDateTime = datetime.now(tz_netherlands).replace(second=0, microsecond=0)
        shabbat_check()

    time.sleep(1)
