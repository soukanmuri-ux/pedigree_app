import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォント対策（Streamlit Cloud OK）
rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(page_title="競走馬 血統分析", layout="centered")
st.title("🏇 競走馬 血統分析アプリ")

# ======================
# CSV 読み込み
# ======================
horses = pd.read_csv("horses.csv")
stallions = pd.read_csv("stallions.csv")

# ======================
# 馬名入力
# ======================
horse_name = st.text_input("馬名を入力してください")

if horse_name:
    horse = horses[horses["horse_name"] == horse_name]

    if horse.empty:
        st.error("該当する馬が見つかりません")
        st.stop()

    sire_name = horse.iloc[0]["sire"]
    dam_sire_name = horse.iloc[0]["dam_sire"]

    sire = stallions[stallions["name"] == sire_name]
    dam_sire = stallions[stallions["name"] == dam_sire_name]

    if sire.empty or dam_sire.empty:
        st.error("種牡馬データが不足しています")
        st.stop()

    sire = sire.iloc[0]
    dam_sire = dam_sire.iloc[0]

    # ======================
    # 母父 40% 反映
    # ======================
    def mix(col):
        return round(sire[col] * 0.6 + dam_sire[col] * 0.4, 2)

    result = {
        "speed": mix("speed"),
        "stamina": mix("stamina"),
        "power": mix("power"),
        "europe": mix("europe"),
        "usa": mix("usa"),
        "japan": mix("japan"),
    }

    # ======================
    # 派生指標
    # ======================
    turf = round(
        (result["speed"] + result["stamina"] +
         result["europe"] + result["japan"]) / 4, 2
    )

    dirt = round(
        (result["power"] + result["usa"] +
         result["stamina"]) / 3, 2
    )

    short = round(result["speed"], 2)
    middle = round((result["speed"] + result["stamina"]) / 2, 2)
    long = round(result["stamina"], 2)

    # ======================
    # 表示
    # ======================
    st.subheader("🧬 血統構成")
    st.write(f"父：{sire_name}")
    st.write(f"母父：{dam_sire_name}")

    st.subheader("📊 能力指数")
    st.write(result)

    st.subheader("🌱 適性")
    st.write(f"芝適性：{turf}")
    st.write(f"ダート適性：{dirt}")
    st.write(f"短距離：{short} / 中距離：{middle} / 長距離：{long}")

    # ======================
    # レーダーチャート
    # ======================
    labels = list(result.keys())
    values = list(result.values())
    values.append(values[0])

    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    angles.append(angles[0])

    fig = plt.figure()
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    ax.set_thetagrids([a * 180 / 3.14159 for a in angles[:-1]], labels)
    ax.set_ylim(0, 5)

    st.pyplot(fig)
