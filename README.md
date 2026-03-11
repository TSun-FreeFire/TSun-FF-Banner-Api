<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:020617,50:0891b2,100:22d3ee&height=200&section=header&text=TSun%20Banner%20Api&fontSize=52&fontColor=ffffff&fontAlignY=38&desc=Free%20Fire%20%E2%80%A2%20Real-Time%20Banner%20Generator&descSize=16&descAlignY=60&animation=fadeIn" width="100%"/>

<br/>

[![Deploy](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://banner.tsunstudio.pw/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-22d3ee?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Online-4ade80?style=for-the-badge&logo=statuspage&logoColor=white)](https://banner.tsunstudio.pw/health)

<br/>

> **Generate pixel-perfect Free Fire profile banner PNGs from any UID — no API key, no login, one request.**

</div>

---

## ✦ Preview

<div align="center">
<img src="https://banner.tsunstudio.pw/profile?uid=2513698016" alt="Banner Preview" width="80%" style="border-radius:12px"/>
<br/><sub>↑ Live output from <code>GET /profile?uid=2513698016</code></sub>
</div>

---

## ✦ What Is This?

**TSun Banner Api** is a lightweight, zero-auth REST API that fetches a Free Fire player's profile data and renders it into a ready-to-use **PNG banner image** — combining the player's equipped banner, avatar, name, level, and guild — all in real time.

```
Player UID  ──►  Free Fire Data  ──►  PIL Renderer  ──►  PNG Response
```

- ⚡ Single GET request — no JSON parsing on your end  
- 🎨 Renders equipped banner + avatar + name + guild + level  
- 🔤 Full Unicode support (Cherokee, Tibetan, Canadian Aboriginal, and more)  
- 🌐 Deployed on Vercel — globally available, zero cold-start penalty  
- 🔓 No API key or authentication required  

---

## ✦ Quick Start

### cURL
```bash
curl -X GET "https://banner.tsunstudio.pw/profile?uid=YOUR_UID" \
  --output banner.png
```

### Python
```python
import requests

r = requests.get(
    "https://banner.tsunstudio.pw/profile",
    params={"uid": "7741399252"}
)
with open("banner.png", "wb") as f:
    f.write(r.content)
```

### Node.js
```js
const fs = require("fs");
const https = require("https");

const uid = "7741399252";
https.get(
  `https://banner.tsunstudio.pw/profile?uid=${uid}`,
  (res) => res.pipe(fs.createWriteStream("banner.png"))
);
```

---

## ✦ API Reference

### `GET /profile`

Generates a Free Fire profile banner PNG.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uid` | `string` | ✅ Yes | Free Fire player UID (numeric) |
| `banner` | `string` | ❌ No | Override banner asset ID — 9 digits, starts with `901` |
| `avatar` | `string` | ❌ No | Override avatar asset ID — 9 digits, starts with `902` |

**Response:** `image/png` — ready to embed, download, or display.

```
200 OK          → PNG image
400 Bad Request → Invalid UID or override ID format
404 Not Found   → Player not found
502 Bad Gateway → Upstream data error
500 Error       → Internal rendering error
```

**Example with overrides:**
```
GET /profile?uid=7741399252&banner=901000011&avatar=902000007
```

---

### `GET /health`

Returns live system status.

```json
{
  "status": "ok",
  "service": "TSun Banner Api",
  "version": "2.6.0",
  "uptime": "1h 23m 45s",
  "uptime_seconds": 5025,
  "banners_rendered": 142,
  "python": "3.12.2",
  "environment": "production"
}
```

---

### `GET /`

Serves the **TSun Banner Api** web frontend — a live interactive banner tester with a terminal boot screen, code docs, and endpoint reference.

---

## ✦ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-PIL-ffb86c?style=flat-square)
![HTTPX](https://img.shields.io/badge/HTTPX-async-22d3ee?style=flat-square)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![GSAP](https://img.shields.io/badge/GSAP-88CE02?style=flat-square&logo=greensock&logoColor=black)

</div>

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| Image Rendering | Pillow (PIL) |
| HTTP Client | HTTPX (async) |
| Font Parsing | FontTools |
| Frontend | Tailwind CSS + GSAP |
| Deployment | Vercel (Serverless) |

---

## ✦ Run Locally

**1. Clone**
```bash
git clone https://github.com/TSun-FreeFire/TSun-FF-Banner-Api.git
cd TSun-FF-Banner-Api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run**
```bash
python app.py
```

API is now live at `http://127.0.0.1:5000`

**Test it:**
```bash
curl "http://127.0.0.1:5000/profile?uid=YOUR_UID" --output banner.png
```

---

## ✦ Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/TSun-FreeFire/TSun-FF-Banner-Api)

The repo includes a pre-configured `vercel.json` — just connect the repo and deploy.

---

## ✦ Project Structure

```
TSun-FF-Banner-Api/
│
├── app.py              # FastAPI application — routes, renderer, lifespan
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel serverless deployment config
│
├── fonts/              # Unicode font files
│   ├── arial_unicode_bold.otf
│   ├── NotoSansCherokee.ttf
│   ├── NotoSansCanadianAboriginal-Regular.ttf
│   ├── NotoSerifTibetan-Regular.ttf
│   └── SansSerifCollection.ttf
│
└── static/
    └── index.html      # Frontend — live banner tester UI
```

---

## ✦ How The Renderer Works

```
1.  Fetch player data    →  GET {INFO_API}/{uid}
2.  Fetch assets         →  Avatar PNG + Banner PNG + Title PIN (parallel)
3.  Composite image      →  PIL: avatar (325×315) + banner (1145×315) = 1470×315
4.  Draw text            →  Name, Guild, Level — multi-font Unicode rendering
5.  Return PNG           →  image/png  Cache-Control: public, max-age=300
```

**Unicode font fallback chain:**

```
Cherokee ──► Canadian Aboriginal ──► Tibetan ──► SansSerif Collection ──► Arial Unicode Bold
```

Every character is checked against each font's cmap before rendering — no missing-glyph boxes.

---

## ✦ Endpoints At A Glance

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web frontend (banner tester UI) |
| `GET` | `/profile?uid=` | Generate banner PNG |
| `GET` | `/health` | System status & uptime |
| `GET` | `/favicon.ico` | Favicon (Free Fire icon) |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:22d3ee,50:0891b2,100:020617&height=100&section=footer&reversal=false" width="100%"/>

<sub>Made with ❤️ by <a href="https://github.com/TSun-FreeFire">TSun-FreeFire</a> · Powered by FastAPI & 𝙎ค૯𝙀𝘿✘🫀</sub>

</div>
