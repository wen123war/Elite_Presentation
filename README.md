<img src="icon.png" align="right" />

# Molecular Dynamics Studio [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/wen123war/Elite_Presentation.git/HEAD)

## Schmelzprozess
In dieser Simulation wird ein Nanowürfel aus Atomen (Aluminium oder Kupfer) aufgeschmolzen. Man beobachtet wie die Atome unter dem Einfluss der thermischen Energie schwingen und der Nanowürfel seine strukturierte Form verliert. In diesem Beispiel wurden keine periodischen Randbedingungen festgelegt, d.h. um den Würfel ist Vakuum. Dies ermöglicht den Schemlzübergang schön zu erkennen; erst an den Ecken, dann den Kanten und schliesslich in die Mitte hinein. In der Schmelze brechen die starken Bindungen und die Atome ordnen sich deutlich ungeordneter als in der feste Phase an. Die Atome können aber noch als eine Einheit betrachtet werden, da sie durch ihre räumliche Nähe weiterhin miteinander wechselwirken (sich anziehen). Das System strebt insgesamt in Richtung der thermodynamisch stabilsten Konfiguration. Diese wird hier durch die Oberflächenspannung bestimmt. Es bildet sich daher eine Kugel, wie man es vom Regentropfen her kennt. Dies geschieht, weil die Kugel das kleinste Oberflächen zu Volumen Verhältnis aufweist. 

## Transformation einer festen in eine feste Phase
Bei der zweiten Simulation wird ein fest-fest Phasenübergang mit Titan simuliert. Bei Raumtemperatur liegt Titan in der hexagonal-dicht-gepackten (hcp) Struktur vor. Bei 1166 K wandelt sich Titan in eine kubisch-raumzentrierte (bcc) Struktur um. Diese Umwandlung liegt unter dem Schmelzpunkt von Titan (1941 K), und es handelt sich immer noch um einen geordneten Kristall nach dieser Phasenumwandlung. Bei dieser Simulation sind periodische Randbedingungen festgelegt worden. Periodische Randbedingungen heißt, dass die Box mit den Atomen in jede Raumrichtung unendlich weitergeführt wird. Als ob es sich um einen unendlich großen Kristall handelt. 

## Bedienung 
Die Bedienung der beiden Simulationen läuft gleich ab. Zuerst müssen die notwendigen Packages importiert und die Funktionen definiert werden. Der Nutzer kann dann über ein Input-Fenster verschiedene Simulationswerte verändern. Zuerst wird das Element und die Größe der Box ausgewählt, dann der Gitterparameter (in realistischen Grenzen). Die Simulationsbox wird mit Preview gezeigt. Danach kann Start und Endtemperatur eingestellt und ein Seed festgelegt werden. Für den Seed kann eine beliebige Zahl eingesetzt werden, er dient nur als Anfang für einen Pseudozufallszahlengenerator. 


