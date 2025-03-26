import random
import time
from wiki_utils import red_flash_image, darken_and_grayscale
import math


# ステータス生成（テキスト量・記号・リンク数などに応じて）
def generate_stats(article_text: str, max_hp: int = 1000) -> dict:
    text_length = len(article_text)
    word_count = len(article_text.split())
    link_count = article_text.count("[[")  # ※後で正確なリンク数に置き換え可
    link_density = link_count / word_count if word_count else 0

    base_hp = min(max_hp, 500 + int(math.sqrt(text_length)) // 2)
    attack = min(100, max(10, 20 + int(link_count ** 0.5) + (text_length % 7)))
    defense = min(100, max(5, 15 + int(link_density * 100)))
    speed = min(150, max(20, 100 - int(text_length ** 0.3)))
    intuition = min(100, max(10, 20 + int(link_density * 80)))
    popularity = min(100, max(10, 100 - int(link_count * 0.2)))

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
    if random.randint(1, 100) <= def_stats["素早さ"] // 2:
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
