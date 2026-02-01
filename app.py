import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="競走馬 血統分析", layout="centered")
st.title("🏇 競走馬 血統分析アプリ")

# =====================
# CSV 読み込み
# =====================
stallions = pd.read_csv("stallions.csv")
horses = pd.read_csv("horses.csv")

# =====================
# 5段階正規化
# =====================
def to_5scale(x, min_v, max_v):
    if max_v - min_v == 0:
        return 3
    return int(round(1 + 4 * (x - min_v) / (max_v - min_v)))

# =====================
# 評価エンジン（基盤）
# =====================
def evaluate(row):
    speed_raw   = row["speed"]*2   + row["japan"] + row["usa"]*0.5
    stamina_raw = row["stamina"]*2 + row["europe"] + row["power"]*0.5
    power_raw   = row["power"]*2   + row["usa"] + row["stamina"]*0.5

    japan_raw  = row["japan"]*2  + row["speed"] + row["stamina"]*0.5
    europe_raw = row["europe"]*2 + row["stamina"] + row["power"]*0.5
    usa_raw    = row["usa"]*2    + row["power"] + row["speed"]*0.5

    turf_raw  = speed_raw + stamina_raw + japan_raw
    dirt_raw  = power_raw + usa_raw

    short_raw  = speed_raw + power_raw
    middle_raw = speed_raw + stamina_raw
    long_raw   = stamina_raw * 2

    return {
        "speed": speed_raw,
        "stamina": stamina_raw,
        "power": power_raw,
        "japan": japan_raw,
        "europe": europe_raw,
        "usa": usa_raw,
        "turf": turf_raw,
        "dirt": dirt_raw,
        "short": short_raw,
        "middle": middle_raw,
        "long": long_raw,
    }

# =====================
# 入力
# =====================
horse_name = st.text_input("馬名を入力してください")

if horse_name:
    horse = horses[horses["horse_name"] == horse_name]

    if horse.empty:
        st.error("該当する馬が見つかりません")
    else:
        sire = horse.iloc[0]["sire"]
        dam_sire = horse.iloc[0]["dam_sire"]

        s1 = stallions[stallions["name"] == sire]
        s2 = stallions[stallions["name"] == dam_sire]

        if s1.empty or s2.empty:
            st.error("種牡馬データが不足しています")
        else:
            base = (s1.iloc[0][1:7] + s2.iloc[0][1:7]) / 2
            base = base.astype(float)

            raw = evaluate(base)

            # 正規化（5段階）
            keys = ["speed","stamina","power","japan","europe","usa"]
            vals = list(raw[k] for k in keys)
            min_v, max_v = min(vals), max(vals)

            scores = {k: to_5scale(raw[k], min_v, max_v) for k in keys}

            st.subheader("📊 基礎評価（5段階）")
            st.json(scores)

            st.subheader("🌱 芝・ダート適性（相対値）")
            st.write(f"芝：{raw['turf']:.1f}")
            st.write(f"ダート：{raw['dirt']:.1f}")

            st.subheader("📏 距離適性（相対値）")
            st.write(f"短距離：{raw['short']:.1f}")
            st.write(f"中距離：{raw['middle']:.1f}")
            st.write(f"長距離：{raw['long']:.1f}")

            # レーダーチャート
            labels = list(scores.keys())
            values = list(scores.values())
            values += values[:1]

            angles = np.linspace(0, 2*np.pi, len(labels)+1)

            fig = plt.figure()
            ax = plt.subplot(111, polar=True)
            ax.plot(angles, values)
            ax.fill(angles, values, alpha=0.3)
            ax.set_thetagrids(angles[:-1]*180/np.pi, labels)
            st.pyplot(fig)


