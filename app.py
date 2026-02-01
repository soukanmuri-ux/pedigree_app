import streamlit as st
import pandas as pd

st.title("競走馬 血統分析アプリ")

# CSV読み込み
horses = pd.read_csv("horses.csv")

# 馬名入力
horse_name = st.text_input("馬名を入力してください")

if horse_name:
    result = horses[horses["horse_name"] == horse_name]

    if result.empty:
        st.error("該当する馬が見つかりません")
    else:
        st.subheader("血統情報")
        st.write("父:", result.iloc[0]["sire"])
        st.write("母父:", result.iloc[0]["dam_sire"])