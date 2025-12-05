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
 "13-dec 16:01",
 "20-dec 16:03",
 "27-dec 16:08",
 "03-jan 16:15",
 "10-jan 16:25",
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
logger.addHandler(rotating_handler)

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
lampen_status = {"normaal": False, "shabbat": False, "warmhoudplaat": False}
timer = {"normaal": 0, "shabbat": 0,}

# MQTT callback functies
def on_message(client, userdata, message):
    global light_value
    light_value = int(message.payload.decode())
    print(f"Ontvangen lichtwaarde: {light_value}")

def on_connect(client, userdata, flags, rc):
    print(f"Verbonden met de broker! Code: {rc}")
    client.subscribe(MQTT_TOPIC_LIGHT)

# Bereken normale tijdvakken
def bereken_tijdvakken():
    begin_terne = datetime.now().date().replace(month=1, day=1)
    eind_terne = datetime.now().date().replace(month=3, day=20)
    
    if begin_terne <= datetime.now().date() <= eind_terne:
        huidige_datum = datetime.now(tz_netherlands) #+ timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk
    else:
        huidige_datum = datetime.now(tz_netherlands) + timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk
    
    today_ss = sun.get_sunset_time(huidige_datum)
    begin_tijd = today_ss.astimezone(tz_netherlands) - timedelta(hours=1)
    eind_tijd = today_ss.astimezone(tz_netherlands).replace(hour=22, minute=30, second=0)
    return begin_tijd, eind_tijd

# Bereken Shabbat tijdvakken
def shabbat_bereken_tijdvakken():
    current_date = datetime.now(tz_netherlands).date()
    for x in shabbat_dict:
        print("\n",x,"\n")
        parsed_date = datetime.strptime(x, "%d-%b %H:%M")
        parsed_date = parsed_date.replace(year=datetime.now().year)
        parsed_date = tz_netherlands.localize(parsed_date)
        print(parsed_date)
        if parsed_date.date() == current_date:
            shabbat_begin_tijd = parsed_date
            shabbat_eind_tijd = parsed_date + timedelta(hours=1, minutes=30)
            return shabbat_begin_tijd, shabbat_eind_tijd
        # placeholder tijd retourneren die nooit op shabbat valt, want het is toch geen shabbat
    placeholder = tz_netherlands.localize(datetime(2025, 12, 31, 0, 0, 0))
    return placeholder, placeholder

# Bereken warmhoudplaat tijdvakken
def warmhoudplaat_bereken_tijdvakken():
    warmhoudplaat_begin_tijd = datetime.now(tz_netherlands).replace(hour=12, minute=0, second=0)
    warmhoudplaat_eind_tijd = datetime.now(tz_netherlands).replace(hour=13, minute=0, second=0)
    return warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd

# Beheer lampen
def beheer_lamp(lamp, begin_tijd, eind_tijd, topicList, licht_drempel=None, dag_restrictie=None, seizoensperiode=None):
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
                timer[lamp] += 1
                print(f"{lamp.capitalize()}-timer: {timer[lamp]} seconden")
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
begin_tijd, eind_tijd = bereken_tijdvakken()
shabbat_begin_tijd, shabbat_eind_tijd = shabbat_bereken_tijdvakken()
warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd = warmhoudplaat_bereken_tijdvakken()
while True:
    huidige_tijd = datetime.now(tz_netherlands)

    # Update tijdvakken bij een nieuwe dag
    if huidige_tijd.date() != begin_tijd.date():
        logger.debug("Nieuwe dag aangebroken, bereken nieuwe tijdvakken!")
        begin_tijd, eind_tijd = bereken_tijdvakken()
        shabbat_begin_tijd, shabbat_eind_tijd = shabbat_bereken_tijdvakken()
        warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd = warmhoudplaat_bereken_tijdvakken()

    print(f"Huidige tijd: {huidige_tijd}")
    print(f"Normaal-tijdvak: {begin_tijd} - {eind_tijd}")
    print(f"Shabbat-tijdvak: {shabbat_begin_tijd} - {shabbat_eind_tijd}")
    print(f"Warmhoudplaat-tijdvak: {warmhoudplaat_begin_tijd} - {warmhoudplaat_eind_tijd}")
    print(f"\n{lampen_status}\n")

    # Beheer lampen
    beheer_lamp("normaal", begin_tijd, eind_tijd, normaalTopicList, 50)
    beheer_lamp("shabbat", shabbat_begin_tijd, shabbat_eind_tijd, shabbatTopicList, 100, dag_restrictie=4)
    beheer_lamp("warmhoudplaat", warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd, warmhoudplaatTopicList, dag_restrictie=5, seizoensperiode=("21-03-2024", "21-09-2024"))

    time.sleep(1)
