# 🚀 Quick Start Guide – OCR Label Extractor (Phi-3 Mini 3.8B)

This guide helps you run the OCR label extraction system **fast** with **high accuracy** using **Phi-3 Mini (phi3:3.8b)** via Ollama.

The system extracts:
- 👤 Recipient Name  
- 🏠 Full Postal Address  
from raw OCR text.

Results are automatically saved in `ocr_labels.db` for instant future lookups.

---

# ✅ 1. System Requirements

**You need:**
- Python 3.8+
- Ollama installed → https://ollama.com
- macOS / Linux / Windows (WSL works)
- 4GB+ RAM (Phi-3 Mini fits easily)

---

# 🔧 2. Install & Pull Phi-3 Mini

### Install Ollama (if not already):
```
brew install ollama
```
or download from the website.

### Start Ollama:
```
ollama serve
```

### Pull Phi-3 Mini model (only once):
```
ollama pull phi3:3.8b
```

This downloads the model into local storage.

---

# 💻 3. Create & Activate Virtual Environment

```
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

Install Python dependencies:
```
pip install -r requirements.txt
```

---

# ⚡ 4. (Recommended) Keep Model Loaded in Memory

This avoids slow cold-start times.

```
export OLLAMA_KEEP_ALIVE=5m
```

To make it permanent (macOS):
```
echo 'export OLLAMA_KEEP_ALIVE=5m' >> ~/.zshrc
source ~/.zshrc
```

---

# 🔥 5. Pre-Warm Phi-3 Mini (Optional but FASTEST)

This ensures all future calls run in **under 2 seconds**.

```
python optimize_for_speed.py
```

Expected:
```
Pre-warm done. Time: ~1.5s
```

---

# 📦 6. Run the Full Pipeline (CSV Processing)

```
python main.py --batch
```

The system will:
1. Read `ocr_raw_labels.csv`
2. Check each row against database
3. Use AI if missing → extract name + address
4. Save into SQLite DB
5. Write final results into `ocr_structured_output.csv`

---

# 💬 7. Run Manually (Interactive Mode)

```
python main.py
```

Example:
```
Would you like to enter raw OCR text manually? (y/n): y
Enter raw text: Ship To: John Doe, 2501 Main St, Austin TX 78701
```

Output:
```
🔍 Not found in database. Using AI extraction...
⏱️ AI Inference Time: 1.12s
👤 Recipient Name: John Doe
🏠 Address: 2501 Main St, Austin TX 78701
📍 Source: AI
```

---

# 👀 8. Watch for CSV Changes (Automation)

To auto-run pipeline whenever `ocr_raw_labels.csv` changes:

```
python watch_data_changes.py
```

Real-time updates for new/edited raw text.

---

# 📁 9. Project Structure

```
ocr_label_phi3/
├── ai_extractor.py
├── data_pipeline.py
├── db_manager.py
├── import_ollama.py
├── main.py
├── optimize_for_speed.py
├── setup_model.py
├── test_performance.py
├── watch_data_changes.py
├── start.sh
├── requirements.txt
├── ocr_raw_labels.csv
├── ocr_structured_output.csv
├── ocr_labels.db
├── README.md
├── QUICK_START.md
├── PERFORMANCE_GUIDE.md
├── CHANGES_SUMMARY.md
```

---

# 🔥 10. Expected Speed

| Stage | Time |
|-------|------|
| Database lookup | <10ms |
| Phi-3 Mini AI extraction (warm) | **0.7–1.4 seconds** |
| Cold start | 2–3 seconds |
| Entire pipeline | **<2 seconds** after warm-up |

---

# 🧠 11. Troubleshooting

### ❌ AI taking more than 3 seconds?
Run:
```
python optimize_for_speed.py
```
and ensure:
```
export OLLAMA_KEEP_ALIVE=5m
```

### ❌ Ollama not reachable?
Start:
```
ollama serve
```

### ❌ Wrong JSON or empty fields?
Phi-3 Mini is stable — but check OCR text quality.

---

# 🎉 Final Notes

You now have:
- Ultra-fast (<2 sec) extraction  
- High accuracy  
- Clean JSON parsing  
- Automatic saving to database  
- Reusable extraction pipeline  

You’re ready to process any OCR shipping label!

Happy coding! 🚀
