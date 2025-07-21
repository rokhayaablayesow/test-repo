# Serveur RTMP pour Streaming Vidéo

Un serveur RTMP (Real-Time Messaging Protocol) implémenté en Python pour la publication et la diffusion de vidéo en streaming.

## Architecture

```
serveur-RTMP/
├── main.py              # Point d'entrée principal
├── rtmp_server.py       # Serveur RTMP de base avec handshake
├── stream_manager.py    # Gestion des streams et abonnés
├── video_processor.py   # Traitement vidéo/audio (H.264/AAC)
├── test_client.py       # Client de test pour simuler le streaming
└── requirements.txt     # Dépendances (aucune externe requise)
```

## Fonctionnalités

- **Handshake RTMP** : Négociation de connexion conforme au protocole RTMP
- **Streaming vidéo** : Support H.264 avec détection des keyframes
- **Streaming audio** : Support AAC avec configuration automatique
- **Multi-streams** : Gestion de plusieurs streams simultanés
- **Abonnés multiples** : Plusieurs viewers par stream
- **Validation** : Vérification des données RTMP/FLV
- **Monitoring** : Logs détaillés et statistiques

## Utilisation

### Démarrer le serveur

```bash
# Serveur sur port par défaut (1935)
python main.py

# Configuration personnalisée
python main.py --host 0.0.0.0 --port 1935 --log-level DEBUG --max-streams 50
```

### Tester avec le client

```bash
# Test basique (30 secondes)
python test_client.py

# Test personnalisé
python test_client.py --host localhost --port 1935 --duration 60 --stream-key mon_stream
```

### Publier avec OBS Studio

1. Ouvrir OBS Studio
2. Aller dans Paramètres > Stream
3. Service: Custom
4. Serveur: `rtmp://localhost:1935/live`
5. Clé de stream: `test_stream` (ou votre clé)

### Publier avec FFmpeg

```bash
# Publier un fichier vidéo
ffmpeg -re -i video.mp4 -c copy -f flv rtmp://localhost:1935/live/test_stream

# Publier webcam (Linux)
ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -preset ultrafast -f flv rtmp://localhost:1935/live/webcam

# Publier webcam (Windows)
ffmpeg -f dshow -i video="Integrated Camera" -c:v libx264 -preset ultrafast -f flv rtmp://localhost:1935/live/webcam
```

## API de Streaming

### Classes principales

- **RTMPServer** : Serveur principal gérant les connexions
- **StreamManager** : Gestionnaire de streams avec publishers/subscribers
- **VideoProcessor** : Analyse et validation des données vidéo/audio
- **RTMPConnection** : Gestion d'une connexion client

### Exemple d'intégration

```python
from rtmp_server import RTMPServer
from stream_manager import StreamManager, StreamMetadata

# Créer le serveur
server = RTMPServer(host="0.0.0.0", port=1935)

# Créer un stream manager
manager = StreamManager()

# Créer un publisher
publisher = manager.create_publisher("mon_stream")

# Métadonnées du stream
metadata = StreamMetadata(
    width=1920, height=1080, fps=30,
    video_bitrate=5000, audio_bitrate=128,
    video_codec="h264", audio_codec="aac"
)

publisher.start_publishing(metadata)

# Démarrer le serveur
server.start()
```

## Configuration

### Variables d'environnement

- `RTMP_HOST` : Adresse d'écoute (défaut: 0.0.0.0)
- `RTMP_PORT` : Port d'écoute (défaut: 1935)
- `RTMP_MAX_STREAMS` : Nombre max de streams (défaut: 100)
- `RTMP_LOG_LEVEL` : Niveau de log (défaut: INFO)

### Ports utilisés

- **1935** : Port standard RTMP
- **8080** : Interface web (future fonctionnalité)

## Monitoring

### Logs

Les logs sont sauvegardés dans `rtmp_server.log` avec les informations suivantes :
- Connexions/déconnexions clients
- Handshakes RTMP
- Début/fin de streams
- Erreurs de traitement

### Statistiques

```python
stats = manager.get_stats()
# {
#   "total_streams": 5,
#   "active_streams": 2, 
#   "total_viewers": 10
# }

active = manager.get_active_streams()
# ["stream1", "stream2"]
```

## Performance

- **Concurrent streams** : Jusqu'à 100 streams simultanés
- **Viewers par stream** : Illimité (limité par la bande passante)
- **Latency** : ~2-3 secondes (typique pour RTMP)
- **Throughput** : Dépend de la configuration réseau

## Sécurité

- Validation des données d'entrée
- Limitation du nombre de connexions
- Timeout des connexions inactives
- Logs d'audit complets

## Limitations actuelles

- Pas d'authentification (à implémenter)
- Pas de SSL/TLS (RTMPS)
- Pas d'enregistrement sur disque
- Pas d'interface web d'administration

## Développement futur

- [ ] Authentification par clé de stream
- [ ] Support RTMPS (SSL)
- [ ] Interface web de monitoring
- [ ] Enregistrement des streams
- [ ] Transcodage adaptatif
- [ ] CDN integration
- [ ] API REST

## Tests

```bash
# Test du serveur (terminal 1)
python main.py --log-level DEBUG

# Test du client (terminal 2)
python test_client.py --duration 10

# Test avec FFmpeg
ffmpeg -re -f lavfi -i testsrc2=duration=10:size=640x480:rate=30 -f flv rtmp://localhost:1935/live/test
```

## Dépannage

### Problèmes courants

1. **Port 1935 occupé**
   ```bash
   sudo lsof -i :1935
   python main.py --port 1936
   ```

2. **Erreur de permission**
   ```bash
   # Utiliser un port > 1024
   python main.py --port 8935
   ```

3. **Connexion refusée**
   - Vérifier que le serveur est démarré
   - Vérifier les règles de firewall
   - Tester avec `telnet localhost 1935`

### Debug

```bash
# Logs détaillés
python main.py --log-level DEBUG

# Test de connectivité
telnet localhost 1935

# Monitoring réseau
sudo tcpdump -i any port 1935
```