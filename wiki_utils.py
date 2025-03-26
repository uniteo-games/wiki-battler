import requests
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup
from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import base64

IMAGE_SIZE = 256  # 正方形のサイズ

def extract_lang_from_url(url):
    parts = url.split("//")[1].split(".")
    return parts[0] if len(parts) > 0 else "en"

def get_page_title(url):
    return unquote(url.split("/")[-1])

def get_article_text(title, lang="ja"):
    try:
        url = f"https://{lang}.wikipedia.org/w/api.php?action=parse&page={quote(title)}&format=json&prop=text&formatversion=2"
        res = requests.get(url)
        if res.status_code == 200:
            html = res.json()["parse"]["text"]
            soup = BeautifulSoup(html, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            return text
    except Exception as e:
        print("[記事取得エラー]", e)
    return ""

def get_first_image(title, lang):
    try:
        # REST API
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if "thumbnail" in data and "source" in data["thumbnail"]:
                return data["thumbnail"]["source"]
    except:
        pass

    # HTML fallback
    try:
        html_url = f"https://{lang}.wikipedia.org/wiki/{quote(title)}"
        res = requests.get(html_url)
        soup = BeautifulSoup(res.text, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = f"https://{lang}.wikipedia.org" + src
                if src.endswith((".jpg", ".jpeg", ".png")):
                    return src
    except:
        pass

    return None

def download_image(url):
    try:
        headers = { "User-Agent": "WikiBattleApp/1.0" }
        res = requests.get(url, headers=headers, timeout=10)
        content_type = res.headers.get("Content-Type", "").lower()
        if "image" not in content_type:
            raise ValueError("Not an image")
        img_data = BytesIO(res.content)
        img_data.seek(0)
        img = Image.open(img_data).convert("RGB")
        return img
    except Exception as e:
        print("[画像取得エラー]:", e)
        return None

def crop_to_square(img):
    w, h = img.size
    scale = IMAGE_SIZE / min(w, h)
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    w, h = img.size
    left = (w - IMAGE_SIZE) // 2
    top = (h - IMAGE_SIZE) // 2
    img = img.crop((left, top, left + IMAGE_SIZE, top + IMAGE_SIZE))
    return img

def image_to_base64(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def create_placeholder_image(char="？"):
    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), color=(255, 255, 100))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    w, h = draw.textbbox((0, 0), char, font=font)[2:]
    draw.text(((IMAGE_SIZE - w) / 2, (IMAGE_SIZE - h) / 2), char, font=font, fill=(0, 0, 0))
    return img

def darken_and_grayscale(img):
    gray = img.convert("L").convert("RGB")
    enhancer = ImageEnhance.Brightness(gray)
    dark = enhancer.enhance(0.5)
    return dark

def red_flash_image(img):
    red_overlay = Image.new("RGB", img.size, (255, 0, 0))
    return Image.blend(img, red_overlay, 0.4)

def add_yellow_border(img, thickness=6):
    return ImageOps.expand(img, border=thickness, fill=(255, 255, 0))

def fetch_wiki_content(url):
    lang = extract_lang_from_url(url)
    title = get_page_title(url)
    text = get_article_text(title, lang)
    return lang, title, text

def get_processed_image(title, lang):
    img_url = get_first_image(title, lang)
    if img_url:
        img = download_image(img_url)
        if img:
            return crop_to_square(img)
    # 画像取得に失敗した場合はタイトルの最初の文字を画像に
    fallback_char = title[0] if title else "？"
    return create_placeholder_image(fallback_char)

def get_special_moves(title, lang):
    """
    記事内のリンク付きテキストから10番目～25番目までを必殺技候補として取得。
    候補が足りない場合は「気合」を追加。
    """
    try:
        html_url = f"https://{lang}.wikipedia.org/wiki/{quote(title)}"
        res = requests.get(html_url)
        soup = BeautifulSoup(res.text, "html.parser")
        all_links = []

        for a in soup.find_all("a", href=True):
            if a.text.strip() and not a["href"].startswith("#") and ":" not in a["href"]:
                all_links.append(a.text.strip())

        # 10番目以降25番目以内をスライス
        special_moves = all_links[9:25]  # 10番目～25番目（0-indexed）

        if len(special_moves) < 1:
            special_moves.append("気合")

        return special_moves
    except Exception as e:
        print("[必殺技候補の取得エラー]:", e)
        return ["気合"]

def format_stats(stats):
    """体力を除いたステータスを整形"""
    return "\n".join([f"{k}: {v}" for k, v in stats.items() if k != "体力"])
