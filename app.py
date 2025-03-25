import streamlit as st
st.set_page_config(page_title="Wikipediaバトラー", layout="wide")  # 🔴 ←最上部！

from wiki_utils import *
from battle_logic import *
import time
from PIL import Image
import random

# 言語選択（安全な代替方法）
lang_selection = st.sidebar.selectbox("Select Language / 言語を選択", ["日本語", "English"])
LANG = "ja" if lang_selection == "日本語" else "en"

# 多言語辞書
TEXT = {
    "ja": {
        "title": "Wikipediaバトラー",
        "input1": "Wikipedia URL 1",
        "input2": "Wikipedia URL 2",
        "start_battle": "バトル開始！",
        "start": "⚡ 戦闘開始！",
        "first_turn": "⚡ 先手は：",
        "log_title": "戦闘ログ",
        "winner_prefix": "🏆 勝者：",
        "hp": "体力",
        "stats": "ステータス",
        "winner_mark": "🏅 勝者！",
        "no_image": "画像が表示できません",
        "winner": "🏆 勝者：",
        "victory": "🏅 勝者！"
    },
    "en": {
        "title": "Wikipedia Battler",
        "input1": "Wikipedia URL 1",
        "input2": "Wikipedia URL 2",
        "start_battle": "Start Battle!",
        "start": "⚡ Battle begins!",
        "first_turn": "⚡ First move: ",
        "log_title": "Battle Log",
        "winner_prefix": "🏆 Winner: ",
        "hp": "HP",
        "stats": "Stats",
        "winner_mark": "🏅 Winner!",
        "no_image": "Image not available",
        "winner": "🏆 Winner: ",
        "victory": "🏅 Winner!"
    }
}[LANG]

st.set_page_config(page_title=TEXT["title"], layout="wide")
st.title("⚔️ " + TEXT["title"])


col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input(TEXT["input1"])
with col_input2:
    url2 = st.text_input(TEXT["input2"])

# 勝者画像に黄色枠をつける関数
def add_yellow_border(img, border_size=10):
    w, h = img.size
    bordered = Image.new("RGB", (w + 2 * border_size, h + 2 * border_size), (255, 255, 0))
    bordered.paste(img, (border_size, border_size))
    return bordered

if st.button(TEXT["start_battle"]) and url1 and url2:
    title1 = get_page_title(url1)
    title2 = get_page_title(url2)
    lang1 = extract_lang_from_url(url1)
    lang2 = extract_lang_from_url(url2)

    text1 = get_article_text(title1, lang1)
    text2 = get_article_text(title2, lang2)

    stats1 = generate_stats(text1)
    stats2 = generate_stats(text2)

    image_url1 = get_first_image(title1, lang1)
    image_url2 = get_first_image(title2, lang2)

    img1 = download_image(image_url1) if image_url1 else None
    img2 = download_image(image_url2) if image_url2 else None
    img1 = crop_to_square(img1) if img1 else create_placeholder_image(title1[0])
    img2 = crop_to_square(img2) if img2 else create_placeholder_image(title2[0])

    img1_orig = img1.copy()
    img2_orig = img2.copy()

    hp_dict = {title1: stats1["体力"], title2: stats2["体力"]}
    log_lines = []
    turn_counter = 1
    winner = None

    col1, col2 = st.columns(2)
    with col1:
        img_display1 = st.empty()
        img_display1.image(img1, width=200)
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**{TEXT['hp']}: {stats1['体力']}**", unsafe_allow_html=True)
        stats_copy1 = {k: v for k, v in stats1.items() if k != "体力"}
        stat_box1 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats_copy1.items()]))

    with col2:
        img_display2 = st.empty()
        img_display2.image(img2, width=200)
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**{TEXT['hp']}: {stats2['体力']}**", unsafe_allow_html=True)
        stats_copy2 = {k: v for k, v in stats2.items() if k != "体力"}
        stat_box2 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats_copy2.items()]))

# （ここから後半が続きます）
    winner_text1 = st.empty()
    winner_text2 = st.empty()
    log_box = st.empty()

    def update_stats():
        hp_display1.markdown(f"**{TEXT['hp']}: {stats1['体力']}**", unsafe_allow_html=True)
        hp_display2.markdown(f"**{TEXT['hp']}: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box1.markdown("\n".join([f"{k}: {v}" for k, v in stats1.items() if k != "体力"]))
        stat_box2.markdown("\n".join([f"{k}: {v}" for k, v in stats2.items() if k != "体力"]))

    # 戦闘ログ初期化
    log_lines.insert(0, f"{turn_counter}: {TEXT['start']}")
    first, second = random.sample([title1, title2], 2)
    turn_counter += 1
    log_lines.insert(0, f"{turn_counter}: {TEXT['first_turn']}{first}")
    log_box.text_area(TEXT["log_title"], height=400, value="\n".join(log_lines), key="log_area")

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 0 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1

        events = []
        damage = battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events)
        check_heal(attacker, atk_stats, hp_dict, events)

        if defender == title1:
            stats1["体力"] = hp_dict[title1]
            img_display1.image(process_image_for_hit(img1_orig), width=200)
            time.sleep(0.2)
            img_display1.image(img1_orig, width=200)
        else:
            stats2["体力"] = hp_dict[title2]
            img_display2.image(process_image_for_hit(img2_orig), width=200)
            time.sleep(0.2)
            img_display2.image(img2_orig, width=200)

        update_stats()
        for event in reversed(events):
            log_lines.insert(0, f"{turn_counter}: {event}")

        turn_counter += 1
        log_box.text_area(TEXT["log_title"], height=400, value="\n".join(log_lines), key="log_area_updated")
        time.sleep(0.6)

    winner = title1 if hp_dict[title1] > 0 else title2
    loser = title2 if winner == title1 else title1
    log_lines.insert(0, f"{turn_counter}: {TEXT['winner']}{winner}！！")
    log_box.text_area(TEXT["log_title"], height=400, value="\n".join(log_lines), key="log_area_final")

    if winner == title1:
        img_display1.image(add_yellow_border(img1_orig), width=200)
        img_display2.image(process_image_for_defeat(img2_orig), width=200)
        winner_text1.markdown(f"{TEXT['victory']}")
        winner_text2.markdown("")
    else:
        img_display2.image(add_yellow_border(img2_orig), width=200)
        img_display1.image(process_image_for_defeat(img1_orig), width=200)
        winner_text2.markdown(f"{TEXT['victory']}")
        winner_text1.markdown("")
