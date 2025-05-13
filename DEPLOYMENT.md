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

### Erreur d'importation de google-play-scraper

Si vous rencontrez l'erreur:
```
ImportError: This app has encountered an error. The original error message is redacted...
```

Cette erreur est généralement liée à l'installation de la bibliothèque `google-play-scraper`. 

**Solutions:**

1. **Vérifiez votre fichier requirements.txt**
   ```
   streamlit==1.31.0
   pandas==2.1.3
   plotly==5.18.0
   google-play-scraper==1.2.4
   numpy>=1.20.0
   datetime
   requests>=2.25.0
   ```

2. **Utilisez notre version robuste de app.py**
   - L'application est conçue pour fonctionner même si `google-play-scraper` n'est pas disponible
   - Elle passera automatiquement en "mode démo" avec des données factices

3. **Alternative: Installez manuellement les packages**
   - Accédez aux paramètres de l'application dans Streamlit Cloud
   - Ajoutez la commande suivante dans "Advanced settings > Packages":
     ```
     pip install google-play-scraper==1.2.4
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

## Conseils d'optimisation

- Les caches (`@st.cache_data`) sont configurés pour 1 heure (3600 secondes)
- Réduisez le TTL si vous avez besoin de données plus fraîches
- Augmentez le TTL pour améliorer les performances

## Utilisation dans un environnement de production

Pour un usage intensif:

1. Considérez l'utilisation d'un serveur proxy rotatif
2. Implémentez un système de mise en file d'attente des requêtes
3. Envisagez de passer à des API officielles si disponibles
