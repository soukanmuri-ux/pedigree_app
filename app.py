import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ======================
# ページ設定
# ======================
st.set_page_config(
    page_title="競走馬 血統分析アプリ",
    layout="centered"
)

# ======================
# 関数定義
# ======================
def stars(score):
    return "⭐" * int(round(score))

def get_stallion(name, df):
    row = df[df["name"] == name]
    if row.empty:
        return None
    return row.iloc[0]

def generate_comment(result, surface, total_index):
    comments = []

    if result["speed"] >= 4:
        comments.append("スピード型")
    if result["stamina"] >= 4:
        comments.append("スタミナ型")
    if result["power"] >= 4:
        comments.append("パワー型")

    if surface == "芝":
        comments.append("芝向き")
    else:
        comments.append("ダート向き")

    if total_index >= 4.5:
        level = "G1級の血統"
    elif total_index >= 3.8:
        level = "重賞クラスの血統"
    elif total_index >= 3.2:
        level = "条件戦向きの血統"
    else:
        level = "成長待ちの血統"

    return "・".join(comments) + f"で、{level}。"

# ======================
# タイトル
# ======================
st.title("🏇 競走馬 血統分析アプリ")

# ======================
# CSV読み込み
# ======================
horses = pd.read_csv("horses.csv")
stallions = pd.read_csv("stallions.csv")

# ======================
# 入力UI
# ======================
horse_name = st.text_input("馬名を入力してください")
surface = st.radio("馬場を選択", ["芝", "ダート"])

# ======================
# メイン処理
# ======================
if horse_name:
    horse = horses[horses["horse_name"] == horse_name]

    if horse.empty:
        st.error("該当する馬が見つかりません")
    else:
        sire_name = horse.iloc[0]["sire"]
        dam_sire_name = horse.iloc[0]["dam_sire"]

        sire = get_stallion(sire_name, stallions)
        dam_sire = get_stallion(dam_sire_name, stallions)

        if sire is None or dam_sire is None:
            st.warning("血統データが不足しています")
        else:
            # ----------------------
            # 血統情報
            # ----------------------
            st.subheader("🧬 血統情報")
            st.write(f"父：{sire_name}")
            st.write(f"母父：{dam_sire_name}")

            # ----------------------
            # 基礎能力
            # ----------------------
            traits = ["speed", "stamina", "power", "europe", "usa", "japan"]
            result = {}

            for t in traits:
                result[t] = round(
                    sire[t] * 0.6 + dam_sire[t] * 0.4, 2
                )

            # ----------------------
            # 星評価
            # ----------------------
            st.subheader("⭐ 5段階評価")
            labels_jp = {
                "speed": "スピード",
                "stamina": "スタミナ",
                "power": "パワー",
                "europe": "欧州",
                "usa": "米国",
                "japan": "日本"
            }

            for k in labels_jp:
                st.write(f"{labels_jp[k]}：{stars(result[k])} ({result[k]})")

            # ----------------------
            # 芝・ダート適性
            # ----------------------
            if surface == "芝":
                surface_score = sire["turf"] * 0.6 + dam_sire["turf"] * 0.4
            else:
                surface_score = sire["dirt"] * 0.6 + dam_sire["dirt"] * 0.4

            surface_score = round(surface_score, 2)
            st.subheader("🏟 馬場適性")
            st.metric(f"{surface}適性", surface_score)

            # ----------------------
            # 総合血統指数
            # ----------------------
            total_index = round(
                result["speed"] * 0.25 +
                result["stamina"] * 0.25 +
                result["power"] * 0.2 +
                surface_score * 0.3, 2
            )

            st.subheader("🏆 総合血統指数")
            st.metric("Bloodline Index", total_index)

            # ----------------------
            # コメント生成
            # ----------------------
            st.subheader("📝 血統評価コメント")
            st.info(generate_comment(result, surface, total_index))

            # ----------------------
            # レーダーチャート（英語表記で文字化け回避）
            # ----------------------
            st.subheader("📊 Ability Balance")

            radar_labels = ["Speed", "Stamina", "Power", "Europe", "USA", "Japan"]
            radar_values = list(result.values())
            radar_values.append(radar_values[0])

            angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False)
            angles = np.append(angles, angles[0])

            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.plot(angles, radar_values)
            ax.fill(angles, radar_values, alpha=0.25)

            ax.set_thetagrids(angles[:-1] * 180 / np.pi, radar_labels)
            ax.set_ylim(0, 5)

            st.pyplot(fig)
