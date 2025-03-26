import random
import time
from wiki_utils import red_flash_image, darken_and_grayscale

# ステータス生成（テキスト量・記号・リンク数などに応じて）
def generate_stats(text, page=None):
    length = len(text)
    comma_period = text.count("、") + text.count("。")
    links = text.count("[[") if "[[" in text else 0

    stats = {
        "攻撃力": min(300, 30 + length // 120),
        "防御力": min(300, 20 + comma_period),
        "素早さ": max(10, 150 - (length // 100)),
        "読みの力": min(300, 10 + links * 5),
        "人気度": min(300, 10 + text.count("の") + text.count("は")),
        "体力": min(1000, 400 + length // 5 + (20 + comma_period) // 2),
    }
    return stats

# バトル1ターンの処理
def battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events, special_moves):
    # 必殺技チャンス
    if special_moves and random.randint(1, 20) == 1:  # 出現率 1/20
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
