
import streamlit as st
from wiki_utils import *
from battle_logic import *
import time
from PIL import Image
import random
from wiki_utils import suggest_titles

st.set_page_config(page_title="Wikipediaバトラー", layout="wide")
st.title("⚔️ Wikipedia バトラー")

# キーワード検索と記事候補選択
col_search1, col_search2 = st.columns(2)
with col_search1:
    query1 = st.text_input("キーワードを入力（例：ピラミッド）", key="query1")
    titles1 = suggest_titles(query1, "ja") if query1 else []
    selected1 = st.selectbox("記事候補を選択", titles1) if titles1 else None
with col_search2:
    query2 = st.text_input("キーワードを入力（例：バッハ）", key="query2")
    titles2 = suggest_titles(query2, "ja") if query2 else []
    selected2 = st.selectbox("記事候補を選択", titles2) if titles2 else None

# 直接URL入力欄
col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input("Wikipedia URL 1")
with col_input2:
    url2 = st.text_input("Wikipedia URL 2")

# 記事タイトル優先処理
if selected1:
    url1 = f"https://ja.wikipedia.org/wiki/{selected1}"
if selected2:
    url2 = f"https://ja.wikipedia.org/wiki/{selected2}"

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

    skills1 = get_special_moves(title1, lang1)
    skills2 = get_special_moves(title2, lang2)

    image_url1 = get_first_image(title1, lang1)
    image_url2 = get_first_image(title2, lang2)

    img1 = download_image(image_url1) if image_url1 else None
    img2 = download_image(image_url2) if image_url2 else None
    img1 = crop_to_square(img1) if img1 else create_placeholder_image(title1[0])
    img2 = crop_to_square(img2) if img2 else create_placeholder_image(title2[0])

    img1_orig = img1.copy()
    img2_orig = img2.copy()

    col1, col2 = st.columns(2)
    with col1:
        img_display1 = st.empty()
        winner_text1 = st.empty()
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**体力: {stats1['体力']}**", unsafe_allow_html=True)
        stat_box1 = st.markdown(format_stats(stats1))
    with col2:
        img_display2 = st.empty()
        winner_text2 = st.empty()
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**体力: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box2 = st.markdown(format_stats(stats2))

    hp_dict = {title1: stats1["体力"], title2: stats2["体力"]}
    log_lines = []
    turn_counter = 1
    winner = None

    log_container = st.empty()
    log_lines.insert(0, f"{turn_counter}: ⚡ 戦闘開始！")
    first, second = random.sample([title1, title2], 2)
    log_lines.insert(0, f"{turn_counter}: ⚡ 先手は：{first}")

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1
        atk_img_display = img_display1 if attacker == title1 else img_display2
        def_img_display = img_display2 if defender == title2 else img_display1
        atk_img_orig = img1_orig if attacker == title1 else img2_orig
        def_img_orig = img2_orig if defender == title2 else img1_orig
        atk_skills = skills1 if attacker == title1 else skills2

        events = []
        damage = battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events, atk_skills)
        heal = check_heal(attacker, atk_stats, hp_dict, events)

        if defender == title1:
            stats1["体力"] = hp_dict[title1]
        else:
            stats2["体力"] = hp_dict[title2]

        def_img_display.image(process_image_for_hit(def_img_orig), width=200)
        time.sleep(0.2)
        def_img_display.image(def_img_orig, width=200)

        hp_display1.markdown(f"**体力: {stats1['体力']}**")
        hp_display2.markdown(f"**体力: {stats2['体力']}**")
        stat_box1.markdown(format_stats(stats1))
        stat_box2.markdown(format_stats(stats2))

        for event in reversed(events):
            log_lines.insert(0, f"{turn_counter}: {event}")

        turn_counter += 1
        log_container.text_area("戦闘ログ", height=400, value="\n".join(log_lines))
        time.sleep(0.8)

    winner = title1 if hp_dict[title1] > 0 else title2
    loser = title2 if winner == title1 else title1
    log_lines.insert(0, f"{turn_counter}: 🏆 勝者：{winner}！！")
    log_container.text_area("戦闘ログ", height=400, value="\n".join(log_lines))

    if winner == title1:
        img_display1.image(add_yellow_border(img1_orig), width=200)
        img_display2.image(process_image_for_defeat(img2_orig), width=200)
        winner_text1.markdown("🏅 **勝者！**")
        winner_text2.markdown("")
    else:
        img_display2.image(add_yellow_border(img2_orig), width=200)
        img_display1.image(process_image_for_defeat(img1_orig), width=200)
        winner_text2.markdown("🏅 **勝者！**")
        winner_text1.markdown("")
