import streamlit as st
from wiki_utils import *
from battle_logic import *
import time
from PIL import Image

st.set_page_config(page_title="Wikipediaバトラー", layout="wide")
st.title("⚔️ Wikipedia バトラー")

col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input("Wikipedia URL 1")
with col_input2:
    url2 = st.text_input("Wikipedia URL 2")

def add_yellow_border(img, border_size=10):
    w, h = img.size
    bordered = Image.new("RGB", (w + 2 * border_size, h + 2 * border_size), (255, 255, 0))
    bordered.paste(img, (border_size, border_size))
    return bordered

if st.button("バトル開始！") and url1 and url2:
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
    stat_col1 = col1.container()
    stat_col2 = col2.container()

    with stat_col1:
        st.image(img1_orig, width=200)
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**体力: {stats1['体力']}**", unsafe_allow_html=True)
        stat_box1 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats1.items() if k != "体力"]))

    with stat_col2:
        st.image(img2_orig, width=200)
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**体力: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box2 = st.markdown("\n".join([f"{k}: {v}" for k, v in stats2.items() if k != "体力"]))

    log_container = st.container()
    log_lines.insert(0, f"{turn_counter}: ⚡ 戦闘開始！")

    first, second = random.sample([title1, title2], 2)

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1

        events = []
        battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events)
        check_heal(attacker, atk_stats, hp_dict, events)

        stats1["体力"] = hp_dict[title1]
        stats2["体力"] = hp_dict[title2]

        hp_display1.markdown(f"**体力: {stats1['体力']}**", unsafe_allow_html=True)
        hp_display2.markdown(f"**体力: {stats2['体力']}**", unsafe_allow_html=True)

        stat_box1.markdown("\n".join([f"{k}: {v}" for k, v in stats1.items() if k != "体力"]))
        stat_box2.markdown("\n".join([f"{k}: {v}" for k, v in stats2.items() if k != "体力"]))

        for event in reversed(events):
            log_lines.insert(0, f"{turn_counter}: {event}")

        log_container.text_area("戦闘ログ", height=400, value="\n".join(log_lines))
        turn_counter += 1
        time.sleep(0.8)

    winner = title1 if hp_dict[title1] > 0 else title2
    loser = title2 if winner == title1 else title1
    log_lines.insert(0, f"{turn_counter}: 🏆 勝者：{winner}！！")
    log_container.text_area("戦闘ログ", height=400, value="\n".join(log_lines))

    with col1:
        if winner == title1:
            st.image(add_yellow_border(img1_orig), width=200)
        else:
            st.image(process_image_for_defeat(img1_orig), width=200)

    with col2:
        if winner == title2:
            st.image(add_yellow_border(img2_orig), width=200)
        else:
            st.image(process_image_for_defeat(img2_orig), width=200)
