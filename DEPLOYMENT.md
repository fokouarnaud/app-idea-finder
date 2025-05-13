# Guide de déploiement sur Streamlit Cloud

Ce document explique comment déployer avec succès l'application App-Idea-Finder sur Streamlit Cloud et résoudre les problèmes courants.

## Prérequis

- Un compte GitHub
- Un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
- Un dépôt GitHub contenant votre application

## Étapes de déploiement

1. **Créez un nouveau dépôt sur GitHub**
   - Créez un nouveau dépôt (public ou privé)
   - Ajoutez-y les fichiers de l'application:
     - `app.py`
     - `requirements.txt`
     - `README.md`
     - `.streamlit/config.toml` (optionnel)

2. **Connectez-vous à Streamlit Cloud**
   - Allez sur [share.streamlit.io](https://share.streamlit.io/)
   - Connectez-vous avec votre compte GitHub

3. **Déployez l'application**
   - Cliquez sur "New app"
   - Sélectionnez votre dépôt GitHub
   - Sélectionnez la branche (généralement main)
   - Entrez le chemin du fichier principal: `app.py`
   - Cliquez sur "Deploy"

## Résolution des problèmes courants

### IMPORTANT: Ordre des commandes Streamlit

La fonction `st.set_page_config()` doit être le premier appel à une fonction Streamlit dans votre script. Assurez-vous qu'aucune commande Streamlit (`st.something()`) n'est appelée avant cette ligne.

```python
import streamlit as st

# Correct - Premier appel à Streamlit
st.set_page_config(page_title="Mon app", page_icon="🔍")

# Autres imports et initialisations après
import pandas as pd
```

### Erreur d'importation de google-play-scraper

Si vous rencontrez l'erreur:
```
ImportError: This app has encountered an error. The original error message is redacted...
```

Cette erreur est généralement liée à l'installation de la bibliothèque `google-play-scraper`. 

**Solutions:**

1. **Vérifiez votre fichier requirements.txt**
   ```
   streamlit>=1.25.0
   pandas>=1.5.0
   plotly>=5.14.0
   google-play-scraper==1.2.4
   numpy>=1.20.0
   requests>=2.25.0
   protobuf>=3.20.0,<4.0.0
   ```

2. **Utilisez notre version robuste de app.py**
   - L'application est conçue pour fonctionner même si `google-play-scraper` n'est pas disponible
   - Elle passera automatiquement en "mode démo" avec des données factices

3. **Testez l'importation avec test_import.py**
   - Déployez d'abord le fichier de test pour vérifier si le package est correctement installé
   - Il fournira des informations diagnostiques utiles

4. **Alternative: Utilisez un fichier packages.txt**
   - Créez un fichier `packages.txt` à la racine du dépôt avec les dépendances système
   ```
   build-essential
   python3-dev
   ```

### Problèmes de performance

Si l'application est lente:

1. Réduisez les valeurs par défaut pour:
   - `max_suggestions`
   - `max_concurrents`

2. Augmentez les délais entre les requêtes dans le code pour éviter les blocages

### Erreurs de scraping

Si vous obtenez des erreurs lors du scraping:

1. Le système de gestion d'erreur avec backoff exponentiel devrait gérer automatiquement ces problèmes
2. Vérifiez si Google a modifié son API ou interface (cela peut nécessiter une mise à jour de `google-play-scraper`)
3. Considérez l'utilisation d'un proxy si vous êtes bloqué de manière persistante

## Méthode de déploiement alternative

Si vous continuez à rencontrer des problèmes, essayez cette approche alternative:

1. **Utilisez une image Docker personnalisée**
   - Créez un fichier `Dockerfile`:
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt ./
   RUN pip install --no-cache-dir -r requirements.txt
   RUN pip install --no-cache-dir google-play-scraper==1.2.4
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py"]
   ```
   - Déployez sur un service prenant en charge Docker (Heroku, DigitalOcean, etc.)

2. **Utilisez les Streamlit Community Cloud Apps**
   - Si l'application est importante pour vous, envisagez de passer à un plan payant
   - Cela offre davantage de contrôle sur l'environnement d'exécution

## Conseils d'optimisation

- Les caches (`@st.cache_data`) sont configurés pour 1 heure (3600 secondes)
- Réduisez le TTL si vous avez besoin de données plus fraîches
- Augmentez le TTL pour améliorer les performances

## Utilisation dans un environnement de production

Pour un usage intensif:

1. Considérez l'utilisation d'un serveur proxy rotatif
2. Implémentez un système de mise en file d'attente des requêtes
3. Envisagez de passer à des API officielles si disponibles
