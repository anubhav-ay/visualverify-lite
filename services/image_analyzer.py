"""Lightweight image analysis - no ML models needed"""
import hashlib
import re
from datetime import datetime
from io import BytesIO
import imagehash
from PIL import Image
import requests

def download_image(url: str, timeout=15) -> Image.Image:
    """Download image from URL"""
    response = requests.get(url, timeout=timeout, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert('RGB')

def get_image_fingerprint(img: Image.Image, img_bytes: bytes) -> dict:
    """Generate image fingerprint (hashes for duplicate detection)"""
    return {
        "md5": hashlib.md5(img_bytes).hexdigest(),
        "phash": str(imagehash.phash(img)),
        "dhash": str(imagehash.dhash(img)),
        "size": len(img_bytes),
        "dimensions": f"{img.width}x{img.height}"
    }

def search_google_images(image_url: str, api_key: str = None) -> list:
    """Google reverse image search via SerpAPI (optional)"""
    if not api_key:
        return []
    try:
        response = requests.get("https://serpapi.com/search", params={
            "engine": "google_lens",
            "url": image_url,
            "api_key": api_key,
        }, timeout=15)
        data = response.json()
        
        results = []
        for match in data.get("visual_matches", [])[:10]:
            results.append({
                "url": match.get("link"),
                "title": match.get("title", ""),
                "snippet": match.get("snippet", ""),
                "source": match.get("source", ""),
            })
        return results
    except Exception as e:
        print(f"Google search failed: {e}")
        return []

def search_bing_news(query: str, api_key: str = None) -> list:
    """Bing news search (optional)"""
    if not api_key or not query:
        return []
    try:
        response = requests.get(
            "https://api.bing.microsoft.com/v7.0/news/search",
            headers={"Ocp-Apim-Subscription-Key": api_key},
            params={"q": query[:100], "count": 10},
            timeout=15
        )
        data = response.json()
        
        results = []
        for article in data.get("value", [])[:10]:
            results.append({
                "url": article.get("url"),
                "title": article.get("name", ""),
                "snippet": article.get("description", ""),
                "date": article.get("datePublished", ""),
            })
        return results
    except Exception as e:
        print(f"Bing search failed: {e}")
        return []

def extract_dates_from_text(text: str) -> list:
    """Extract potential dates from text"""
    dates = []
    # YYYY format
    years = re.findall(r'\b(20\d{2})\b', text)
    dates.extend(years)
    # Month YYYY format
    month_year = re.findall(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b', text, re.IGNORECASE)
    dates.extend([f"{m} {y}" for m, y in month_year])
    return dates[:5]

def extract_locations(text: str) -> list:
    """Extract potential location names (capitalized words)"""
    # Simple heuristic: capitalized words that aren't common English words
    caps = re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*\b', text)
    stopwords = {'The', 'This', 'That', 'Image', 'Photo', 'Video', 'People', 'When', 'Where', 'Breaking', 'Watch'}
    locations = [c for c in caps if c not in stopwords]
    return list(set(locations))[:8]

def extract_events(text: str) -> list:
    """Extract event keywords"""
    events = ['flood', 'earthquake', 'fire', 'protest', 'war', 'explosion', 
              'hurricane', 'attack', 'riot', 'crash', 'pandemic', 'election']
    found = [e for e in events if e in text.lower()]
    return list(set(found))

def calculate_credibility(url: str) -> float:
    """Domain credibility score"""
    credible = {
        'reuters.com': 0.95, 'bbc.com': 0.93, 'apnews.com': 0.95,
        'nytimes.com': 0.90, 'theguardian.com': 0.90, 'aljazeera.com': 0.85,
        'cnn.com': 0.82, 'nbcnews.com': 0.82, 'snopes.com': 0.90,
    }
    for domain, score in credible.items():
        if domain in url.lower():
            return score
    return 0.5  # unknown source

def compare_contexts(real_context: dict, claim_context: dict) -> dict:
    """Compare real vs claimed context - deterministic logic"""
    issues = []
    
    # Temporal check
    real_dates = real_context.get("dates", [])
    claim_dates = claim_context.get("dates", [])
    if real_dates and claim_dates:
        try:
            real_year = int(real_dates[0].split()[-1] if ' ' in real_dates[0] else real_dates[0])
            claim_year = int(claim_dates[0].split()[-1] if ' ' in claim_dates[0] else claim_dates[0])
            if claim_year - real_year > 1:
                issues.append({
                    "type": "RECYCLED",
                    "confidence": 0.9,
                    "detail": f"Image from {real_year} being shared as {claim_year} event"
                })
        except:
            pass
    
    # Location check
    real_locs = set(l.lower() for l in real_context.get("locations", []))
    claim_locs = set(l.lower() for l in claim_context.get("locations", []))
    if real_locs and claim_locs and not real_locs & claim_locs:
        issues.append({
            "type": "FALSE_LOCATION",
            "confidence": 0.75,
            "detail": f"Real: {list(real_locs)[:3]}, Claimed: {list(claim_locs)[:3]}"
        })
    
    # Event check
    real_events = set(real_context.get("events", []))
    claim_events = set(claim_context.get("events", []))
    if real_events and claim_events and not real_events & claim_events:
        issues.append({
            "type": "MISLEADING",
            "confidence": 0.65,
            "detail": f"Real event: {list(real_events)}, Claimed: {list(claim_events)}"
        })
    
    return issues
