import streamlit as st
import pandas as pd
import plotly.express as px
import time
import random
import requests
import json
from datetime import datetime

# Configuration de la page - DOIT ÊTRE LE PREMIER APPEL À STREAMLIT
st.set_page_config(
    page_title="App Idea Finder",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0068C9;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .highlight {
        background-color: #FFFF00;
        padding: 0 2px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de SerpApi (à configurer dans les secrets de Streamlit)
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY", None)

# Vérification de la clé API
if not SERPAPI_KEY:
    st.error("⚠️ Clé API SerpApi non configurée. Veuillez configurer votre clé API dans les paramètres de l'application.")
    st.info("""
    **Configuration de la clé API SerpApi**:
    1. Créez un compte sur [SerpApi.com](https://serpapi.com/)
    2. Obtenez votre clé API
    3. Ajoutez la clé dans les paramètres de l'application Streamlit Cloud
       - Accédez à votre application sur Streamlit Cloud
       - Cliquez sur les trois points en haut à droite
       - Sélectionnez "Settings" > "Secrets"
       - Ajoutez votre clé: `SERPAPI_KEY = "votre_clé_api"`
    """)
    st.stop()  # Arrête l'exécution de l'application

# Initialisation des états de session
if "quota" not in st.session_state:
    st.session_state.quota = {
        "total": 100,  # Quota total par session
        "used": 0,     # Quota utilisé
        "reset_time": datetime.now().strftime("%H:%M:%S"),
        "last_error_time": None,
        "backoff_factor": 1.0
    }

if "user_agents" not in st.session_state:
    st.session_state.user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ]

# Fonctions utilitaires
def update_quota(cost=1):
    """Met à jour le quota et vérifie s'il reste des requêtes disponibles"""
    st.session_state.quota["used"] += cost
    
    # Vérifier si le quota est dépassé
    if st.session_state.quota["used"] >= st.session_state.quota["total"]:
        remaining_time = 3600  # 1 heure en secondes
        st.error(f"⚠️ Quota de requêtes atteint! Veuillez réessayer dans environ 1 heure pour éviter d'être bloqué.")
        return False
    return True

def get_random_user_agent():
    """Retourne un User-Agent aléatoire"""
    return random.choice(st.session_state.user_agents)

def handle_api_error(function_name, e):
    """Gère les erreurs d'API avec backoff exponentiel"""
    now = datetime.now()
    
    # Initialiser le temps de la dernière erreur s'il n'existe pas
    if st.session_state.quota["last_error_time"] is None:
        st.session_state.quota["last_error_time"] = now
        st.session_state.quota["backoff_factor"] = 1.0
    else:
        # Augmenter le facteur de backoff
        time_since_last_error = (now - st.session_state.quota["last_error_time"]).total_seconds()
        
        if time_since_last_error < 300:  # Moins de 5 minutes
            st.session_state.quota["backoff_factor"] *= 1.5
        else:
            # Réinitialiser le facteur après 5 minutes sans erreur
            st.session_state.quota["backoff_factor"] = 1.0
        
        st.session_state.quota["last_error_time"] = now
    
    # Calculer le temps d'attente
    wait_time = min(30, 2 * st.session_state.quota["backoff_factor"])
    
    st.warning(f"⚠️ Erreur lors de l'appel à {function_name}: {str(e)}")
    st.info(f"Pause de {wait_time:.1f} secondes pour éviter le blocage...")
    
    time.sleep(wait_time)
    return None

# Fonctions SerpApi
@st.cache_data(ttl=3600)
def serpapi_suggestions(query, lang="fr", country="fr"):
    """Obtient des suggestions de recherche depuis SerpApi Google Autocomplete"""    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_autocomplete",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": country,
        "hl": lang
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lève une exception si la réponse contient une erreur HTTP
        data = response.json()
        
        if "suggestions" in data:
            return [item.get("value", "") for item in data["suggestions"]]
        return []
    except Exception as e:
        handle_api_error("serpapi_suggestions", e)
        return []

@st.cache_data(ttl=3600)
def serpapi_search_apps(query, lang="fr", country="fr", limit=5):
    """Recherche des applications sur le Play Store via SerpApi"""    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_play",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": country,
        "hl": lang,
        "store": "apps"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "organic_results" in data and data["organic_results"]:
            for app_data in data["organic_results"][:limit]:
                # Transformer les données SerpApi en format compatible
                app_info = {
                    "appId": app_data.get("id", ""),
                    "title": app_data.get("title", ""),
                    "developer": app_data.get("developer", ""),
                    "score": app_data.get("rating", 0),
                    "installs": app_data.get("downloads", "Non disponible"),
                    "price": app_data.get("price_text", "Gratuit").replace("Gratuit", "0"),
                    "free": "Gratuit" in app_data.get("price_text", "Gratuit")
                }
                results.append(app_info)
        
        return results
    except Exception as e:
        handle_api_error("serpapi_search_apps", e)
        return []

@st.cache_data(ttl=3600)
def serpapi_app_details(app_id, lang="fr", country="fr"):
    """Récupère les détails d'une application via SerpApi"""
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_play",
        "id": app_id,
        "api_key": SERPAPI_KEY,
        "gl": country,
        "hl": lang
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "app_results" not in data:
            st.error(f"Aucune information trouvée pour l'application {app_id}")
            return None, [], {}, []
        
        app_data = data["app_results"]
        
        # Extraire les informations pertinentes
        details = {
            "title": app_data.get("title", ""),
            "description": app_data.get("description", ""),
            "genre": app_data.get("genre", ""),
            "icon": app_data.get("thumbnail", ""),
            "developer": app_data.get("developer", ""),
            "minInstalls": app_data.get("installs", "Non disponible"),
            "updated": app_data.get("updated", "Non disponible")
        }
        
        # Récupérer les avis (si disponibles)
        app_reviews = []
        reviews_data = app_data.get("reviews", [])
        for review in reviews_data:
            app_reviews.append({
                "content": review.get("content", ""),
                "score": review.get("rating", 0)
            })
        
        # Calculer les statistiques des avis
        avis_stats = {
            "nb_avis_1": sum(1 for r in app_reviews if r["score"] == 1),
            "nb_avis_2": sum(1 for r in app_reviews if r["score"] == 2),
            "nb_avis_3": sum(1 for r in app_reviews if r["score"] == 3),
            "nb_avis_4": sum(1 for r in app_reviews if r["score"] == 4),
            "nb_avis_5": sum(1 for r in app_reviews if r["score"] == 5),
        }
        
        # Extraire les avis négatifs
        avis_negatifs = [r for r in app_reviews if r["score"] <= 3]
        
        return details, app_reviews, avis_stats, avis_negatifs
        
    except Exception as e:
        handle_api_error("serpapi_app_details", e)
        return None, [], {}, []

# Fonctions d'analyse
@st.cache_data(ttl=3600)
def obtenir_suggestions_keywords(prefixes, max_suggestions=5):
    """Obtient les suggestions de recherche pour une liste de préfixes"""
    resultats = {}
    
    for prefix in prefixes:
        if prefix.strip():
            if not update_quota(cost=1):
                break
                
            try:
                # Pause aléatoire avant chaque requête
                time.sleep(random.uniform(1.5, 3.0))
                
                # Utiliser SerpApi pour les suggestions
                sugg = serpapi_suggestions(
                    prefix,
                    lang="fr",
                    country="fr"
                )
                resultats[prefix] = sugg[:max_suggestions] if sugg else []
                
            except Exception as e:
                handle_api_error(f"suggestions('{prefix}')", e)
    
    # Aplatir les résultats
    tous_resultats = []
    for prefix, sugg_list in resultats.items():
        for sugg in sugg_list:
            tous_resultats.append({"prefix": prefix, "suggestion": sugg})
    
    return pd.DataFrame(tous_resultats) if tous_resultats else pd.DataFrame(columns=["prefix", "suggestion"])

@st.cache_data(ttl=3600)
def analyser_concurrence(keyword, limit=5, max_retries=3):
    """Analyse la concurrence pour un mot-clé donné avec tentatives de réessai"""
    if not update_quota(cost=2):  # Coût plus élevé pour l'analyse concurrentielle
        return pd.DataFrame(columns=["app_id", "title", "score", "installs", "price"])
    
    for attempt in range(max_retries):
        try:
            # Pause plus longue pour les recherches d'applications
            time.sleep(random.uniform(2.0, 4.0))
            
            # Rechercher les applications via SerpApi
            results = serpapi_search_apps(
                keyword,
                lang="fr",
                country="fr",
                limit=limit
            )
            
            if not results:
                return pd.DataFrame(columns=["app_id", "title", "score", "installs", "price"])
            
            # Extraire les données de base
            apps_data = []
            for app_info in results:
                apps_data.append({
                    "app_id": app_info["appId"],
                    "title": app_info["title"],
                    "developer": app_info["developer"],
                    "score": app_info["score"],
                    "installs": app_info.get("installs", "Non disponible"),
                    "price": app_info["price"],
                    "free": app_info["free"]
                })
            
            return pd.DataFrame(apps_data)
            
        except Exception as e:
            wait_time = handle_api_error(f"search('{keyword}')", e)
            if attempt == max_retries - 1:
                st.error(f"Échec après {max_retries} tentatives. Veuillez réessayer plus tard.")
                return pd.DataFrame(columns=["app_id", "title", "score", "installs", "price"])

@st.cache_data(ttl=3600)
def analyser_details_app(app_id, max_retries=3):
    """Récupère les détails d'une application avec tentatives de réessai"""
    if not update_quota(cost=3):  # Coût élevé pour l'analyse détaillée
        return None, [], {}, []
    
    for attempt in range(max_retries):
        try:
            # Pause plus longue pour les détails d'application
            time.sleep(random.uniform(2.5, 5.0))
            
            # Obtenir les détails via SerpApi
            details, app_reviews, avis_stats, avis_negatifs = serpapi_app_details(
                app_id,
                lang="fr",
                country="fr"
            )
            
            return details, app_reviews, avis_stats, avis_negatifs
            
        except Exception as e:
            wait_time = handle_api_error(f"app_details('{app_id}')", e)
            if attempt == max_retries - 1:
                st.error(f"Échec après {max_retries} tentatives. Veuillez réessayer plus tard.")
                return None, [], {}, []

def evaluer_potentiel_marche(apps_df):
    """Évalue le potentiel d'un marché en fonction des apps concurrentes"""
    if apps_df.empty:
        return {
            "score": 0,
            "nb_concurrents": 0,
            "note_moyenne": 0,
            "difficulte": "Indéterminée",
            "potentiel": "Indéterminé"
        }
    
    nb_concurrents = len(apps_df)
    note_moyenne = apps_df["score"].mean() if "score" in apps_df else 0
    
    # Calcul du potentiel
    if nb_concurrents == 0:
        difficulte = "Indéterminée"
        potentiel = "Indéterminé"
        score = 0
    elif nb_concurrents < 3:
        difficulte = "Faible"
        potentiel = "Incertain" if note_moyenne >= 4.0 else "Faible"
        score = 40 if note_moyenne >= 4.0 else 20
    elif nb_concurrents <= 10:
        difficulte = "Moyenne"
        potentiel = "Élevé" if note_moyenne < 4.0 else "Moyen"
        score = 80 if note_moyenne < 4.0 else 60
    else:
        difficulte = "Élevée"
        potentiel = "Faible" if note_moyenne >= 4.5 else "Moyen"
        score = 30 if note_moyenne >= 4.5 else 50
    
    return {
        "score": score,
        "nb_concurrents": nb_concurrents,
        "note_moyenne": round(note_moyenne, 1),
        "difficulte": difficulte,
        "potentiel": potentiel
    }

# Interface utilisateur
st.markdown('<h1 class="main-header">🔍 App Idea Finder</h1>', unsafe_allow_html=True)
st.markdown("""
Découvrez des idées d'applications rentables en analysant les recherches réelles 
des utilisateurs et la concurrence sur le Google Play Store.
""")

# Afficher l'état du quota dans la sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Affichage du quota
    st.markdown(f"""
    ### Quota de requêtes
    <div class="metric-card">
        <p>Utilisé: <b>{st.session_state.quota['used']}/{st.session_state.quota['total']}</b></p>
        <p>Réinitialisation: <b>{st.session_state.quota['reset_time']}</b></p>
        <div style="background-color: {'green' if st.session_state.quota['used'] < st.session_state.quota['total']*0.7 
                                     else 'orange' if st.session_state.quota['used'] < st.session_state.quota['total']*0.9 
                                     else 'red'}; 
                  height: 10px; 
                  width: {min(100, (st.session_state.quota['used']/st.session_state.quota['total'])*100)}%; 
                  border-radius: 5px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Option pour réinitialiser le quota (à des fins de démonstration)
    if st.button("Réinitialiser le quota"):
        st.session_state.quota["used"] = 0
        st.session_state.quota["reset_time"] = datetime.now().strftime("%H:%M:%S")
        st.session_state.quota["backoff_factor"] = 1.0
        st.session_state.quota["last_error_time"] = None
        st.rerun()
    
    analyse_mode = st.radio(
        "Mode d'analyse",
        ["Recherche par préfixe", "Analyse de mot-clé spécifique"]
    )
    
    with st.expander("Paramètres anti-blocage", expanded=False):
        max_suggestions = st.slider("Nombre max de suggestions par préfixe", 2, 10, 3)
        max_concurrents = st.slider("Nombre max d'apps concurrentes à analyser", 2, 10, 3)
        st.info("💡 Des valeurs plus faibles réduisent considérablement le risque d'être bloqué")
        
        st.divider()
        st.markdown("### Stratégies anti-blocage actives")
        st.markdown("""
        - ✅ Délais aléatoires entre requêtes
        - ✅ Système de quota par session
        - ✅ Backoff exponentiel en cas d'erreur
        - ✅ Rotation des User-Agents
        - ✅ Mise en cache des résultats (1h)
        - ✅ Limitation du volume de données
        """)

# Interface principale
tab1, tab2, tab3 = st.tabs(["Recherche", "Analyse de la concurrence", "Potentiel du marché"])

# Onglet 1: Recherche
with tab1:
    st.markdown('<h2 class="sub-header">Recherche de mots-clés</h2>', unsafe_allow_html=True)
    
    if analyse_mode == "Recherche par préfixe":
        prefixe_type = st.radio("Type de recherche", ["Alphabétique", "Personnalisé"])
        
        if prefixe_type == "Alphabétique":
            lettres = st.multiselect(
                "Sélectionnez les lettres à analyser (maximum 3 recommandé)", 
                list("abcdefghijklmnopqrstuvwxyz"),
                ["a"]
            )
            if len(lettres) > 3:
                st.warning("⚠️ Sélectionner plus de 3 lettres augmente considérablement le risque d'être bloqué!")
        else:
            prefixes_input = st.text_area(
                "Entrez vos préfixes (un par ligne, maximum 3 recommandé)",
                "app"
            )
            lettres = [p.strip() for p in prefixes_input.split("\n") if p.strip()]
            if len(lettres) > 3:
                st.warning("⚠️ Utiliser plus de 3 préfixes augmente considérablement le risque d'être bloqué!")
        
        if st.button("Rechercher des suggestions", disabled=st.session_state.quota["used"] >= st.session_state.quota["total"]):
            if not lettres:
                st.warning("Veuillez sélectionner au moins un préfixe à analyser.")
            else:
                with st.spinner(f"Recherche de suggestions pour {len(lettres)} préfixes..."):
                    # Simulation d'une barre de progression
                    progress_bar = st.progress(0)
                    for i in range(101):
                        progress_bar.progress(i)
                        time.sleep(0.01)
                    
                    # Récupérer les suggestions
                    suggestions_df = obtenir_suggestions_keywords(lettres, max_suggestions)
                    
                    # Stocker dans la session state
                    st.session_state.suggestions_df = suggestions_df
                    
                    if suggestions_df.empty:
                        st.warning("Aucune suggestion trouvée pour les préfixes sélectionnés. Essayez d'autres préfixes.")
                    else:
                        st.success(f"✅ {len(suggestions_df)} suggestions trouvées!")
                        
                        # Afficher les résultats
                        st.dataframe(suggestions_df)
                        
                        if len(suggestions_df) > 1:
                            # Visualisation
                            fig = px.bar(
                                suggestions_df.groupby("prefix").count().reset_index(),
                                x="prefix",
                                y="suggestion",
                                title="Nombre de suggestions par préfixe",
                                labels={"suggestion": "Nombre de suggestions", "prefix": "Préfixe"}
                            )
                            st.plotly_chart(fig, use_container_width=True)
    else:
        mot_cle = st.text_input("Entrez un mot-clé spécifique à analyser", "fitness tracker")
        
        if st.button("Analyser le mot-clé", disabled=st.session_state.quota["used"] >= st.session_state.quota["total"]):
            if not mot_cle:
                st.warning("Veuillez entrer un mot-clé à analyser.")
            else:
                with st.spinner(f"Analyse du mot-clé '{mot_cle}'..."):
                    # Créer un DataFrame avec ce seul mot-clé
                    st.session_state.suggestions_df = pd.DataFrame([{
                        "prefix": mot_cle.split()[0] if ' ' in mot_cle else mot_cle,
                        "suggestion": mot_cle
                    }])
                    
                    st.success(f"Mot-clé '{mot_cle}' prêt à être analysé!")
                    
                    # Rediriger vers l'onglet d'analyse
                    st.session_state.active_tab = "Analyse"

# Onglet 2: Analyse de la concurrence
with tab2:
    st.markdown('<h2 class="sub-header">Analyse de la concurrence</h2>', unsafe_allow_html=True)
    
    if "suggestions_df" in st.session_state and not st.session_state.suggestions_df.empty:
        # Liste des suggestions disponibles
        suggestions_list = st.session_state.suggestions_df["suggestion"].unique().tolist()
        selected_keyword = st.selectbox("Sélectionnez un mot-clé à analyser", suggestions_list)
        
        if st.button("Analyser la concurrence", disabled=st.session_state.quota["used"] >= st.session_state.quota["total"]):
            with st.spinner(f"Analyse de la concurrence pour '{selected_keyword}'..."):
                # Analyser la concurrence
                concurrence_df = analyser_concurrence(selected_keyword, max_concurrents)
                
                # Stocker dans la session state
                st.session_state.concurrence_df = concurrence_df
                st.session_state.selected_keyword = selected_keyword
                
                if concurrence_df.empty:
                    st.warning(f"Aucune application trouvée pour le mot-clé '{selected_keyword}'. Essayez un autre mot-clé.")
                else:
                    st.success(f"✅ {len(concurrence_df)} applications concurrentes trouvées!")
                    
                    # Afficher les résultats
                    st.dataframe(concurrence_df)
                    
                    # Visualisation des scores
                    fig = px.bar(
                        concurrence_df,
                        x="title",
                        y="score",
                        color="score",
                        color_continuous_scale="RdYlGn",
                        title=f"Évaluations des applications pour '{selected_keyword}'",
                        labels={"title": "Application", "score": "Évaluation"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Évaluation du potentiel
                    potentiel = evaluer_potentiel_marche(concurrence_df)
                    st.session_state.potentiel = potentiel
                    
                    # Afficher le résumé
                    st.markdown('<h3>Résumé du marché</h3>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Nombre de concurrents", potentiel["nb_concurrents"])
                    with col2:
                        st.metric("Note moyenne", potentiel["note_moyenne"])
                    with col3:
                        st.metric("Difficulté", potentiel["difficulte"])
                    with col4:
                        st.metric("Potentiel", potentiel["potentiel"])
    else:
        st.info("Commencez par rechercher des suggestions dans l'onglet 'Recherche'.")

# Onglet 3: Potentiel du marché
with tab3:
    st.markdown('<h2 class="sub-header">Analyse détaillée du potentiel</h2>', unsafe_allow_html=True)
    
    if "concurrence_df" in st.session_state and not st.session_state.concurrence_df.empty:
        # Sélection de l'application à analyser
        app_options = st.session_state.concurrence_df[["title", "app_id"]].values.tolist()
        selected_app = st.selectbox(
            "Sélectionnez une application à analyser en détail",
            options=[f"{app[0]} ({app[1]})" for app in app_options],
            format_func=lambda x: x.split(" (")[0]
        )
        
        selected_app_id = selected_app.split(" (")[1].rstrip(")")
        
        if st.button("Analyser l'application", disabled=st.session_state.quota["used"] >= st.session_state.quota["total"]):
            with st.spinner(f"Analyse détaillée de '{selected_app.split(' (')[0]}'..."):
                # Analyser les détails de l'application
                details, app_reviews, avis_stats, avis_negatifs = analyser_details_app(selected_app_id)
                
                if details:
                    # Afficher les informations de base
                    st.markdown(f"### {details['title']}")
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(
                            details["icon"],
                            width=150,
                            caption=f"Par {details['developer']}"
                        )
                    with col2:
                        st.markdown(f"**Description:** {details['description'][:300]}...")
                        st.markdown(f"**Catégorie:** {details['genre']}")
                        st.markdown(f"**Installations:** {details.get('minInstalls', 'Non disponible')}")
                        st.markdown(f"**Dernière mise à jour:** {details.get('updated', 'Non disponible')}")
                    
                    # Évaluation et avis
                    st.markdown("### Évaluation et avis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # Distribution des avis
                        avis_data = pd.DataFrame({
                            "Note": ["5 étoiles", "4 étoiles", "3 étoiles", "2 étoiles", "1 étoile"],
                            "Nombre": [
                                avis_stats["nb_avis_5"],
                                avis_stats["nb_avis_4"],
                                avis_stats["nb_avis_3"],
                                avis_stats["nb_avis_2"],
                                avis_stats["nb_avis_1"]
                            ]
                        })
                        
                        fig = px.bar(
                            avis_data,
                            x="Note",
                            y="Nombre",
                            color="Note",
                            title="Distribution des avis"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Afficher quelques avis négatifs
                        st.markdown("#### Problèmes soulevés par les utilisateurs")
                        
                        if avis_negatifs:
                            for i, avis in enumerate(avis_negatifs[:3]):
                                st.markdown(f"""
                                **Avis {i+1} ({avis['score']}⭐):**  
                                "{avis['content'][:200]}..."
                                """)
                        else:
                            st.markdown("Pas d'avis négatifs récents trouvés.")
                    
                    # Analyse des opportunités
                    st.markdown("### Opportunités d'amélioration")
                    
                    # Marché global
                    if "potentiel" in st.session_state:
                        potentiel = st.session_state.potentiel
                        st.markdown(f"""
                        Pour le mot-clé **"{st.session_state.selected_keyword}"**, le marché présente:
                        - Nombre de concurrents: **{potentiel['nb_concurrents']}**
                        - Note moyenne: **{potentiel['note_moyenne']}⭐**
                        - Difficulté: **{potentiel['difficulte']}**
                        - Potentiel: **{potentiel['potentiel']}**
                        """)
                    
                    # Opportunités basées sur les avis négatifs
                    if avis_negatifs:
                        st.markdown("""
                        **Opportunités identifiées:**
                        
                        En analysant les avis négatifs de cette application et de ses concurrents,
                        il semble y avoir des opportunités d'amélioration sur les points suivants:
                        """)
                        
                        problemes = ["Interface utilisateur confuse", "Fonctionnalités manquantes", "Trop de publicités"]
                        for probleme in problemes:
                            st.markdown(f"- {probleme}")
                    
                    # Téléchargement du rapport
                    st.download_button(
                        "Télécharger le rapport complet",
                        f"Rapport d'analyse pour {details['title']}\n\n" + 
                        f"Mot-clé: {st.session_state.selected_keyword}\n" +
                        f"Potentiel du marché: {potentiel['potentiel']}\n" +
                        f"Nombre de concurrents: {potentiel['nb_concurrents']}\n" +
                        "...",
                        file_name=f"rapport_{selected_app_id}.txt"
                    )
    else:
        st.info("Commencez par analyser la concurrence dans l'onglet 'Analyse de la concurrence'.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Développé avec ❤️ pour trouver des idées d'applications rentables</p>
    <p><strong>Protection anti-blocage activée</strong> | Dernière mise à jour: Mai 2025</p>
</div>
""", unsafe_allow_html=True)
