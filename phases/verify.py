"""Main verification pipeline - single synchronous function"""
import os
from datetime import datetime
from io import BytesIO
from services.image_analyzer import (
    download_image, get_image_fingerprint,
    search_google_images, search_bing_news,
    extract_dates_from_text, extract_locations, extract_events,
    calculate_credibility, compare_contexts
)

def verify_image(image_url: str, user_claim: str = None, api_keys: dict = None) -> dict:
    """
    Main verification function - runs all phases
    Returns complete verdict with explanation
    """
    api_keys = api_keys or {}
    
    try:
        # Phase 1: Download and fingerprint image
        print("📥 Downloading image...")
        response = __import__('requests').get(image_url, timeout=15)
        img_bytes = response.content
        img = __import__('PIL.Image').open(BytesIO(img_bytes)).convert('RGB')
        fingerprint = get_image_fingerprint(img, img_bytes)
        print(f"✓ Image fingerprinted: {fingerprint['md5'][:8]}...")
        
        # Phase 2: Collect evidence (works even without API keys)
        print("🔍 Searching for evidence...")
        evidence = []
        
        # Google reverse image search (optional)
        google_results = search_google_images(image_url, api_keys.get("SERPAPI_KEY"))
        evidence.extend(google_results)
        
        # Bing news search (optional)
        if user_claim:
            bing_results = search_bing_news(user_claim, api_keys.get("BING_API_KEY"))
            evidence.extend(bing_results)
        
        # Demo mode: if no API keys, use mock data
        if not evidence:
            print("⚠️  No API keys - using basic analysis")
            evidence = [{
                "url": "https://example.com/article",
                "title": "No API keys configured - analysis limited",
                "snippet": "Configure SERPAPI_KEY or BING_API_KEY for full analysis",
                "source": "system",
            }]
        
        print(f"✓ Found {len(evidence)} evidence sources")
        
        # Phase 3: Reconstruct real context from evidence
        print("📊 Analyzing evidence...")
        all_text = " ".join([
            e.get("title", "") + " " + e.get("snippet", "")
            for e in evidence
        ])
        
        real_context = {
            "dates": extract_dates_from_text(all_text),
            "locations": extract_locations(all_text),
            "events": extract_events(all_text),
            "sources": len(evidence),
            "avg_credibility": sum(calculate_credibility(e.get("url", "")) for e in evidence) / max(len(evidence), 1)
        }
        
        # Phase 4: Extract claim context
        claim_text = user_claim or ""
        claim_context = {
            "dates": extract_dates_from_text(claim_text),
            "locations": extract_locations(claim_text),
            "events": extract_events(claim_text),
            "text": claim_text
        }
        
        # Phase 5: Compare and reason
        print("⚖️  Comparing contexts...")
        issues = compare_contexts(real_context, claim_context)
        
        # Phase 6: Generate verdict
        if not issues:
            if real_context["avg_credibility"] > 0.7 and real_context["sources"] >= 3:
                verdict = "TRUE"
                confidence = 0.85
                explanation = f"Found {real_context['sources']} credible sources supporting this image and claim."
            else:
                verdict = "UNVERIFIED"
                confidence = 0.4
                explanation = f"Insufficient evidence to verify ({real_context['sources']} sources found)."
        else:
            # Take highest confidence issue
            top_issue = max(issues, key=lambda x: x["confidence"])
            verdict = top_issue["type"]
            confidence = top_issue["confidence"]
            explanation = top_issue["detail"]
            
            if verdict == "RECYCLED":
                explanation = f"⚠️ OLD IMAGE REUSED: {explanation}"
            elif verdict == "FALSE_LOCATION":
                explanation = f"❌ FALSE LOCATION: {explanation}"
            elif verdict == "MISLEADING":
                explanation = f"⚠️ MISLEADING CONTEXT: {explanation}"
        
        print(f"✅ Verdict: {verdict} (confidence: {confidence:.0%})")
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "explanation": explanation,
            "fingerprint": fingerprint,
            "real_context": real_context,
            "claim_context": claim_context,
            "evidence": evidence[:5],  # top 5 sources
            "issues": issues
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "explanation": f"Verification failed: {str(e)}",
            "error": str(e)
        }
