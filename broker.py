import paho.mqtt.client as mqtt
import time
from suntime import Sun
from datetime import datetime, date, timedelta
from logging.handlers import RotatingFileHandler
import pytz
import logging
from astral.sun import sun
from pysolar.solar import get_altitude
from astral import LocationInfo

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
console_handler.setLevel("INFO")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

rotating_handler = RotatingFileHandler(
    "apps.log",
    mode="a",
    encoding="utf-8",
    maxBytes=100000,
    backupCount=3)
rotating_handler.setLevel("DEBUG")
rotating_handler.setFormatter(formatter)
#logger.addHandler(rotating_handler)

# MQTT instellingen
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_LIGHT = "home/lightsensor"
MQTT_TOPIC_SMARTPLUG1 = "cmnd/home/smartplug1/Power"
MQTT_TOPIC_SMARTPLUG2 = "cmnd/home/smartplug2/Power"
MQTT_TOPIC_SMARTPLUG3 = "cmnd/home/smartplug3/Power"
MQTT_TOPIC_SMARTPLUG4 = "cmnd/home/smartplug4/Power"
MQTT_TOPIC_SMARTPLUG5 = "cmnd/test/SetChannel"

# Lijsten met MQTT-topics
normaalTopicList = [MQTT_TOPIC_SMARTPLUG1, MQTT_TOPIC_SMARTPLUG2, MQTT_TOPIC_SMARTPLUG3, MQTT_TOPIC_SMARTPLUG4]
shabbatTopicList = [MQTT_TOPIC_SMARTPLUG5]
warmhoudplaatTopicList = [MQTT_TOPIC_SMARTPLUG3]

# Zon- en tijdzone-instellingen
latitude = 52.3676
longtitude = 4.9041
tz_netherlands = pytz.timezone("Europe/Amsterdam")
sun = Sun(latitude, longtitude)

# Globale variabelen
light_value = 150
lampen_status = {"normaal": False, "shabbat": False, "warmhoudplaat": False, "warmhoudplaat2": False}
timer = {"normaal": 0, "shabbat": 0,}

# MQTT callback functies
def on_message(client, userdata, message):
    global light_value
    light_value = int(message.payload.decode())
    logger.info(f"Ontvangen lichtwaarde: {light_value}")

def on_connect(client, userdata, flags, rc):
    logger.info(f"Verbonden met de broker! Code: {rc}")
    client.subscribe(MQTT_TOPIC_LIGHT)

# Bereken normale tijdvakken
def calculate_time_window():
    current_date_time = datetime.now()
    current_date_time_tz = tz_netherlands.localize(current_date_time)
    start_date = current_date_time.date().replace(month=1, day=1)
    end_date = current_date_time.date().replace(month=3, day=20)
    
    if start_date <= current_date_time.date() <= end_date:
        current_date = current_date_time_tz #+ timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk
    else:
        current_date = current_date_time_tz + timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk
    
    today_ss = sun.get_sunset_time(current_date)
    start_time = today_ss.astimezone(tz_netherlands) - timedelta(hours=1)
    end_time = tz_netherlands.localize(current_date_time).replace(hour=22, minute=30, second=0)
    return start_time, end_time

# Bereken Shabbat tijdvakken
def shabbat_calculate_time_window():
    current_date_tz = datetime.now(tz_netherlands).date()
    for x in shabbat_dict:
        parsed_date = datetime.strptime(x, "%d-%b %H:%M")
        parsed_date = parsed_date.replace(year=datetime.now().year)
        parsed_date = tz_netherlands.localize(parsed_date)
        if parsed_date.date() == current_date_tz:
            shabbat_start_time = parsed_date
            shabbat_end_time = parsed_date + timedelta(hours=1, minutes=30)
            return shabbat_start_time, shabbat_end_time
        # placeholder tijd retourneren want het is toch geen shabbat
    placeholder = tz_netherlands.localize(datetime(2024, 11, 30, 0, 0, 0))
    return placeholder, placeholder

# Bereken warmhoudplaat tijdvakken
def warmhoudplaat_calculate_time_window():
    current_date_time_tz = datetime.now(tz_netherlands)
    warmhoudplaat_start_time = current_date_time_tz.replace(hour=12, minute=0, second=0)
    warmhoudplaat_end_time = current_date_time_tz.replace(hour=13, minute=0, second=0)
    return warmhoudplaat_start_time, warmhoudplaat_end_time

# Beheer lampen
def manage_devices(lamp, begin_tijd, eind_tijd, topicList, licht_drempel=None, dag_restrictie=None, seizoensperiode=None):
    huidige_tijd = datetime.now(tz_netherlands)
    global lampen_status, timer

    # Als seizoensperiode is meegegeven, check dan of het binnen het seizoen valt
    # Controleer seizoensperiode
    if seizoensperiode:
        start_datum1 = datetime.strptime(seizoensperiode[0], "%d-%m-%Y").replace(year=huidige_tijd.year)
        start_datum = tz_netherlands.localize(start_datum1)

        eind_datum1 = datetime.strptime(seizoensperiode[1], "%d-%m-%Y").replace(year=huidige_tijd.year)
        eind_datum = tz_netherlands.localize(eind_datum1)

        if start_datum > eind_datum:
            # Indien de periode over de jaarwisseling gaat (bijv. okt - mrt)
            eind_datum = eind_datum.replace(year=huidige_tijd.year + 1) if huidige_tijd < start_datum else eind_datum
        
        if not (start_datum <= huidige_tijd <= eind_datum): # Als de start_datum niet kleiner is dan huidige tijd en ook niet kleiner is dan eind_datum, dan zit de huidige_tijd niet binnen het seizoensvak
            logger.debug(f"{lamp.capitalize()} wordt niet ingeschakeld buiten de seizoensperiode ({start_datum1}, {eind_datum1}).")
            return
        logger.debug(f"Juiste seizoensperiode voor {lamp}")

    # Als dag regstrictie is meegegeven, check dan welke dag het is
    if dag_restrictie:
        if dag_restrictie and huidige_tijd.weekday() != dag_restrictie:
            logger.debug(f"{lamp.capitalize()} gaat niet aan, niet juiste dag!")
            if lampen_status[lamp]:
                logger.debug(f"{lamp.capitalize()} lamp gaat uit (niet de juiste dag)!")
                for topic in topicList:
                    if topic != MQTT_TOPIC_SMARTPLUG5:
                        client.publish(topic, "0")
                        logger.debug(f"{topic}, uit")
                    else:
                        client.publish(topic, "2 0")
                        logger.debug(f"{topic}, uit")
                lampen_status[lamp] = False
                logger.info(f"{lamp.capitalize()} uit")
            return
        logger.debug(f"Juiste dag voor {lamp}")

    if begin_tijd <= huidige_tijd <= eind_tijd:
        logger.debug(f"Tijd valt binnen {lamp}-tijdvak")
        if not lampen_status[lamp] and licht_drempel:
            logger.debug(f"{lamp.capitalize()} is nog niet aan en licht_drempel is meegegeven")
            if light_value < licht_drempel:
                timer[lamp] += 10
                logger.debug(f"{lamp.capitalize()}-timer loopt: {timer[lamp]} seconden")
                if timer[lamp] >= 60:
                    for topic in topicList:
                        if topic != MQTT_TOPIC_SMARTPLUG5:
                            client.publish(topic, "1")
                            logger.debug(f"{topic}, aan")
                        else:
                            client.publish(topic, "2 1")
                            logger.debug(f"{topic}, aan")
                    lampen_status[lamp] = True
                    logger.info(f"{lamp.capitalize()}, aan")
            else:
                timer[lamp] = 0  # Reset timer als het niet donker genoeg is
                logger.debug(f"Timer reset naar 0, lichtwaarde({light_value}) niet onder drempelwaarde({licht_drempel})")
        # Lamp blijft aan tijdens het tijdvak
        elif not lampen_status[lamp] and not licht_drempel:
            logger.debug(f"{lamp.capitalize()} is nog niet aan en licht_drempel is niet meegegeven")
            for topic in topicList:
                if topic != MQTT_TOPIC_SMARTPLUG5:
                    client.publish(topic, "1")
                    logger.debug(f"{topic}, aan")
                else:
                    client.publish(topic, "2 1")
                    logger.debug(f"{topic}, aan")
            lampen_status[lamp] = True
            logger.info(f"{lamp.capitalize()} aan")
    else:
        logger.debug(f"Tijd valt niet binnen {lamp}-tijdvak")
        if lampen_status[lamp]:
            logger.debug(f"{lamp.capitalize()} gaat uit (einde tijdvak)")
            for topic in topicList:
                if topic != MQTT_TOPIC_SMARTPLUG5:
                    client.publish(topic, "0")
                    logger.debug(f"{topic}, uit")
                else:
                    client.publish(topic, "2 0")
                    logger.debug(f"{topic}, uit")
            lampen_status[lamp] = False
            logger.info(f"{lamp.capitalize()} uit")
        timer[lamp] = 0  # Reset timer buiten tijdvak

# MQTT client instellen
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Hoofdprogramma
begin_tijd, eind_tijd = calculate_time_window()
shabbat_begin_tijd, shabbat_eind_tijd = shabbat_calculate_time_window()
warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd = warmhoudplaat_calculate_time_window()
while True:
    huidige_tijd = datetime.now(tz_netherlands)

    # Update tijdvakken bij een nieuwe dag
    if huidige_tijd.date() != begin_tijd.date():
        logger.debug("Nieuwe dag aangebroken, bereken nieuwe tijdvakken!")
        begin_tijd, eind_tijd = calculate_time_window()
        shabbat_begin_tijd, shabbat_eind_tijd = shabbat_calculate_time_window()
        warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd = warmhoudplaat_calculate_time_window()

    logger.info(f"Huidige tijd: {huidige_tijd}")
    logger.info(f"Normaal-tijdvak: {begin_tijd} - {eind_tijd}")
    logger.info(f"Shabbat-tijdvak: {shabbat_begin_tijd} - {shabbat_eind_tijd}")
    logger.info(f"Warmhoudplaat-tijdvak: {warmhoudplaat_begin_tijd} - {warmhoudplaat_eind_tijd}")
    logger.info(f"{lampen_status}")

    # Beheer lampen
    manage_devices("normaal", begin_tijd, eind_tijd, normaalTopicList, 45)
    manage_devices("shabbat", shabbat_begin_tijd, shabbat_eind_tijd, shabbatTopicList, 100, dag_restrictie=4)
    manage_devices("warmhoudplaat2", shabbat_begin_tijd, shabbat_begin_tijd + timedelta(hours=1), warmhoudplaatTopicList, dag_restrictie=4)
    manage_devices("warmhoudplaat", warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd, warmhoudplaatTopicList, dag_restrictie=5)

    time.sleep(10)
