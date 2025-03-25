import streamlit as st
st.set_page_config(page_title="Wikipediaバトラー", layout="wide")
from streamlit_javascript import st_javascript
from wiki_utils import *
from battle_logic import *
import time
from PIL import Image
import random



# 🌐 自動言語切替
lang_code = st_javascript("window.navigator.language")[:2]
if lang_code == "ja":
    lang = "ja"
    TEXT = {
        "title": "⚔️ Wikipedia バトラー",
        "start_battle": "バトル開始！",
        "url1": "Wikipedia URL 1",
        "url2": "Wikipedia URL 2",
        "log": "戦闘ログ",
        "winner": "🏅 勝者！",
        "battle_start": "⚡ 戦闘開始！",
        "turn": "ターン",
        "hp": "体力"
    }
else:
    lang = "en"
    TEXT = {
        "title": "⚔️ Wikipedia Battler",
        "start_battle": "Start Battle!",
        "url1": "Wikipedia URL 1",
        "url2": "Wikipedia URL 2",
        "log": "Battle Log",
        "winner": "🏅 Winner!",
        "battle_start": "⚡ Battle Start!",
        "turn": "Turn",
        "hp": "HP"
    }

st.set_page_config(page_title=TEXT["title"], layout="wide")
st.title(TEXT["title"])

col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input(TEXT["url1"])
with col_input2:
    url2 = st.text_input(TEXT["url2"])

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

    col1, col2 = st.columns(2)
    with col1:
        img_display1 = st.image(img1, width=200)
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**{TEXT['hp']}: {stats1['体力']}**", unsafe_allow_html=True)
        stat_box1 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats1.items() if k != "体力"]))
        winner_text1 = st.empty()

    with col2:
        img_display2 = st.image(img2, width=200)
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**{TEXT['hp']}: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box2 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats2.items() if k != "体力"]))
        winner_text2 = st.empty()

    def update_stats():
        hp_display1.markdown(f"**{TEXT['hp']}: {stats1['体力']}**", unsafe_allow_html=True)
        hp_display2.markdown(f"**{TEXT['hp']}: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box1.markdown("\n".join([f"{k}: {v}" for k, v in stats1.items() if k != "体力"]))
        stat_box2.markdown("\n".join([f"{k}: {v}" for k, v in stats2.items() if k != "体力"]))

    log_container = st.empty()
    log_lines.insert(0, f"{turn_counter}: {TEXT['battle_start']}")

    first, second = random.sample([title1, title2], 2)

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
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

        log_container.text_area(TEXT["log"], height=400, value="\n".join(log_lines), key=f"log_{turn_counter}")
        turn_counter += 1
        time.sleep(0.7)

    winner = title1 if hp_dict[title1] > 0 else title2
    loser = title2 if winner == title1 else title1
    log_lines.insert(0, f"{turn_counter}: 🏆 勝者：{winner}！！")
    log_container.text_area(TEXT["log"], height=400, value="\n".join(log_lines), key="log_final")

    if winner == title1:
        img_display1.image(add_yellow_border(img1_orig), width=200)
        img_display2.image(process_image_for_defeat(img2_orig), width=200)
        winner_text1.markdown(TEXT["winner"])
        winner_text2.markdown("")
    else:
        img_display2.image(add_yellow_border(img2_orig), width=200)
        img_display1.image(process_image_for_defeat(img1_orig), width=200)
        winner_text2.markdown(TEXT["winner"])
        winner_text1.markdown("")
