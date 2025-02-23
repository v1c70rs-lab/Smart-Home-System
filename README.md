# automatisering-binnenverlichting
project: automatisering binnenverlichting

In dit project leer ik je hoe je de binnenverlichting van je huis kunt automatiseren met behulp van een lichtsensor en tijdvakken.

**Waarom dit project?**
Bij mij thuis was er behoefte aan om de binnenverlichting automatisch aan en uit te zetten op basis van het gemeten daglicht.

Voordat ik dit heb gedaan, gebruikte ik Sonoff S60 smartplugs met de eWelink app. Hiermee kon ik op basis van de horizonsovergangen de tijdstippen waarop de verlichting aan en uit moest gaan dynamisch creeren. Er werd dus geen daglicht gemeten. 
Het enige punt is dat deze setup geen rekening houdt met het daadwerkelijke licht niveau binnenshuis. Het zou zomaar kunnen zijn dat de zon nog niet onder is, maar het wel donker is door de wolken. De verlichting die is ingesteld op zonsondergang gaat dan niet aan, maar binnen is het wel donker.

**Hoe werkt dit project?**
Door gebruik te maken van een lichtsensor kan je op basis van een gemeten licht niveau lampen aan en uit zetten. Dit overkomt het probleem van wanneer je alleen maar kijkt naar de horizonsovergangen/tijdstip van de dag.

Er is een lichtsensor die het daglicht meet in Lux. Lux is de hoeveelheid licht uitgestraald door een lichtbron. Deze lichtsensor zit vast aan een ESP8266-01 die het gemeten lightlevel verwerkt en doorstuurt naar een broker.

De boker draait in mijn geval op een Raspberry Pi, aangezien dit computerje dag in dag uit aan staat wil ik dat het zo min mogelijk stroom verbruikt. De Pi ontvangt dit licht niveau en maakt een besluit op basis van een drempelwaarde, tijdvak en andere contities of er een aan/uit signaal wordt verstuurd naar de smartplugs.

De smartplugs ontvangen dit signaal en gaan aan of uit waardoor het apparaat dat verbonden is aan deze pluggen ook aan of uit gaan.

Het verzenden van het licht niveau en de aan/uit commando's gebeurt met een lichtgewicht protocol dat hier voor gemaakt is genaamd MQTT.

Voor het verwerken van de ontvangen lichtwaarde op de Pi schrijven we een script in Python. Dit script is netzoals de lichtsensor en smartplugs een MQTT client van de MQTT broker die op de Pi draait.

Ook de code voor de ESP8266-01 waar de lichtsensor aan verbonden is, is zelf geschreven in de Arduino IDE.
