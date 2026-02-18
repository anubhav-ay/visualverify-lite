"""
VisualVerify Lite - Simple image verification API
Runs on laptop without Docker, Celery, or heavy dependencies
"""
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
from dotenv import load_dotenv

from database.models import VerificationJob, ImageCache, get_db
from phases.verify import verify_image

# Load API keys from .env (optional)
load_dotenv()
API_KEYS = {
    "SERPAPI_KEY": os.getenv("SERPAPI_KEY"),
    "BING_API_KEY": os.getenv("BING_API_KEY"),
}

app = FastAPI(
    title="VisualVerify Lite",
    description="Lightweight image misinformation detection - works on laptop!",
    version="1.0.0"
)

# Request/Response models
class VerifyRequest(BaseModel):
    image_url: HttpUrl
    user_claim: Optional[str] = None

class VerifyResponse(BaseModel):
    job_id: int
    status: str
    message: str

# ─────────────────────────────────────────────────────────────────────────────

def run_verification(job_id: int, image_url: str, user_claim: str):
    """Background task - runs verification"""
    db = next(get_db())
    job = db.query(VerificationJob).filter_by(id=job_id).first()
    
    try:
        # Check cache first
        if job.image_url:
            import hashlib
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:16]
            cached = db.query(ImageCache).filter_by(image_hash=url_hash).first()
            if cached:
                print(f"💾 Cache hit! {url_hash}")
                job.verdict = cached.verdict
                job.confidence = cached.confidence
                job.explanation = f"[CACHED] {cached.explanation}"
                job.status = "COMPLETED"
                job.completed_at = datetime.utcnow()
                db.commit()
                return
        
        # Run verification
        result = verify_image(image_url, user_claim, API_KEYS)
        
        # Update job
        job.status = "COMPLETED"
        job.verdict = result.get("verdict")
        job.confidence = result.get("confidence")
        job.explanation = result.get("explanation")
        job.evidence = result.get("evidence")
        job.real_context = result.get("real_context")
        job.claim_context = result.get("claim_context")
        job.completed_at = datetime.utcnow()
        
        # Save to cache
        if result.get("fingerprint"):
            cache_entry = ImageCache(
                image_hash=result["fingerprint"]["md5"][:32],
                phash=result["fingerprint"]["phash"],
                verdict=result["verdict"],
                confidence=result["confidence"],
                explanation=result["explanation"]
            )
            db.merge(cache_entry)
        
        db.commit()
        print(f"✅ Job {job_id} completed: {result['verdict']}")
        
    except Exception as e:
        job.status = "FAILED"
        job.explanation = f"Error: {str(e)}"
        db.commit()
        print(f"❌ Job {job_id} failed: {e}")
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home():
    """Simple web UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VisualVerify Lite</title>
        <style>
            body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2563eb; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #1d4ed8; }
            .result { background: #f3f4f6; padding: 20px; border-radius: 8px; margin-top: 20px; display: none; }
            .verdict { font-size: 24px; font-weight: bold; margin: 10px 0; }
            .TRUE { color: #059669; }
            .FALSE, .FALSE_LOCATION { color: #dc2626; }
            .RECYCLED, .MISLEADING { color: #d97706; }
            .UNVERIFIED { color: #6b7280; }
        </style>
    </head>
    <body>
        <h1>🔍 VisualVerify Lite</h1>
        <p>Lightweight image misinformation detector - runs on your laptop!</p>
        
        <input type="text" id="imageUrl" placeholder="Image URL (e.g. https://example.com/image.jpg)" />
        <textarea id="claim" rows="3" placeholder="User claim (optional) - e.g. 'Flooding in Turkey 2024'"></textarea>
        <button onclick="verify()">Verify Image</button>
        
        <div id="result" class="result"></div>
        
        <script>
        async function verify() {
            const url = document.getElementById('imageUrl').value;
            const claim = document.getElementById('claim').value;
            
            if (!url) { alert('Please enter image URL'); return; }
            
            document.getElementById('result').innerHTML = '<p>⏳ Analyzing...</p>';
            document.getElementById('result').style.display = 'block';
            
            try {
                // Submit job
                const submitResp = await fetch('/verify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({image_url: url, user_claim: claim})
                });
                const submitData = await submitResp.json();
                const jobId = submitData.job_id;
                
                // Poll for result
                let attempts = 0;
                const poll = setInterval(async () => {
                    attempts++;
                    const resultResp = await fetch(`/result/${jobId}`);
                    const result = await resultResp.json();
                    
                    if (result.status === 'COMPLETED') {
                        clearInterval(poll);
                        displayResult(result);
                    } else if (result.status === 'FAILED' || attempts > 20) {
                        clearInterval(poll);
                        document.getElementById('result').innerHTML = 
                            '<p style="color:red">❌ Verification failed</p>';
                    }
                }, 2000);
                
            } catch (err) {
                document.getElementById('result').innerHTML = 
                    '<p style="color:red">❌ Error: ' + err.message + '</p>';
            }
        }
        
        function displayResult(job) {
            const html = `
                <div class="verdict ${job.verdict}">${job.verdict}</div>
                <p><strong>Confidence:</strong> ${Math.round(job.confidence * 100)}%</p>
                <p><strong>Explanation:</strong><br>${job.explanation}</p>
                ${job.evidence && job.evidence.length > 0 ? `
                    <details style="margin-top:15px">
                        <summary><strong>Evidence Sources (${job.evidence.length})</strong></summary>
                        <ul>
                        ${job.evidence.map(e => `<li><a href="${e.url}" target="_blank">${e.title || e.url}</a></li>`).join('')}
                        </ul>
                    </details>
                ` : ''}
            `;
            document.getElementById('result').innerHTML = html;
        }
        </script>
    </body>
    </html>
    """

@app.post("/verify", response_model=VerifyResponse)
def submit_verification(request: VerifyRequest, background_tasks: BackgroundTasks):
    """Submit image for verification - returns immediately"""
    db = next(get_db())
    
    # Create job
    job = VerificationJob(
        image_url=str(request.image_url),
        user_claim=request.user_claim,
        status="PROCESSING"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Run in background
    background_tasks.add_task(
        run_verification,
        job.id,
        str(request.image_url),
        request.user_claim
    )
    
    return VerifyResponse(
        job_id=job.id,
        status="PROCESSING",
        message=f"Verification started. Check /result/{job.id}"
    )

@app.get("/result/{job_id}")
def get_result(job_id: int):
    """Get verification result"""
    db = next(get_db())
    job = db.query(VerificationJob).filter_by(id=job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "verdict": job.verdict,
        "confidence": job.confidence,
        "explanation": job.explanation,
        "evidence": job.evidence,
        "real_context": job.real_context,
        "claim_context": job.claim_context,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }

@app.get("/health")
def health():
    return {"status": "ok", "api_keys_configured": bool(API_KEYS.get("SERPAPI_KEY"))}

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting VisualVerify Lite...")
    print("📱 Open: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
