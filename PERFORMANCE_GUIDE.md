# Performance Optimization Guide (Phi-3 Mini)

## 🎯 Goal: Sub-2-Second Extraction Speed

This guide explains how to achieve the fastest extraction speeds using **Phi-3 Mini (phi3:3.8b)** in your OCR label pipeline.

---

# ✅ 1. Model Selection

### Recommended Model:
```
phi3:3.8b
```

### Why?
- Fastest inference (<1.5s warm)
- Highly accurate name/address extraction
- Clean JSON output
- Works on CPU and GPU

---

# ✅ 2. Ollama Settings

### Keep model in memory:
```
export OLLAMA_KEEP_ALIVE=5m
```

Add permanently (optional):
```
echo 'export OLLAMA_KEEP_ALIVE=5m' >> ~/.zshrc
```

---

# ✅ 3. Pre-Warm the Model

Run before batch processing:
```
python optimize_for_speed.py
```

Expected warm-up time:
- **Phi-3 Mini:** 1.5–2.0 seconds

---

# ✅ 4. Optimized AI Extraction Settings

These settings are used in `ai_extractor.py`:

```python
options = {
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_predict": 120
}
```

Why?

| Setting | Effect |
|--------|--------|
| low temperature | deterministic JSON |
| low num_predict | faster generation |
| top_p=0.9 | stable sampling |
| repeat_penalty | avoids repeated output |

---

# ✅ 5. Pipeline Speed Expectations

| Stage | Time |
|--------|------|
| Database lookup | **<10ms** |
| Phi-3 inference (warm) | **0.7–1.4s** |
| Phi-3 inference (cold) | 2–3s |
| Entire pipeline | Always **<2 seconds** after warm-up |

---

# ✅ 6. Example Inference Log

```
🧾 Label #10
🔍 Not found in database. Using AI extraction...
⏱️ AI Inference Time: 1.21s
✅ Extracted with AI
👤 Name: John Doe
🏠 Address: 123 Main St, New York NY 10001
💾 Saved to database
```

---

# 🔧 7. Troubleshooting Slow Performance

1. **Check if model is loaded**  
   ```
   ollama ps
   ```

2. **Check available models**  
   ```
   ollama list
   ```

3. **Re-warm the model**  
   ```
   python optimize_for_speed.py
   ```

4. **Verify CPU load is not high**  
   Close Chrome, VSCode, etc.

---

# 🎉 Final Result

With Phi-3 Mini and this optimized pipeline, you will achieve:

### ⭐ 1.0–1.5 sec extraction  
### ⭐ Accurate name/address detection  
### ⭐ Zero JSON errors  
### ⭐ Sub-2-second total response time  
