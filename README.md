<img src="icon.png" align="right" />

# Molecule Dynamic Studio [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/wen123war/Elite_Presentation.git/HEAD)

## Schmelzprozess
In dieser Simulation wird eine Box an Atomen (Aluminium oder Kupfer) aufgeschmolzen. Man beobachtet wie die Atome unter dem Einfluss der thermischen Energie schwingen und der Kristall seine strukturierte Form verliert. In diesem Beispiel wurden, wie bei MD-Simulationen üblich, keine periodischen Randbedingungen festgelegt. 

Periodische Randbedingungen heißt, dass die Box mit den Atomen in jede Raumrichtung unendlich weitergeführt wird. Als ob es sich um einen unendlich großen Kristall handelt. Wenn diese aufgehoben werden, handelt es sich "wirklich" nur um die Atome die man in der Box sieht. Dies ermöglicht den Schemlzübergang schön zu erkennen. 

Wie oben erwähnt, verliert der Kristall seine periodische und geordnete Struktur während des Schmelzvorganges. In der Schmelze brechen die starken Bindungen und die Atome ordnen sich statistisch an. Die Atome können aber noch als eine Einheit betrachten, da sie durch ihre räumliche Nähe weiterhin miteinander wechselwirken. Das System strebt immer Richtung der thermodynamisch stabilsten Konfiguration. Diese wird hier durch die Oberflächenspannung bestimmt. Es bildet sich eine Kugel, wie man es von Regentropfen kennt. Dies geschieht, weil die Kugel das kleinste Oberflächen zu Volumen Verhältnis aufweist. 

## Phasentransformation
Bei der zweiten Simulation wird ein Phasenübergang bei Titan simuliert. Bei Raumtemperatur liegt Titan in der hexagonal-dicht-gepackten (hcp) Struktur vor. Bei ca. 1200 K wandelt Titan in eine kubisch-raumzentrierte (bcc) Struktur um. Diese Umwandlung liegt natürlich unter dem Schmelzpunkt von Titan (1941 K), denn es handelt sich immer noch um einen geordneten Kristall nach dieser Phasenumwandlung. 

## Bedienung 
Die Bedienung der zwei Simulationen läuft gleich ab. Zuerst müssen die notwendigen Packages importiert und die Funktionen definiert werden. Der Nutzer kann dann über ein input-Fenster ein paar Simulationswerte verändern. 

![alt text](image1.png "Input 1")
![alt text](image2.png "Input 2")


Abbildungen 1 und 2 zeigen das input-Fenster. Hier für den Schmelzprozess. Zuerst wird das Element und die Größe der Box ausgewählt, dann der Gitterparameter (in realistischen Grenzen). Die Simulationsbox wird mit Preview gezeigt. Es ist wichtig auf Preview zu klicken, bevor die Simulation gestartet wird. Danach kann Start und Endtemperatur eingestellt und ein Seed festgelegt werden. Für den Seed kann eine beliebige Zahl eingesetzt werden, er dient nur als Anfang für einen Pseudozufallszahlengenerator. 


