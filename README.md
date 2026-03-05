# 💼 FinanceBase — Student Finance Learning Website

A beginner-friendly finance learning website with an AI tutor powered by Groq (free & fast).

## 🚀 Run Locally

### 1. Get a free Groq API Key
Go to [console.groq.com](https://console.groq.com) → Sign up → API Keys → Create key
(It's free — no credit card needed)

### 2. Set your API key

**Recommended (persistent): create a `.env` file in this folder**
```env
GROQ_API_KEY=gsk_your_key_here
```

`server.py` now auto-loads this value.

**Mac / Linux:**
```bash
export GROQ_API_KEY=gsk_your_key_here
```

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=gsk_your_key_here
```

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="gsk_your_key_here"
```

### 3. Start the server
```bash
python server.py
```

### 4. Open the site
Visit **http://localhost:8080** ✅

---

## 📁 Project Structure
```
financebase/
├── index.html    # The full website
├── server.py     # Backend — keeps API key safe
└── README.md     # This file
```

## 🤖 Switching Models
Edit the `MODEL` variable in `server.py`:
| Model | Best for |
|---|---|
| `llama-3.3-70b-versatile` | Best quality (default) |
| `llama-3.1-8b-instant` | Fastest responses |
| `mixtral-8x7b-32768` | Long detailed answers |

## ❓ Why server.py?
Your API key must never go in the HTML — anyone could steal it.
`server.py` sits between your browser and Groq, keeping the key on your machine only.

## 📄 License
MIT
