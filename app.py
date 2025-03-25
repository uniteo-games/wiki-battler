import streamlit as st
import time
from wiki_utils import fetch_wiki_content, get_processed_image
from battle_logic import generate_stats, battle_round

st.set_page_config(page_title="Wikiバトラー", layout="wide")

# 初期化
if "log" not in st.session_state:
    st.session_state.log = []
if "turn" not in st.session_state:
    st.session_state.turn = 0
if "battle_over" not in st.session_state:
    st.session_state.battle_over = False
if "highlight" not in st.session_state:
    st.session_state.highlight = {"left": False, "right": False}

# 入力
col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input("左のURL", "https://ja.wikipedia.org/wiki/ギザの大ピラミッド")
with col_input2:
    url2 = st.text_input("右のURL", "https://ja.wikipedia.org/wiki/心理学原理")

if url1 and url2:
    # データ取得
    text1, title1, page1 = fetch_wiki_content(url1)
    text2, title2, page2 = fetch_wiki_content(url2)
    stats1 = generate_stats(text1, page1)
    stats2 = generate_stats(text2, page2)
    img1 = get_processed_image(page1)
    img2 = get_processed_image(page2)

    # バトラー表示
    col1, col2 = st.columns(2)
    with col1:
        st.image(img1, width=220)
        if st.session_state.highlight["left"]:
            st.image(img1, caption=None, width=120, output_format="PNG", channels="RGB", use_column_width=False)
            st.markdown('<div style="border: 5px solid yellow; width: 120px; margin: auto;"></div>', unsafe_allow_html=True)
        st.markdown(f"### {title1}")
        st.markdown(f"<b style='font-size: 20px;'>体力: {stats1['体力']}</b>", unsafe_allow_html=True)
        st.markdown(f"攻撃力: {stats1['攻撃力']} 防御力: {stats1['防御力']} 素早さ: {stats1['素早さ']} 読みの力: {stats1['読みの力']} 人気度: {stats1['人気度']}")
    with col2:
        st.image(img2, width=220)
        if st.session_state.highlight["right"]:
            st.image(img2, caption=None, width=120, output_format="PNG", channels="RGB", use_column_width=False)
            st.markdown('<div style="border: 5px solid yellow; width: 120px; margin: auto;"></div>', unsafe_allow_html=True)
        st.markdown(f"### {title2}")
        st.markdown(f"<b style='font-size: 20px;'>体力: {stats2['体力']}</b>", unsafe_allow_html=True)
        st.markdown(f"攻撃力: {stats2['攻撃力']} 防御力: {stats2['防御力']} 素早さ: {stats2['素早さ']} 読みの力: {stats2['読みの力']} 人気度: {stats2['人気度']}")

    if st.button("⚔️ バトル開始！"):
        st.session_state.log = ["1: ⚡ 戦闘開始！"]
        st.session_state.turn = 1
        st.session_state.battle_over = False
        st.session_state.highlight = {"left": False, "right": False}

        hp1 = stats1["体力"]
        hp2 = stats2["体力"]
        attacker = "left"

        while hp1 > 0 and hp2 > 0:
            result, dmg, event = battle_round(stats1, stats2, attacker)
            if attacker == "left":
                hp2 = max(0, hp2 - dmg)
            else:
                hp1 = max(0, hp1 - dmg)

            log_msg = f"{st.session_state.turn+1}: {event or result}"
            st.session_state.log.insert(0, log_msg)

            if hp1 == 0 or hp2 == 0:
                winner = title1 if hp2 == 0 else title2
                st.session_state.log.insert(0, f"{st.session_state.turn+2}: 🏆 勝者：{winner}！！")
                st.session_state.highlight["left"] = (hp2 == 0)
                st.session_state.highlight["right"] = (hp1 == 0)
                break

            attacker = "right" if attacker == "left" else "left"
            st.session_state.turn += 1
            time.sleep(0.2)

    # ログ表示
    st.markdown("### 戦闘ログ")
    with st.container():
        st.code("\n".join(st.session_state.log), language="markdown")
