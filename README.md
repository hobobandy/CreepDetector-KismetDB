# CreepDetector-KismetDB

KismetDB compatible CreepDetector remake.

## Requirements

### Python Packages

- Haversine
- Pandas
- Folium
- kismetdb ([git version](https://github.com/kismetwireless/python-kismet-db), see below)

### kismetdb special note

Due to changes in the KismetDB file schema, the python-kismet-db package was updated on Git, but not yet on PyPi.

Until the PyPi version is more recent than 2021.6.1, you'll have to manually install the Git version. Don't worry, it's simple!

- clone the package to an accessible folder: ```git clone https://github.com/kismetwireless/python-kismet-db.git```
- from this script's folder, type: ```pipenv install ../python-kismet-db```
