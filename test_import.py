import streamlit as st

# Configuration de la page - DOIT ÊTRE LE PREMIER APPEL À STREAMLIT
st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="wide"
)

st.title("Test d'importation de Scraper")

# Test d'importation du scraper officiel
st.subheader("1. Test de google-play-scraper")
try:
    from google_play_scraper import search, app, reviews, suggestions
    st.success("✅ L'importation de google-play-scraper a réussi!")
    st.write("Version installée:", getattr(search, "__version__", "Inconnue"))
    
    # Afficher les fonctions disponibles
    st.code("""
    from google_play_scraper import search, app, reviews, suggestions
    
    # Rechercher des applications
    results = search("fitness tracker", lang="fr", country="fr")
    
    # Obtenir les détails d'une application
    details = app("com.example.app", lang="fr", country="fr")
    
    # Récupérer les avis
    reviews_result, continuation_token = reviews("com.example.app", lang="fr", country="fr")
    
    # Obtenir des suggestions de recherche
    sugg = suggestions("app", lang="fr", country="fr")
    """)
    
except ImportError as e:
    st.error(f"❌ Erreur d'importation du scraper officiel: {str(e)}")

# Test d'importation du scraper personnalisé
st.subheader("2. Test de notre scraper personnalisé")
try:
    from scrapers.play_scraper import search as custom_search, __version__ as custom_version
    st.success("✅ L'importation du scraper personnalisé a réussi!")
    st.write("Version du scraper personnalisé:", custom_version)
    
    # Tester une fonction du scraper personnalisé
    st.subheader("Test de fonctionnalité")
    with st.spinner("Recherche de suggestions pour 'app'..."):
        suggestions = custom_search("app", n_hits=3)
        st.write("Résultats de recherche pour 'app':", suggestions)
        
    if suggestions:
        st.success("Le scraper personnalisé fonctionne correctement!")
    else:
        st.warning("Le scraper personnalisé n'a retourné aucun résultat.")
        
except ImportError as e:
    st.error(f"❌ Erreur d'importation du scraper personnalisé: {str(e)}")
    st.info("Assurez-vous que le dossier 'scrapers' est présent dans le même répertoire que ce script.")

# Informations système
st.subheader("Informations système")
import sys
st.write(f"Python version: {sys.version}")
st.write(f"Executable path: {sys.executable}")

# Lister tous les packages installés
st.subheader("Packages installés")
try:
    import subprocess
    installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8")
    st.code(installed_packages)
except Exception as e:
    st.error(f"Impossible de lister les packages: {str(e)}")

# Récapitulatif
st.subheader("Récapitulatif")
st.markdown("""
### Diagnostic:

Si vous voyez l'un des scrapers importé avec succès, votre application devrait fonctionner correctement.

#### Préférence d'utilisation:
1. Scraper officiel (google-play-scraper) - Données réelles
2. Scraper personnalisé (scrapers.play_scraper) - Données simulées
3. Mode démo - Si aucun scraper n'est disponible

### Que faire maintenant?
- Si les tests réussissent, déployez la version principale de l'application
- Si l'import échoue, vérifiez les instructions dans DEPLOYMENT.md
""")