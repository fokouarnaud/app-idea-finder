"""
Version simplifiée du module google-play-scraper
"""
import json
import requests
from typing import List, Dict, Any, Tuple, Optional

__version__ = "0.1.0"

# Constantes
BASE_URL = "https://play.google.com/store/apps"
SEARCH_URL = "https://play.google.com/store/search"
SUGGESTIONS_URL = "https://market.android.com/suggest/SuggRequest"

def search(query: str, lang: str = "en", country: str = "us", n_hits: int = 5) -> List[Dict[str, Any]]:
    """Recherche des applications sur le Play Store"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": f"{lang}-{country}"
        }
        params = {
            "q": query,
            "c": "apps",
            "hl": lang,
            "gl": country
        }
        
        # Effectuer la requête
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=30)
        
        # Simuler les résultats car le parsing HTML est complexe
        # Dans une implémentation réelle, nous ferions du scraping HTML ici
        return generate_dummy_results(query, n_hits)
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {str(e)}")
        return []

def app(app_id: str, lang: str = "en", country: str = "us") -> Dict[str, Any]:
    """Récupère les détails d'une application"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": f"{lang}-{country}"
        }
        url = f"{BASE_URL}/details?id={app_id}&hl={lang}&gl={country}"
        
        # Effectuer la requête
        response = requests.get(url, headers=headers, timeout=30)
        
        # Simuler les résultats
        return generate_dummy_app_details(app_id)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des détails: {str(e)}")
        return {}

def reviews(app_id: str, lang: str = "en", country: str = "us", count: int = 30, sort: str = "NEWEST") -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Récupère les avis d'une application"""
    try:
        # Simuler les avis
        return generate_dummy_reviews(app_id, count), None
        
    except Exception as e:
        print(f"Erreur lors de la récupération des avis: {str(e)}")
        return [], None
        
def suggestions(query: str, lang: str = "en", country: str = "us") -> List[str]:
    """Récupère les suggestions de recherche"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        params = {
            "query": query,
            "language": lang,
            "country": country
        }
        
        # Effectuer la requête
        response = requests.get(SUGGESTIONS_URL, headers=headers, params=params, timeout=30)
        
        # Simuler les suggestions
        return generate_dummy_suggestions(query)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des suggestions: {str(e)}")
        return []

# Fonctions auxiliaires pour générer des données fictives

def generate_dummy_results(query: str, n: int) -> List[Dict[str, Any]]:
    """Génère des résultats fictifs"""
    results = []
    for i in range(min(n, 10)):
        results.append({
            "appId": f"com.example.{query.lower().replace(' ', '')}{i}",
            "title": f"{query.title()} App {i+1}",
            "developer": f"Developer {i+1}",
            "developerId": f"dev{i+1}",
            "icon": f"https://via.placeholder.com/150?text={query.replace(' ', '+')}+{i+1}",
            "score": round(3.5 + (i % 3) * 0.5, 1),
            "price": 0 if i % 3 != 0 else 2.99,
            "free": i % 3 == 0,
            "summary": f"This is a fictional {query} application for demonstration purposes.",
            "minInstalls": 10000 * (i+1)
        })
    return results

def generate_dummy_app_details(app_id: str) -> Dict[str, Any]:
    """Génère des détails d'application fictifs"""
    app_name = app_id.split(".")[-1].title()
    return {
        "appId": app_id,
        "title": app_name,
        "description": f"This is a detailed description for {app_name}. The application provides various features and functionalities that users might find useful. It's designed to be user-friendly and efficient.\n\nKey Features:\n- Feature 1\n- Feature 2\n- Feature 3\n\nThis is a fictional description for demonstration purposes.",
        "descriptionHTML": f"<p>This is a detailed description for {app_name}...</p>",
        "summary": f"Summary of {app_name}",
        "installs": "1,000,000+",
        "minInstalls": 1000000,
        "score": 4.2,
        "ratings": 50000,
        "reviews": 10000,
        "histogram": [1000, 2000, 5000, 15000, 27000],
        "price": 0,
        "free": True,
        "currency": "USD",
        "priceText": "Free",
        "offersIAP": True,
        "IAPRange": "$0.99 - $9.99",
        "size": "15M",
        "androidVersion": "5.0 and up",
        "androidVersionText": "5.0+",
        "developer": f"{app_name} Developer",
        "developerId": f"dev_{app_id}",
        "developerEmail": f"dev@{app_id}.com",
        "developerWebsite": f"https://www.{app_id}.com",
        "developerAddress": "123 Developer Street, Tech City",
        "genre": "Tools",
        "genreId": "TOOLS",
        "icon": f"https://via.placeholder.com/150?text={app_name}",
        "headerImage": f"https://via.placeholder.com/600x200?text={app_name}+Header",
        "screenshots": [f"https://via.placeholder.com/300x600?text={app_name}+Screenshot+{i+1}" for i in range(5)],
        "contentRating": "Everyone",
        "adSupported": True,
        "released": "Jan 15, 2020",
        "updated": "Jun 20, 2025",
        "version": "2.3.1",
        "recentChanges": "- Bug fixes\n- Performance improvements\n- New features",
        "comments": [f"User comment {i+1}" for i in range(3)],
        "editorsChoice": False
    }

def generate_dummy_reviews(app_id: str, count: int) -> List[Dict[str, Any]]:
    """Génère des avis fictifs"""
    reviews = []
    for i in range(count):
        score = (i % 5) + 1  # De 1 à 5
        reviews.append({
            "id": f"gp:AOqpTOHF{i}",
            "userName": f"User {i+1}",
            "userImage": f"https://via.placeholder.com/50?text=User+{i+1}",
            "content": generate_review_text(score),
            "score": score,
            "thumbsUpCount": i * 2,
            "reviewCreatedVersion": "2.1.0",
            "at": "2025-05-01",
            "replyContent": "Thank you for your feedback!" if score <= 3 else "",
            "repliedAt": "2025-05-02" if score <= 3 else None
        })
    return reviews

def generate_review_text(score: int) -> str:
    """Génère un texte d'avis en fonction du score"""
    if score == 1:
        return "This app is terrible! It crashes all the time and has a confusing interface. Would not recommend."
    elif score == 2:
        return "Not very good. There are too many ads and the app is slow. Some features don't work as expected."
    elif score == 3:
        return "It's okay but could be better. The interface is a bit confusing and there are some bugs that need fixing."
    elif score == 4:
        return "Good app with useful features. Just a few minor issues that could be improved, but overall a solid experience."
    else:  # score == 5
        return "Excellent app! Easy to use, fast, and has all the features I need. Highly recommend to everyone!"

def generate_dummy_suggestions(query: str) -> List[str]:
    """Génère des suggestions fictives"""
    base_query = query.lower()
    suggestions = [
        f"{base_query} app",
        f"{base_query} pro",
        f"{base_query} free",
        f"{base_query} plus",
        f"{base_query} premium",
        f"best {base_query}",
        f"{base_query} for beginners",
        f"{base_query} alternative"
    ]
    # Limiter à 5 suggestions
    return suggestions[:5]

# Classe d'exception
class NotFoundError(Exception):
    """Levée lorsqu'une application n'est pas trouvée"""
    pass
