import io
import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await client.aclose()
    process_pool.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

INFO_API_URL = "https://tsun-ff-infoxvisits.onrender.com/info"
FONT_FILE = "arial_unicode_bold.otf"
FONT_CHEROKEE = "NotoSansCherokee.ttf"
FONT_CANADIAN_ABORIGINAL = "NotoSansCanadianAboriginal-Regular.ttf"
FONT_TIBETAN = "NotoSerifTibetan-Regular.ttf"

client = httpx.AsyncClient(
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=10.0,
    follow_redirects=True
)

process_pool = ThreadPoolExecutor(max_workers=4)

def load_unicode_font(size, font_file=FONT_FILE):
    try:
        font_path = os.path.join(os.path.dirname(__file__), font_file)
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
    font_small = load_unicode_font(GUILD_H)
    font_small_cherokee = load_unicode_font(GUILD_H, FONT_CHEROKEE)
    font_small_canadian = load_unicode_font(GUILD_H, FONT_CANADIAN_ABORIGINAL)
    font_small_tibetan = load_unicode_font(GUILD_H, FONT_TIBETAN)
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

    def resolve_font(char, font_main, font_cherokee, font_canadian, font_tibetan):
        if is_cherokee(char):
            return font_cherokee
        if is_canadian_aboriginal(char):
            return font_canadian
        if is_tibetan(char):
            return font_tibetan
        return font_main

    def draw_text_with_stroke(x, y, text, font_main, font_cherokee, font_canadian, font_tibetan, size):
        current_x = x
        for char in text:
            font = resolve_font(char, font_main, font_cherokee, font_canadian, font_tibetan)
            for dx in range(-size, size + 1):
                for dy in range(-size, size + 1):
                    draw.text((current_x + dx, y + dy), char, font=font, fill=stroke_col)
            draw.text((current_x, y), char, font=font, fill=text_col)
            current_x += font.getlength(char)

    stroke_col, text_col = "black", "white"
    draw_text_with_stroke(NAME_X, NAME_Y, name, font_large, font_large_cherokee, font_large_canadian, font_large_tibetan, 4)
    draw_text_with_stroke(GUILD_X, GUILD_Y, guild, font_small, font_small_cherokee, font_small_canadian, font_small_tibetan, 3)

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

@app.get("/")
async def home():
    return {"message": "⚡ Ultra Fast Banner API Running",
           "Fix By": "TSun × Kittens",
           "Telegram": "@saeedxdie",
           "Your Info Api": INFO_API_URL,
           "Api Endpoint": "/profile?uid={uid}",
           "Note": "Join To @TSun_FreeFire For More 💝"
    }

@app.get("/profile")
async def get_banner(uid: str):
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
        
        avatar_task = fetch_image_bytes(equipped_items.get("EquippedAvatarId"))
        banner_task = fetch_image_bytes(equipped_items.get("EquippedBannerId"))
        
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
        
        return Response(content=img_io.getvalue(), media_type="image/png", headers={"Cache-Control": "public, max-age=300"})

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
