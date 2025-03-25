import streamlit as st
from wiki_utils import *
from battle_logic import *
import time
from PIL import Image

st.set_page_config(page_title="Wikipediaバトラー", layout="wide")
st.title(T["title"])

# 入力欄
col_input1, col_input2 = st.columns(2)
with col_input1:
    url1 = st.text_input(T["url1"])
with col_input2:
    url2 = st.text_input(T["url2"])

def add_yellow_border(img, border_size=10):
    w, h = img.size
    bordered = Image.new("RGB", (w + 2 * border_size, h + 2 * border_size), (255, 255, 0))
    bordered.paste(img, (border_size, border_size))
    return bordered

if st.button(T["start_battle"]) and url1 and url2:
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
        img_display1 = st.image(img1, use_container_width=True)
        st.markdown(f"### {title1}")
        hp_display1 = st.markdown(f"**{T['hp']}: {stats1['体力']}**")
        stat_box1 = st.empty()
        winner_text1 = st.empty()

    with col2:
        img_display2 = st.image(img2, use_container_width=True)
        st.markdown(f"### {title2}")
        hp_display2 = st.markdown(f"**{T['hp']}: {stats2['体力']}**")
        stat_box2 = st.empty()
        winner_text2 = st.empty()

    def update_stats():
        stats_copy1 = {k: v for k, v in stats1.items() if k != "体力"}
        stats_copy2 = {k: v for k, v in stats2.items() if k != "体力"}

        hp_display1.markdown(f"**{T['hp']}: {stats1['体力']}**")
        hp_display2.markdown(f"**{T['hp']}: {stats2['体力']}**")

        stat_box1.markdown("\n".join([f"{k}: {v}" for k, v in stats_copy1.items()]))
        stat_box2.markdown("\n".join([f"{k}: {v}" for k, v in stats_copy2.items()]))

    update_stats()

    log_container = st.empty()
    log_lines.append("⚡ 戦闘開始！")

    first, second = random.sample([title1, title2], 2)
    # イベント＋行動を一括でログにまとめる
    combined_log = []
    if len(log_lines) > 0 and not log_lines[-1].startswith("ターン"):
        # 直前の戦闘イベントをターンと紐づける
        last_event = log_lines.pop()
        combined_log.append(f"{turn_counter}: {last_event}")
    else:
        combined_log.append(f"{turn_counter}: （ログなし）")
    
    # ここに必要に応じて複数イベントを追加する場合の処理が可能（省略）
    
    # 勝敗決着時のログ処理
    if hp_dict[title1] <= 0 or hp_dict[title2] <= 0:
        combined_log.append(f"{turn_counter}: {T['winner']}{winner}！！")
    
    # 既存ログに追加
    log_lines.extend(combined_log)
    log_container.text_area(T["battle_log"], height=400, value="\n".join(reversed(log_lines)))
    time.sleep(1)

    while hp_dict[title1] > 0 and hp_dict[title2] > 0:
        attacker = first if turn_counter % 2 == 1 else second
        defender = second if attacker == first else first
        atk_stats = stats1 if attacker == title1 else stats2
        def_stats = stats2 if defender == title2 else stats1

        damage = battle_turn(attacker, defender, atk_stats, def_stats, hp_dict, log_lines)
        check_heal(attacker, atk_stats, hp_dict, log_lines)

        if defender == title1:
            stats1["体力"] = hp_dict[title1]
            img_display1.image(process_image_for_hit(img1_orig), use_container_width=True)
            time.sleep(0.2)
            img_display1.image(img1_orig, use_container_width=True)
        else:
            stats2["体力"] = hp_dict[title2]
            img_display2.image(process_image_for_hit(img2_orig), use_container_width=True)
            time.sleep(0.2)
            img_display2.image(img2_orig, use_container_width=True)

        update_stats()
        log_lines.append(f"ターン {turn_counter}")
        log_container.text_area(T["battle_log"], height=400, value="\n".join(reversed(log_lines)))
        turn_counter += 1
        time.sleep(0.8)

    winner = title1 if hp_dict[title1] > 0 else title2
    loser = title2 if winner == title1 else title1
    log_lines.append(f"🏆 勝者：{winner}！！")
    log_container.text_area(T["battle_log"], height=400, value="\n".join(reversed(log_lines)))


from streamlit_javascript import st_javascript

# Detect browser language
lang = st_javascript("navigator.language || navigator.userLanguage")
lang = lang[:2] if lang else 'ja'  # use 'ja' or 'en'

# Text dictionary
TEXTS = {
    'ja': {
        'title': "⚔️ Wikipedia バトラー",
        'url1': T["url1"],
        'url2': T["url2"],
        'start_battle': T["start_battle"],
        'battle_log': T["battle_log"],
        'winner': "🏆 勝者：",
        'start': "⚡ 戦闘開始！",
        'win': "🏅 勝者！",
        'hp': "体力"
    },
    'en': {
        'title': "⚔️ Wikipedia Battler",
        'url1': T["url1"],
        'url2': T["url2"],
        'start_battle': "Start Battle!",
        'battle_log': "Battle Log",
        'winner': "🏆 Winner:",
        'start': "⚡ Battle begins!",
        'win': "🏅 Winner!",
        'hp': "HP"
    }
}
T = TEXTS.get(lang, TEXTS['ja'])

    if winner == title1:
        img_display1.image(add_yellow_border(img1_orig), use_container_width=True)
        img_display2.image(process_image_for_defeat(img2_orig), use_container_width=True)
        winner_text1.markdown(f"{T['win']}")
        winner_text2.markdown("")
    else:
        img_display2.image(add_yellow_border(img2_orig), use_container_width=True)
        img_display1.image(process_image_for_defeat(img1_orig), use_container_width=True)
        winner_text2.markdown(f"{T['win']}")
        winner_text1.markdown("")
