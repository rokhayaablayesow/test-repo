# Restaurant Menu - Application Mobile Hybride

Application mobile hybride développée avec Apache Cordova pour Android, basée sur l'interface web du menu restaurant.

## 🚀 Fonctionnalités

- **Interface mobile responsive** adaptée aux écrans tactiles
- **Navigation par catégories** avec sidebar coulissante
- **Recherche de plats** en temps réel
- **Panier d'achat** avec animation
- **Navigation bottom** native mobile
- **Gestes tactiles** (swipe pour ouvrir/fermer le menu)
- **Feedback haptique** (vibrations)
- **Support PWA** avec service worker

## 📱 Prérequis

- Node.js (v14 ou supérieur)
- Apache Cordova
- Android SDK
- Java Development Kit (JDK)

## 🛠️ Installation

1. **Installer Cordova globalement**
   ```bash
   npm install -g cordova
   ```

2. **Installer les dépendances du projet**
   ```bash
   cd "interface mobile hybride"
   npm install
   ```

3. **Ajouter la plateforme Android**
   ```bash
   npm run add-android
   ```

## 🏗️ Build et Déploiement

### Build pour Android
```bash
npm run build
```

### Lancer sur émulateur/appareil Android
```bash
npm run run-android
```

### Serveur de développement
```bash
npm run serve
```

## 📁 Structure du Projet

```
interface mobile hybride/
├── config.xml              # Configuration Cordova
├── package.json            # Dépendances npm
├── www/                    # Code source web
│   ├── index.html          # Page principale mobile
│   ├── styles.css          # Styles responsive mobile
│   ├── js/
│   │   └── app.js         # Application JavaScript
│   ├── res/               # Ressources (icônes, splash)
│   └── sw.js              # Service Worker PWA
└── platforms/             # Code natif généré
    └── android/
```

## 🎨 Fonctionnalités Mobiles

### Interface Tactile
- **Sidebar coulissante** pour les catégories
- **Scroll horizontal** pour les sous-catégories
- **Grid responsive** pour les plats
- **Bottom navigation** native

### Gestes et Interactions
- **Swipe right** : Ouvrir le menu (depuis le bord gauche)
- **Swipe left** : Fermer le menu
- **Touch feedback** : Animation sur tous les éléments interactifs
- **Vibration** : Feedback haptique sur les actions

### Fonctionnalités Avancées
- **Recherche instantanée** dans tous les plats
- **Panier animé** avec compteur en temps réel
- **Modal panier** avec récapitulatif
- **Gestion du bouton retour** Android
- **Support mode sombre** automatique

## 🔧 Configuration

### Permissions Android (config.xml)
- Accès Internet
- Vibration
- Stockage local

### Optimisations Mobile
- **Viewport** optimisé pour mobile
- **Touch-action** configuré
- **Scroll** smooth natif
- **Cache** avec service worker

## 🚨 Gestion des Événements

### Événements Cordova
- `deviceready` : Initialisation de l'app
- `backbutton` : Gestion du bouton retour Android
- `pause/resume` : Cycle de vie de l'application

### Événements Tactiles
- `touchstart/touchend` : Feedback visuel
- `swipe gestures` : Navigation intuitive
- `long press` : Prévention du menu contextuel

## 📊 Performance

### Optimisations
- **Lazy loading** des images
- **CSS animations** hardware-accelerated
- **Event delegation** pour les interactions
- **Debounced search** pour les performances

### Cache Stratégie
- **Service Worker** pour le cache offline
- **Image caching** automatique
- **API response caching** (si backend connecté)

## 🔍 Debug et Test

### Debug Chrome DevTools
```bash
chrome://inspect/#devices
```

### Logs Cordova
```bash
cordova run android --device --debug
```

### Test Responsive
- **Chrome DevTools** mode mobile
- **Émulateurs Android** différentes tailles
- **Appareils physiques** test réel

## 📱 Déploiement

### APK Debug
```bash
cordova build android --debug
```

### APK Release (Production)
```bash
cordova build android --release
```

### Google Play Store
1. Signer l'APK avec votre keystore
2. Optimiser avec ProGuard
3. Upload sur Google Play Console

## 🎯 Améliorations Futures

- [ ] **Notifications push**
- [ ] **Géolocalisation** pour livraison
- [ ] **Paiement intégré**
- [ ] **Mode offline** complet
- [ ] **Partage social**
- [ ] **Favoris** persistants
- [ ] **Thème personnalisable**
- [ ] **Multi-langue**

## 🐛 Problèmes Connus

- Certaines animations peuvent être saccadées sur anciens appareils
- Le service worker nécessite HTTPS en production
- Les vibrations ne fonctionnent pas sur tous les appareils

## 📝 Notes de Développement

Cette application convertit l'interface web restaurant en application mobile hybride native pour Android. Elle conserve toute la fonctionnalité du menu tout en ajoutant des fonctionnalités mobiles natives comme les gestes tactiles, les vibrations et la navigation mobile.