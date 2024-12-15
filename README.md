# CreepDetector-KismetDB

KismetDB compatible [CreepDetector](https://github.com/skickar/CreepDetector) remake.

## Installation

### Python Version

* Python 3.13

### Python Packages

- Haversine
- Pandas
- Folium
- kismetdb
  
### kismetdb special note

Due to changes in the KismetDB file schema, the python-kismet-db package was updated on Github, but not yet on PyPi.

Until the PyPi version is more recent than 2021.6.1, the `requirements.txt` downloads and installs the [Github version](https://github.com/kismetwireless/python-kismet-db).

### Using pip

1) Recommendation: Create a new virtual environment using `python -m venv .venv` inside the project's folder. Activate using your platform's script under `.venv/Scripts/` (e.g. activate.bat for Windows, activate for Linux).

2) Install required packages: `pip install -r requirements.txt`

## Credits

Based on the work of [skickar](https://github.com/skickar) and [Alex Lynd](https://github.com/AlexLynd), check out the original [CreepDetector](https://github.com/skickar/CreepDetector)!
