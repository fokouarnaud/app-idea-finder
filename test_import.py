import streamlit as st

# Configuration de la page - DOIT ÊTRE LE PREMIER APPEL À STREAMLIT
st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="wide"
)

st.title("Test d'importation de Google-Play-Scraper")

# Test d'importation
try:
    from google_play_scraper import search, app, reviews, suggestions
    st.success("✅ L'importation de google-play-scraper a réussi!")
    st.write("Version installée:", getattr(search, "__version__", "Inconnue"))
    
    # Afficher les fonctions disponibles
    st.subheader("Fonctions disponibles:")
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
    st.error(f"❌ Erreur d'importation: {str(e)}")
    st.info("Essayons d'installer le package manuellement...")
    
    # Afficher la commande d'installation
    st.code("pip install google-play-scraper==1.2.4")
    
    # Tenter l'installation (ne fonctionnera pas dans Streamlit Cloud)
    import sys
    import subprocess
    try:
        st.write("Tentative d'installation...")
        result = subprocess.check_output([sys.executable, "-m", "pip", "install", "google-play-scraper==1.2.4"])
        st.success("Installation réussie! Redémarrez l'application.")
    except Exception as install_error:
        st.error(f"Erreur lors de l'installation: {str(install_error)}")
        st.warning("Cette opération n'est probablement pas autorisée dans Streamlit Cloud.")

# Informations système
st.subheader("Informations système")
import sys
st.write(f"Python version: {sys.version}")
st.write(f"Executable path: {sys.executable}")

# Lister tous les packages installés
st.subheader("Packages installés")
try:
    installed_packages = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8")
    st.code(installed_packages)
except Exception as e:
    st.error(f"Impossible de lister les packages: {str(e)}")
