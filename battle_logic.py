import random
import time
from wiki_utils import red_flash_image, darken_and_grayscale
import math
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote

def get_link_count(title, lang="ja"):
    """
    Wikipediaの記事本文に含まれるリンク数を返す
    """
    try:
        url = f"https://{lang}.wikipedia.org/wiki/{quote(title)}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        body = soup.find("div", {"id": "bodyContent"})  # 本文エリアに限定
        links = body.find_all("a", href=True) if body else []
        return len(links)
    except Exception as e:
        print("[リンク数取得エラー]:", e)
        return 0

# ステータス生成（テキスト量・記号・リンク数などに応じて）
def generate_stats(article_text: str, title: str, lang: str, max_hp: int = 1000) -> dict:
    text_length = len(article_text)
    word_count = article_text.count("。") + article_text.count("、")

    link_count = get_link_count(title, lang)
    link_density = link_count / word_count if word_count else 0

    base_hp = min(max_hp, 500 + int(math.sqrt(text_length)) // 2)
    attack = min(300, max(10, 30 + int(math.log(link_count + 1) * 25)))
    defense = min(200, max(10, int((link_density ** 0.5) * 80)))
    speed = min(150, max(20, 100 - int(text_length ** 0.3)))
        # 読みの力（リンク密度が高いほど下がる）
    link_density = link_count / word_count if word_count else 0
    
# 安定的に広いレンジに分布させる式
    raw_intuition = 1 / (1 + link_density)  # リンク密度が高いほど読みが弱い（逆相関）
    intuition_score = int(raw_intuition * 120)  # 拡大係数を調整
    intuition = min(100, max(5, intuition_score))


    #popularity = min(500, max(10, int(link_count * 1.5)))  # リンク数に比例して人気度を上げる
    popularity = int(link_count * 0.15)  # リンク数に比例して人気度を上げる

    return {
        "攻撃力": attack,
        "防御力": defense,
        "素早さ": speed,
        "読みの力": intuition,
        "人気度": popularity,
        "体力": base_hp
    }

# バトル1ターンの処理
def battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events, special_moves):
    # 必殺技チャンス
    special_move_chance = min(30, atk_stats["素早さ"] // 5)
    
    if special_moves and random.randint(1, 100) <= special_move_chance:
        technique = random.choice(special_moves)
        success_chance = min(90, (atk_stats["素早さ"] + atk_stats["読みの力"]) // 2)
        if random.randint(1, 100) <= success_chance:
            damage = int(atk_stats["攻撃力"] * 2.5)
            hp_dict[defender] = max(0, hp_dict[defender] - damage)
            events.append(f"{attacker}の必殺技『{technique}』がヒット！ 💥 {defender} に {damage} ダメージ！")
            return damage
        else:
            events.append(f"{attacker}の必殺技『{technique}』は外れた…")
            return 0

    # 通常攻撃処理
    dodge_chance = (def_stats["素早さ"] ** 1.2) / 10  # 成長はやや遅め
    if random.randint(1, 100) <= min(50, dodge_chance):  # 最大50%に制限
        events.append(f"💨 {defender} は素早さで攻撃を回避！")
        return 0

    base_damage = atk_stats["攻撃力"]
    if random.randint(1, 8) == 1:
        if random.randint(1, 100) <= def_stats["防御力"]:
            events.append(f"🛡 {defender} は完全防御に成功！ノーダメージ！")
            return 0
    elif random.randint(1, 100) <= def_stats["防御力"]:
        base_damage = base_damage // 2
        events.append(f"🛡 {defender} の防御力でダメージ半減！")

    hp_dict[defender] = max(0, hp_dict[defender] - base_damage)
    events.append(f"{attacker} が {defender} に {base_damage} ダメージ！")
    return base_damage

# 回復イベント
def check_heal(name, stats, hp_dict, log_lines):
    if random.randint(1, 10) == 1 and random.random() < stats['人気度'] / 300:
        heal = stats['人気度'] // 6
        hp_dict[name] = min(stats['体力'], hp_dict[name] + heal)
        log_lines.insert(1, f"💖 {name} は観客の声援で {heal} 回復した！")

# 画像処理
def process_image_for_hit(img):
    return red_flash_image(img)

def process_image_for_defeat(img):
    return darken_and_grayscale(img)
