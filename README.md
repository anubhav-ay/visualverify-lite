# VisualVerify Lite 🚀

**Laptop pe chalega** - No Docker, No Complex Setup!

Image misinformation detector jo easily **Windows/Mac/Linux** pe run hoga.

---

## ✨ Features

- ✅ **Single command start** - `python main.py`
- ✅ **SQLite database** - No PostgreSQL setup needed
- ✅ **Works without API keys** - Optional better results with APIs
- ✅ **Simple Web UI** - Browser me kholo aur verify karo
- ✅ **Light weight** - ~50MB total with dependencies
- ✅ **Cache system** - Same image dubara instantly return hoga

---

## 📦 Installation

### Step 1: Python install karo (3.9+)
```bash
python --version  # Check karo, should be 3.9+
```

### Step 2: Dependencies install karo
```bash
pip install -r requirements.txt
```

Bas! 2 minutes me ready.

---

## 🚀 Start Karo

```bash
python main.py
```

Output:
```
🚀 Starting VisualVerify Lite...
📱 Open: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
```

Browser me `http://localhost:8000` kholo.

---

## 🔑 API Keys (Optional - Better Results)

Free API keys:
1. **SerpAPI** (Google reverse image search): https://serpapi.com - 100 searches/month free
2. **Bing API** (News search): https://azure.microsoft.com/products/ai-services/bing-search - 1000 calls/month free

Keys milne ke baad:
```bash
cp .env.example .env
nano .env  # ya koi editor me API keys paste karo
```

**Bina API keys ke bhi basic verification chalega!**

---

## 📖 How to Use

### Web UI (Easiest)
1. Open: http://localhost:8000
2. Image URL daalo
3. Claim daalo (optional)
4. "Verify Image" click karo
5. Wait 5-10 seconds → Result milega

### API (For developers)
```bash
# Submit verification
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/viral-image.jpg",
    "user_claim": "Flooding in Turkey 2024"
  }'

# Response: {"job_id": 1, "status": "PROCESSING"}

# Get result
curl http://localhost:8000/result/1
```

---

## 🎯 Example Test Cases

Try these viral misinformation cases:

1. **Old Flood Image as New Event**
   - URL: Any Bangladesh 2017 flood image
   - Claim: "Turkey earthquake 2024"
   - Expected: RECYCLED verdict

2. **Wrong Location**
   - URL: Syria war image
   - Claim: "Ukraine conflict"
   - Expected: FALSE_LOCATION

3. **Legitimate Image**
   - URL: Recent news photo
   - Claim: Matching description
   - Expected: TRUE or UNVERIFIED (depending on sources)

---

## 📊 Verdicts Explained

| Verdict | Matlab |
|---------|--------|
| **TRUE** | Image aur claim match kar rahe hain |
| **RECYCLED** | Purani image ko naya event bata rahe hain |
| **FALSE_LOCATION** | Galat location claim |
| **MISLEADING** | Real image, galat context |
| **UNVERIFIED** | Confirm nahi kar sake |
| **ERROR** | Technical error (invalid URL, etc) |

---

## 🗂 File Structure

```
visualverify-lite/
├── main.py              ← FastAPI app (start here)
├── requirements.txt     ← Dependencies
├── .env.example         ← API keys template
│
├── database/
│   └── models.py        ← SQLite models
│
├── phases/
│   └── verify.py        ← Core verification logic
│
└── services/
    └── image_analyzer.py ← Image processing functions

# Auto-generated files:
├── verify.db            ← SQLite database (created on first run)
```

---

## 💡 System Requirements

- **RAM:** 2GB minimum
- **Disk:** 200MB for dependencies + database
- **Internet:** Required for image download + optional APIs
- **OS:** Windows 10+, macOS 10.14+, or Linux

---

## 🐛 Common Issues

### Port 8000 already in use?
```bash
python main.py --port 8001  # Different port use karo
```

### PIL/Image errors?
```bash
pip install --upgrade pillow
```

### SQLite errors?
```bash
rm verify.db  # Delete database and restart
```

---

## 🚀 Production Tips

For production deployment:
1. Use proper API keys (not free tier)
2. Add rate limiting
3. Use Gunicorn instead of uvicorn:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
4. Add nginx reverse proxy
5. Set up SSL certificate

---

## 📝 How It Works

```
1. Download image → Calculate hashes (MD5, pHash)
2. Check cache → Return instant if seen before
3. Search evidence:
   - Google reverse image (if API key)
   - Bing news search (if API key)
4. Extract context:
   - Dates (YYYY format, "January 2024")
   - Locations (capitalized words)
   - Events (flood, earthquake, etc)
5. Compare real vs claimed context
6. Generate verdict + explanation
7. Cache result for future
```

**No ML training, no heavy models** - just smart heuristics!

---

## 🤝 Contributing

Issues/PRs welcome! Keep it **simple** and **lightweight**.

## 📄 License

MIT - Free to use anywhere
