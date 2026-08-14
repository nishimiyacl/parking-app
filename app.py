import streamlit as st
import pandas as pd

# ページ設定（スマホ向けUI）
st.set_page_config(page_title="駐車場横断検索", layout="centered")

st.title("🚗 パーキング横断検索")
st.caption("距離順・料金順で自由にソートできます")

# 入力エリア
location_input = st.text_input("目的地（住所や駅名を入力）", placeholder="例：東京駅、渋谷区宇田川町")

# ソート条件の選択
sort_option = st.radio(
    "並び順を選択",
    ["距離が近い順", "時間料金が安い順 (円/h)", "当日最大料金が安い順 (円/日)"],
    horizontal=True
)

if st.button("検索する", type="primary") or location_input:
    st.markdown("---")
    
    # テスト用データ（※実際はここに検索ロジックが入ります）
    data = [
        {
            "サービス": "akippa",
            "駐車場名": "〇〇パーキング第1",
            "距離": "180m",
            "distance_m": 180,
            "時間料金": 300,
            "最大料金": 1200,
            "予約URL": "https://www.akippa.com/"
        },
        {
            "サービス": "特P",
            "駐車場名": "特P △△駐車場",
            "距離": "350m",
            "distance_m": 350,
            "時間料金": 200,
            "最大料金": 1000,
            "予約URL": "https://toku-p.earth-car.com/"
        },
        {
            "サービス": "タイムズのB",
            "駐車場名": "◇◇ビル駐車場",
            "距離": "90m",
            "distance_m": 90,
            "時間料金": 400,
            "最大料金": 1800,
            "予約URL": "https://btimes.jp/"
        }
    ]
    
    df = pd.DataFrame(data)
    
    if sort_option == "距離が近い順":
        df = df.sort_values("distance_m")
    elif sort_option == "時間料金が安い順 (円/h)":
        df = df.sort_values("時間料金")
    elif sort_option == "当日最大料金が安い順 (円/日)":
        df = df.sort_values("最大料金")

    st.subheader(f"検索結果（{sort_option}）")
    
    for _, row in df.iterrows():
        with st.container():
            st.markdown(f"### 【{row['サービス']}】{row['駐車場名']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("目的地まで", row['距離'])
            col2.metric("1時間", f"{row['時間料金']}円")
            col3.metric("最大", f"{row['最大料金']}円")
            
            st.link_button(f"{row['サービス']}で予約・詳細を見る", row['予約URL'])
            st.markdown("---")
