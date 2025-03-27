import streamlit as st
from wiki_utils import *
from battle_logic import *
import time
from PIL import Image
import random

st.set_page_config(page_title="Wikipediaバトラー", layout="wide")
st.title("⚔️ Wikipedia バトラー")

# 入力欄2列
col_input1, col_input2 = st.columns(2)
with col_input1:
    query1 = st.text_input("記事候補検索 1")
    url1 = st.text_input("Wikipedia URL 1")
with col_input2:
    query2 = st.text_input("記事候補検索 2")
    url2 = st.text_input("Wikipedia URL 2")

# バトルボタン
st.markdown("<div style='text-align:center;'><h3>　</h3></div>", unsafe_allow_html=True)
battle_start = st.button("バトル開始！")

# バトル処理
if battle_start and url1 and url2:
    title1 = get_page_title(url1)
    title2 = get_page_title(url2)
    lang1 = extract_lang_from_url(url1)
    lang2 = extract_lang_from_url(url2)

    text1 = get_article_text(title1, lang1)
    text2 = get_article_text(title2, lang2)
    stats1 = generate_stats(text1, title1, lang1)
    stats2 = generate_stats(text2, title2, lang2)

    image_url1 = get_first_image(title1, lang1)
    image_url2 = get_first_image(title2, lang2)

    img1 = download_image(image_url1) if image_url1 else None
    img2 = download_image(image_url2) if image_url2 else None
    img1 = crop_to_square(img1) if img1 else create_placeholder_image(title1[0])
    img2 = crop_to_square(img2) if img2 else create_placeholder_image(title2[0])
    img1_orig = img1.copy()
    img2_orig = img2.copy()

    skills1 = get_special_moves(title1, lang1)
    skills2 = get_special_moves(title2, lang2)

    hp_dict = {title1: stats1["体力"], title2: stats2["体力"]}
    log_lines = []
    turn_counter = 1
    winner = None

    # 画像・ステータス表示
    col1, col2 = st.columns(2)
    with col1:
        st.image(img1, use_column_width=True)
        st.markdown(f"### {title1}")
        st.markdown(f"**体力: {hp_dict[title1]}**", unsafe_allow_html=True)
        st.markdown(format_stats(stats1))
    with col2:
        st.image(img2, use_column_width=True)
        st.markdown(f"### {title2}")
        st.markdown(f"**体力: {hp_dict[title2]}**", unsafe_allow_html=True)
        st.markdown(format_stats(stats2))

    # ログエリア
    log_container = st.empty()
    log_lines.insert(0, f"{turn_counter}: ⚡ 戦闘開始！")
    first, second = random.sample([title1, title2], 2)
    log_lines.insert(0, f"{turn_counter}: ⚡ 先手は：{first}")
    log_container.text_area("戦闘ログ", height=300, value="\n".join(log_lines), key="log_area")

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1
        skill_list = skills1 if attacker == title1 else skills2

        events = []
        damage = battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events, skill_list)

        for event in reversed(events):
            log_lines.insert(0, f"{turn_counter}: {event}")

        turn_counter += 1
        log_container.text_area("戦闘ログ", height=300, value="\n".join(log_lines), key="log_area_updated")
        time.sleep(0.8)

    winner = title1 if hp_dict[title1] > 0 else title2
    log_lines.insert(0, f"{turn_counter}: 🏆 勝者：{winner}！！")
    log_container.text_area("戦闘ログ", height=300, value="\n".join(log_lines), key="log_area_final")
