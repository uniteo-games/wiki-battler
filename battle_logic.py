import random
import time

# ステータス生成（テキスト量・記号・リンク数などに応じて）
def generate_stats(text, page=None):
    length = len(text)
    comma_period = text.count("、") + text.count("。")
    links = text.count("[[") if "[[" in text else 0  # テキスト中にリンク表記があれば

    stats = {
        "攻撃力": min(300, 30 + length // 120),
        "防御力": min(300, 20 + comma_period),
        "素早さ": max(10, 150 - (length // 100)),  # 長文はやや鈍く
        "読みの力": min(300, 10 + links * 5),
        "人気度": min(300, 10 + text.count("の") + text.count("は")),
    }

    # 体力（HP）は文字量に比例＋防御力の一部加算
    stats["体力"] = min(1000, 400 + length // 5 + stats["防御力"] // 2)

    return stats

# バトル1ターンの処理
def battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, log_lines):
    base_damage = max(10, atk_stats['攻撃力'] * 2 - def_stats['防御力'])

    # イベント発生処理
    event_log = ""
    damage = base_damage

    # 1/8の確率で完全防御チャレンジ
    if random.randint(1, 8) == 1 and random.random() < def_stats['読みの力'] / 300:
        damage = 0
        event_log += f"🧠 {defender} は読みの力で攻撃を無効化！\n"
    # それ以外の回避 or 軽減 or 増加
    elif random.random() < def_stats['素早さ'] / 400:
        damage = 0
        event_log += f"💨 {defender} は素早さで攻撃を回避！\n"
    else:
        if random.random() < def_stats['防御力'] / 400:
            damage = damage // 2
            event_log += f"🛡 {defender} の防御力でダメージ半減！\n"
        if random.randint(1, 10) == 1 and random.random() < atk_stats['人気度'] / 300:
            damage = int(damage * 1.5)
            event_log += f"🔥 {attacker} の人気度で観客が応援！ダメージ増加！\n"

    hp_dict[defender] = max(0, hp_dict[defender] - damage)

    log_lines.insert(0, f"{attacker} が {defender} に {damage} ダメージ！")
    if event_log:
        for line in reversed(event_log.strip().split('\n')):
            log_lines.insert(1, line)

    return damage

# 回復イベント
def check_heal(name, stats, hp_dict, log_lines):
    if random.randint(1, 10) == 1 and random.random() < stats['人気度'] / 300:
        heal = stats['人気度'] // 6
        hp_dict[name] = min(stats['体力'], hp_dict[name] + heal)
        log_lines.insert(1, f"💖 {name} は観客の声援で {heal} 回復した！")

# 赤く光る画像を返す（PILイメージ）
from wiki_utils import red_flash_image, darken_and_grayscale

def process_image_for_hit(img):
    return red_flash_image(img)

def process_image_for_defeat(img):
    return darken_and_grayscale(img)
