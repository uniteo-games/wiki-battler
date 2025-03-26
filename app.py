import streamlit as st
from wiki_utils import *
from battle_logic import *
import requests
import time
from PIL import Image
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="Wiki大戦", layout="wide")
st.title("⚔️ Wiki大戦")

def search_wikipedia_titles(query, lang="ja"):
    """キーワードからWikipediaの記事候補を返す"""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "format": "json",
        "search": query
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data[1], data[3]  # title list, URL list
    except:
        return [], []

col_input1, col_input2 = st.columns(2)

with col_input1:
    input_type1 = st.radio("入力方法 1", ["記事名から選ぶ", "URLを直接入力"])
    if input_type1 == "記事名から選ぶ":
        query1 = st.text_input("キーワードを入力（例：ピラミッド）", key="query1")
        if query1:
            titles1, urls1 = search_wikipedia_titles(query1)
            selected1 = st.selectbox("記事候補を選択", titles1) if titles1 else None
            url1 = urls1[titles1.index(selected1)] if selected1 else ""
        else:
            url1 = ""
    else:
        url1 = st.text_input("Wikipedia URL 1", key="url1")

with col_input2:
    input_type2 = st.radio("入力方法 2", ["記事名から選ぶ", "URLを直接入力"])
    if input_type2 == "記事名から選ぶ":
        query2 = st.text_input("キーワードを入力（例：バッハ）", key="query2")
        if query2:
            titles2, urls2 = search_wikipedia_titles(query2)
            selected2 = st.selectbox("記事候補を選択", titles2) if titles2 else None
            url2 = urls2[titles2.index(selected2)] if selected2 else ""
        else:
            url2 = ""
    else:
        url2 = st.text_input("Wikipedia URL 2", key="url2")

def add_yellow_border(img, border_size=10):
    w, h = img.size
    bordered = Image.new("RGB", (w + 2 * border_size, h + 2 * border_size), (255, 255, 0))
    bordered.paste(img, (border_size, border_size))
    return bordered

if st.button("バトル開始！") and name1 and name2:
    title1 = get_page_title(name1)
    title2 = get_page_title(name2)
    lang1 = extract_lang_from_url(name1)
    lang2 = extract_lang_from_url(name2)

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
        img_display1 = st.image(img1, width=200)
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**体力: {stats1['体力']}**", unsafe_allow_html=True)
        stat_box1 = st.markdown(display_stats(stats1))

    with col2:
        img_display2 = st.image(img2, width=200)
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**体力: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box2 = st.markdown(display_stats(stats2))

    def update_stats():
        stats_copy1 = {k: v for k, v in stats1.items() if k != "体力"}
        stats_copy2 = {k: v for k, v in stats2.items() if k != "体力"}
        hp_display1.markdown(f"**体力: {stats1['体力']}**", unsafe_allow_html=True)
        hp_display2.markdown(f"**体力: {stats2['体力']}**", unsafe_allow_html=True)
        stat_box1.markdown(display_stats(stats_copy1))
        stat_box2.markdown(display_stats(stats_copy2))

    log_container = st.empty()
    log_lines.insert(0, f"{turn_counter}: ⚡ 戦闘開始！")
    first, second = random.sample([title1, title2], 2)
    log_lines.insert(0, f"{turn_counter}: ⚡ 先手は：{first}")

    special1 = extract_special_moves(text1)
    special2 = extract_special_moves(text2)

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1
        img_display = img_display1 if defender == title1 else img_display2
        img_orig = img1_orig if defender == title1 else img2_orig

        special_moves = special1 if attacker == title1 else special2
        events = []
        damage = battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, events, special_moves)

        if defender == title1:
            stats1["体力"] = hp_dict[title1]
        else:
            stats2["体力"] = hp_dict[title2]

        img_display.image(process_image_for_hit(img_orig), width=200)
        time.sleep(0.2)
        img_display.image(img_orig, width=200)

        update_stats()

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
    else:
        img_display2.image(add_yellow_border(img2_orig), width=200)
        img_display1.image(process_image_for_defeat(img1_orig), width=200)
