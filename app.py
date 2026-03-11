import io
import os
import sys
import time
import asyncio
import httpx
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from fontTools.ttLib import TTFont

_START_TIME   = time.time()
_RENDER_COUNT = 0
client: httpx.AsyncClient = None  # type: ignore[assignment]  # set in lifespan
process_pool: ThreadPoolExecutor  = None  # type: ignore[assignment]  # set in lifespan

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global client, process_pool
    client = httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10.0,
        follow_redirects=True
    )
    process_pool = ThreadPoolExecutor(max_workers=4)
    yield
    await client.aclose()
    process_pool.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend assets
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

INFO_API_URL = "https://tsun-ff-infoxvisits.onrender.com/info"
FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONT_FILE = os.path.join(FONTS_DIR, "arial_unicode_bold.otf")
FONT_CHEROKEE = os.path.join(FONTS_DIR, "NotoSansCherokee.ttf")
FONT_CANADIAN_ABORIGINAL = os.path.join(FONTS_DIR, "NotoSansCanadianAboriginal-Regular.ttf")
FONT_TIBETAN = os.path.join(FONTS_DIR, "NotoSerifTibetan-Regular.ttf")
FONT_SANS_SERIF_COLLECTION = os.path.join(FONTS_DIR, "SansSerifCollection.ttf")

def _build_cmap(font_file):
    """Return the set of supported Unicode codepoints for a font file."""
    try:
        path = font_file
        if os.path.exists(path):
            tt = TTFont(path, lazy=True)
            cmap = tt.getBestCmap()
            if cmap:
                return set(cmap.keys())
    except Exception:
        pass
    return set()

_CMAP_MAIN         = _build_cmap(FONT_FILE)
_CMAP_CHEROKEE     = _build_cmap(FONT_CHEROKEE)
_CMAP_CANADIAN     = _build_cmap(FONT_CANADIAN_ABORIGINAL)
_CMAP_TIBETAN      = _build_cmap(FONT_TIBETAN)
_CMAP_SANS_SERIF   = _build_cmap(FONT_SANS_SERIF_COLLECTION)
_CMAP_ALL          = _CMAP_MAIN | _CMAP_CHEROKEE | _CMAP_CANADIAN | _CMAP_TIBETAN | _CMAP_SANS_SERIF

def load_unicode_font(size, font_file=FONT_FILE):
    try:
        font_path = font_file
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

async def fetch_image_bytes(item_id):
    if not item_id or str(item_id) == "0" or item_id is None:
        return None

    item_id = str(item_id)
    url = f"https://raw.githubusercontent.com/3ch0Byt3-1/Icons/refs/heads/main/icons/{item_id}.png"

    try:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.content
    except:
        pass
    return None

def bytes_to_image(img_bytes):
    if img_bytes:
        try:
            return Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        except Exception:
            pass
    return None

def process_banner_image(data, avatar_bytes, banner_bytes, pin_bytes):
    avatar_img = bytes_to_image(avatar_bytes) or Image.new('RGBA', (325, 315), (0, 0, 0, 0))
    banner_img = bytes_to_image(banner_bytes) or Image.new('RGBA', (1145, 315), (0, 0, 0, 0))
    banner_img = banner_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    pin_img    = bytes_to_image(pin_bytes)

    level = str(data.get("AccountLevel") or "0")
    name = str(data.get("AccountName") or "Unknown")
    guild = str(data.get("GuildName") or "")

    AVATAR_W, AVATAR_H = 325, 315
    BANNER_W, BANNER_H = 1145, 315
    FINAL_W, FINAL_H = 1470, 315

    avatar_img = avatar_img.resize((AVATAR_W, AVATAR_H), Image.Resampling.LANCZOS)
    banner_img = banner_img.resize((BANNER_W, BANNER_H), Image.Resampling.LANCZOS)

    combined = Image.new("RGBA", (FINAL_W, FINAL_H), (0, 0, 0, 0))
    combined.paste(avatar_img, (0, 0))
    combined.paste(banner_img, (AVATAR_W, 0))
    
    draw = ImageDraw.Draw(combined)

    # Layout positions
    NAME_X,  NAME_Y,  NAME_H,  NAME_W  = 396,  34,  95,  900
    GUILD_X, GUILD_Y, GUILD_H, GUILD_W = 396,  206, 70,  700
    LVL_X,   LVL_Y,  LVL_H,   LVL_W   = 1293, 249, 60,  170

    font_large = load_unicode_font(NAME_H)
    font_large_cherokee = load_unicode_font(NAME_H, FONT_CHEROKEE)
    font_large_canadian = load_unicode_font(NAME_H, FONT_CANADIAN_ABORIGINAL)
    font_large_tibetan = load_unicode_font(NAME_H, FONT_TIBETAN)
    font_large_sans_serif = load_unicode_font(NAME_H, FONT_SANS_SERIF_COLLECTION)
    font_small = load_unicode_font(GUILD_H)
    font_small_cherokee = load_unicode_font(GUILD_H, FONT_CHEROKEE)
    font_small_canadian = load_unicode_font(GUILD_H, FONT_CANADIAN_ABORIGINAL)
    font_small_tibetan = load_unicode_font(GUILD_H, FONT_TIBETAN)
    font_small_sans_serif = load_unicode_font(GUILD_H, FONT_SANS_SERIF_COLLECTION)
    font_level = load_unicode_font(LVL_H)

    def is_cherokee(char):
        code = ord(char)
        return (0x13A0 <= code <= 0x13FF) or (0xAB70 <= code <= 0xABBF)

    def is_canadian_aboriginal(char):
        code = ord(char)
        return 0x1400 <= code <= 0x167F

    def is_tibetan(char):
        code = ord(char)
        return 0x0F00 <= code <= 0x0FFF

    def resolve_font(char, font_main, font_cherokee, font_canadian, font_tibetan, font_sans_serif):
        if is_cherokee(char):
            return font_cherokee
        if is_canadian_aboriginal(char):
            return font_canadian
        if is_tibetan(char):
            return font_tibetan
        cp = ord(char)
        if cp > 127 and cp not in _CMAP_MAIN and cp in _CMAP_SANS_SERIF:
            return font_sans_serif
        return font_main

    def draw_text_with_stroke(x, y, text, font_main, font_cherokee, font_canadian, font_tibetan, font_sans_serif, size):
        current_x = x
        for char in text:
            # Skip characters not supported by any available font to avoid {box} glyphs
            if ord(char) > 127 and ord(char) not in _CMAP_ALL:
                continue
            font = resolve_font(char, font_main, font_cherokee, font_canadian, font_tibetan, font_sans_serif)
            for dx in range(-size, size + 1):
                for dy in range(-size, size + 1):
                    draw.text((current_x + dx, y + dy), char, font=font, fill=stroke_col)
            draw.text((current_x, y), char, font=font, fill=text_col)
            current_x += font.getlength(char)

    stroke_col, text_col = "black", "white"
    draw_text_with_stroke(NAME_X, NAME_Y, name, font_large, font_large_cherokee, font_large_canadian, font_large_tibetan, font_large_sans_serif, 4)
    draw_text_with_stroke(GUILD_X, GUILD_Y, guild, font_small, font_small_cherokee, font_small_canadian, font_small_tibetan, font_small_sans_serif, 3)

    if pin_img is not None:
        pin_size = 130
        pin_img = pin_img.resize((pin_size, pin_size), Image.Resampling.LANCZOS)
        combined.paste(pin_img, (0, FINAL_H - pin_size), pin_img)

    level_txt = f"Lvl.{level}"
    draw.text((LVL_X, LVL_Y), level_txt, font=font_level, fill="white")

    img_io = io.BytesIO()
    combined.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>TSun Banner Api</h1><p>Use <code>/profile?uid=YOUR_UID</code></p>")


@app.get("/health")
async def health():
    global _RENDER_COUNT
    uptime_seconds = round(time.time() - _START_TIME)
    days,    rem1      = divmod(uptime_seconds, 86400)
    hours,   rem2      = divmod(rem1, 3600)
    minutes, seconds   = divmod(rem2, 60)

    parts = []
    if days:    parts.append(f"{days}d")
    if hours:   parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    uptime_human = " ".join(parts)

    return JSONResponse({
        "status": "ok",
        "service": "TSun Banner Api",
        "version": "2.6.0",
        "uptime": uptime_human,
        "uptime_seconds": uptime_seconds,
        "banners_rendered": _RENDER_COUNT,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": os.getenv("APP_ENV", "production"),
    })


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Serve local file first
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.ico")
    if os.path.exists(favicon_path):
        with open(favicon_path, "rb") as f:
            return Response(content=f.read(), media_type="image/x-icon")
    # Fall back to Icons8 Free Fire icon (proxied so the browser gets it from our origin)
    try:
        r = await client.get(
            "https://img.icons8.com/?id=S82R0mhIAwEg&format=png&size=32",
            timeout=5.0
        )
        if r.status_code == 200:
            return Response(content=r.content, media_type="image/png",
                            headers={"Cache-Control": "public, max-age=86400"})
    except Exception:
        pass
    return Response(status_code=204)

def validate_avatar_id(avatar_id: str) -> int:
    if len(avatar_id) != 9 or not avatar_id.isdigit() or not avatar_id.startswith("902"):
        raise HTTPException(status_code=400, detail="Invalid avatar ID. Must be exactly 9 digits and start with 902 (e.g. 902000001)")
    return int(avatar_id)

def validate_banner_id(banner_id: str) -> int:
    if len(banner_id) != 9 or not banner_id.isdigit() or not banner_id.startswith("901"):
        raise HTTPException(status_code=400, detail="Invalid banner ID. Must be exactly 9 digits and start with 901 (e.g. 901000001)")
    return int(banner_id)

@app.get("/profile")
async def get_banner(uid: str, banner: Optional[str] = None, avatar: Optional[str] = None):
    if not uid:
        raise HTTPException(status_code=400, detail="UID required")

    try:
        resp = await client.get(f"{INFO_API_URL}/{uid}")
        
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Info API Error")
            
        data = resp.json()
        
        account_info = data.get("AccountInfo") or {}
        equipped_items = data.get("EquippedItemsInfo") or {}
        profile_info = data.get("AccountProfileInfo") or {}
        guild_info = data.get("GuildInfo") or {}
        
        if not account_info: raise HTTPException(status_code=404, detail="Not Found")
        
        avatar_id = validate_avatar_id(avatar) if avatar else (equipped_items.get("EquippedAvatarId") or 902000003)
        banner_id = validate_banner_id(banner) if banner else (equipped_items.get("EquippedBannerId") or 901000001)
        avatar_task = fetch_image_bytes(avatar_id)
        banner_task = fetch_image_bytes(banner_id)
        
        pin_id = profile_info.get("Title")
        pin_task = fetch_image_bytes(pin_id) if (pin_id and str(pin_id) != "0") else asyncio.sleep(0, result=None)

        results = await asyncio.gather(avatar_task, banner_task, pin_task)
        avatar_bytes  = results[0] or b''
        banner_bytes  = results[1] or b''
        pin_bytes     = results[2] or b''

        loop = asyncio.get_event_loop()
        banner_data = {
            "AccountLevel": account_info.get("AccountLevel") or "0",
            "AccountName": account_info.get("AccountName") or "Unknown",
            "GuildName": guild_info.get("GuildName") or ""
        }
        
        img_io = await loop.run_in_executor(
            process_pool, 
            process_banner_image, 
            banner_data, avatar_bytes, banner_bytes, pin_bytes
        )
        
        global _RENDER_COUNT
        _RENDER_COUNT += 1
        return Response(content=img_io.getvalue(), media_type="image/png", headers={"Cache-Control": "public, max-age=300"})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
