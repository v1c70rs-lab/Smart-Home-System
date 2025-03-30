import paho.mqtt.client as mqtt
import time
from suntime import Sun
from datetime import datetime, date, timedelta
import pytz

# MQTT instellingen
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_LIGHT = "home/lightsensor"
MQTT_TOPIC_SMARTPLUG1 = "cmnd/home/smartplug1/Power"
MQTT_TOPIC_SMARTPLUG2 = "cmnd/home/smartplug2/Power"
MQTT_TOPIC_SMARTPLUG3 = "cmnd/home/smartplug3/Power"
MQTT_TOPIC_SMARTPLUG4 = "cmnd/home/smartplug4/Power"
MQTT_TOPIC_SMARTPLUG5 = "cmnd/test/SetChannel"

# Lijst met MQTT-topics
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
    begin_terne = datetime.now().date().replace(month=1, day=1)
    eind_terne = datetime.now().date().replace(month=3, day=20)
    
    if begin_terne <= datetime.now().date() <= eind_terne:
        huidige_datum = datetime.now(tz_netherlands) #+ timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk
    else:
        huidige_datum = datetime.now(tz_netherlands) + timedelta(days=1) # bug die er voor zorgt dat get_sunset_time de dag ervoor pakt i.p.v. de huidige dag, vandaar dat we een dag optellen bij de huidige_datum. Bug gebeurt alleen na ongeveer 21 maart. Dus zomer- wintertijd gerelateerd waarschijnlijk

    today_ss = sun.get_sunset_time(huidige_datum)
    shabbat_begin_tijd = today_ss.astimezone(tz_netherlands) - timedelta(minutes=18)
    shabbat_eind_tijd = today_ss.astimezone(tz_netherlands) + timedelta(hours=2)
    return shabbat_begin_tijd, shabbat_eind_tijd

# Tijdvaken warmhoudplaat
warmhoudplaat_begin_tijd = datetime.now(tz_netherlands).replace(hour=12, minute=0, second=0)
warmhoudplaat_eind_tijd = datetime.now(tz_netherlands).replace(hour=13, minute=0, second=0)

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
            print(f"{lamp.capitalize()} wordt niet ingeschakeld buiten de seizoensperiode ({start_datum1}, {eind_datum1}).")
            return

    # Als dag regstrictie is meegegeven, check dan welke dag het is
    if dag_restrictie and huidige_tijd.weekday() != dag_restrictie:
        print(f"\n{lamp.capitalize()} gaat niet aan, niet juiste dag!\n")
        if lampen_status[lamp]:
            print(f"\n{lamp.capitalize()} lamp gaat uit (niet de juiste dag)!\n")
            for topic in topicList:
                if topic != MQTT_TOPIC_SMARTPLUG5:
                    client.publish(topic, "0")
                else:
                    client.publish(topic, "2 0")
            lampen_status[lamp] = False                    
        return

    if begin_tijd <= huidige_tijd <= eind_tijd:
        print(f"{lamp} zit in begin_tijd huidige_tijd eind_tijd check")
        if not lampen_status[lamp] and licht_drempel:
            if light_value < licht_drempel:
                timer[lamp] += 1
                print(f"{lamp.capitalize()} timer: {timer[lamp]} seconden")
                if timer[lamp] >= 60:
                    print(f"\n{lamp.capitalize()} lamp gaat aan!\n")
                    for topic in topicList:
                        if topic != MQTT_TOPIC_SMARTPLUG5:
                            client.publish(topic, "1")
                        else:
                            client.publish(topic, "2 1")
                    lampen_status[lamp] = True
            else:
                timer[lamp] = 0  # Reset timer als het niet donker genoeg is
        # Lamp blijft aan tijdens het tijdvak
        elif not lampen_status[lamp] and not licht_drempel:
            print(f"{lamp.capitalize()} gaat aan!\n")
            for topic in topicList:
                if topic != MQTT_TOPIC_SMARTPLUG5:
                    client.publish(topic, "1")
                else:
                    client.publish(topic, "2 1")
            lampen_status[lamp] = True
    else:
        print(f"{lamp} zit niet in het tijdvak")
        if lampen_status[lamp]:
            print(f"\n{lamp.capitalize()} lamp gaat uit (einde tijdvak)!\n")
            for topic in topicList:
                if topic != MQTT_TOPIC_SMARTPLUG5:
                    client.publish(topic, "0")
                else:
                    client.publish(topic, "2 0")
            lampen_status[lamp] = False
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

while True:
    huidige_tijd = datetime.now(tz_netherlands)

    # Update tijdvakken bij een nieuwe dag
    if huidige_tijd.date() != begin_tijd.date():
        print("\nik ben tijdvakken opnieuw aan het berekenen.\n")
        begin_tijd, eind_tijd = bereken_tijdvakken()
        shabbat_begin_tijd, shabbat_eind_tijd = shabbat_bereken_tijdvakken()

    print(f"Huidige tijd: {huidige_tijd}")
    print(f"Normale tijdvakken: {begin_tijd} - {eind_tijd}")
    print(f"Shabbat tijdvakken: {shabbat_begin_tijd} - {shabbat_eind_tijd}")

    # Beheer lampen
    beheer_lamp("normaal", begin_tijd, eind_tijd, normaalTopicList, 50)
    beheer_lamp("shabbat", shabbat_begin_tijd, shabbat_eind_tijd, shabbatTopicList, 100, dag_restrictie=4)
    beheer_lamp("warmhoudplaat", warmhoudplaat_begin_tijd, warmhoudplaat_eind_tijd, warmhoudplaatTopicList, dag_restrictie=5, seizoensperiode=("21-03-2024", "21-09-2024"))

    time.sleep(1)
