# Streaming Telemetry: Real-time Network Monitoring met Python

> Live demo van PyUtrecht Meetup - Van SNMP naar gNMI/gRPC streaming telemetry

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyGNMI](https://img.shields.io/badge/pygnmi-0.8.15-green.svg)](https://github.com/akarneliuk/pygnmi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Containerlab](https://img.shields.io/badge/Containerlab-latest-orange.svg)](https://containerlab.dev)

## 📋 Overzicht

Deze repository bevat een complete, werkende demonstratie van **streaming telemetry** voor moderne netwerk monitoring. De demo laat zien hoe je van traditionele SNMP polling naar real-time gRPC/gNMI streaming kunt overstappen.


### Netwerk Topologie

<img src=docs/network-diagram.svg />

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Demo Scenario                          │
└─────────────────────────────────────────────────────────────┘

  1. CAPABILITIES Query
     Python ──────GET────────► Spine1
     Python ◄────Response──── Spine1
     
  2. Traditional GET (SNMP-style)
     Python ──────GET────────► Spine1
     Python ◄────Snapshot──── Spine1
     (One-time poll - must repeat every N seconds)
     
  3. SAMPLE Mode Streaming
     Python ──────SUBSCRIBE──► Spine1
            ◄────Update 1────┤ (t=0s)
            ◄────Update 2────┤ (t=5s)
            ◄────Update 3────┤ (t=10s)
            ◄────Update N────┘ (continuous...)
     
  4. ON_CHANGE Mode Streaming  
     Python ──────SUBSCRIBE──► Spine1
            ◄────Update──────┤ (only when change!)
            (silence)         
            ◄────Update──────┘ (interface down!)
```

## Quick Start

### Vereisten

- **Hardware**: 8GB RAM minimum, 16GB aanbevolen
- **Software**:
  - Docker & Docker Compose
  - Python 3.8 of hoger
  - Git
- **Netwerk**: Arista cEOS image (gratis download van arista.com)

### Installatie (5 minuten)

```bash
# 1. Clone repository
git clone https://github.com/mstoof/pyutrecht-telemetry-demo.git
cd pyutrecht-telemetry-demo

# 2. Installeer Containerlab
bash -c "$(curl -sL https://get.containerlab.dev)"

# 3. Importeer Arista cEOS image (download eerst van arista.com)
docker import cEOS-lab-4.32.0F.tar ceos:latest

# 4. Maak Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Installeer dependencies
pip install -r requirements.txt

# 6. Maak configuratie bestanden
./create_configs.sh

# 7. Deploy het netwerk
sudo containerlab deploy -t topology.yml

# 8. Wacht 60 seconden voor boot...
sleep 60

# 9. Run de demo! 🎉
python3 streaming_demo.py
```

## 📁 Repository Structuur

```
pyutrecht-telemetry-demo/
├── README.md                    # Dit bestand
├── topology.yml                 # Containerlab netwerk definitie
├── streaming_demo.py            # Hoofd demo script
├── test_gnmi.py                # Test script voor gNMI connectie
├── requirements.txt             # Python dependencies
├── create_configs.sh           # Script om configs te genereren
├── verify_deployment.sh        # Deployment verificatie
├── configs/                    # Switch configuraties
│   ├── spine1.cfg
│   ├── spine2.cfg
│   ├── leaf1.cfg
│   └── leaf2.cfg
├── docs/                       # Extra documentatie
│   ├── PRESENTATION.md        # Volledige presentatie script
│   └── TROUBLESHOOTING.md     # Troubleshooting gids
└── slides/                     # Presentatie slides (optional)
```

## 🎬 Demo Scenario's

De demo bevat 5 interactieve scenario's:

### 1️⃣ Device Capabilities
Ontdek welke gNMI features en YANG models de switch ondersteunt.

### 2️⃣ Traditional GET Request
Vergelijkbaar met SNMP - één keer data ophalen (snapshot).

### 3️⃣ SAMPLE Mode Streaming
Time-based streaming: updates elke N seconden, continu.

### 4️⃣ ON_CHANGE Mode Streaming  
Event-driven streaming: alleen updates bij veranderingen.

### 5️⃣ Vergelijking
Side-by-side overzicht van SNMP vs Streaming Telemetry.


## 🔧 Configuratie

### IP Adres Schema

| Device       | Management IP  | gNMI Port | BGP AS |
|-------------|---------------|-----------|--------|
| spine1      | 172.20.20.11  | 6030      | 65000  |
| spine2      | 172.20.20.12  | 6030      | 65000  |
| leaf1       | 172.20.20.21  | 6030      | 65001  |
| leaf2       | 172.20.20.22  | 6030      | 65002  |
| traffic-gen | 172.20.20.100 | -         | -      |
| host1       | 172.20.20.101 | -         | -      |

**Credentials**: `admin` / `admin` (alle devices)

### Data Plane Subnets

- Spine-Leaf uplinks: `10.0.1.0/31`, `10.0.2.0/31`
- Leaf1 access: `10.1.1.0/24`
- Leaf2 access: `10.1.2.0/24`




## 🎤 Presentatie Informatie

Deze demo is ontwikkeld voor **PyUtrecht Meetup**.

**Talk**: "Streaming Telemetry: Real-time Network Monitoring met Python"  
**Duur**: 25 minuten (20 min talk + 5 min Q&A)  
**Level**: Intermediate  
**Tags**: `network-automation`, `telemetry`, `gnmi`, `grpc`, `devops`


## Bijdragen

Contributions zijn welkom! Als je een bug vindt of verbetering hebt:

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/awesome-feature`)
3. Commit je changes (`git commit -m 'Add awesome feature'`)
4. Push naar de branch (`git push origin feature/awesome-feature`)
5. Open een Pull Request

## 📝 License

Dit project is gelicenseerd onder de MIT License - zie [LICENSE](LICENSE) voor details.

## Acknowledgments

- **PyUtrecht** community voor de mogelijkheid om te presenteren
- **Containerlab** team voor de geweldige tool
- **Arista Networks** voor cEOS
- **Anton Karneliuk** voor PyGNMI library

## 📧 Contact

**Presenter**: Maurice Stoof  
**Email**: maurice@mcstoof.com  
**LinkedIn**: [@mauricestoof](https://www.linkedin.com/in/maurice-stoof/)  
**GitHub**: [@mstoof](https://github.com/mstoof)


## Real-world Toepassingen

Deze technologie wordt gebruikt bij:

- **Cloud providers**: Real-time monitoring van duizenden devices
- **ISPs**: Network performance monitoring
- **Datacenters**: Fabric health monitoring
- **Enterprise**: Campus network automation
- **SD-WAN**: Dynamic path selection based on telemetry

## Advanced Topics

Voor gevorderde gebruikers:

### Custom Subscriptions

```python
from pygnmi.client import gNMIclient

# Maak custom subscription
subscription = {
    'subscription': [
        {
            'path': '/interfaces/interface[name=Ethernet1]/state/counters',
            'mode': 'sample',
            'sample_interval': 2000000000  # 2 seconden
        }
    ],
    'mode': 'stream',
    'encoding': 'json_ietf'
}

# Start streaming
for update in client.subscribe2(subscription):
    process_telemetry(update)
```

### Integratie met Time Series Database

```python
from influxdb_client import InfluxDBClient

# Schrijf naar InfluxDB
def write_to_influxdb(interface, rx_bytes, tx_bytes):
    point = {
        "measurement": "interface_counters",
        "tags": {"interface": interface},
        "fields": {
            "rx_bytes": rx_bytes,
            "tx_bytes": tx_bytes
        }
    }
    write_api.write(bucket="network", record=point)
```



---

**Made with ❤️ for the Python & Network Automation community**

🐍 Happy automating! 🚀