import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import urllib.parse

st.set_page_config(page_title="パーキング横断検索", layout="centered", page_icon="🚗")

st.title("🚗 パーキング横断検索")
st.caption("入力した目的地からの「距離順」や「料金順」でソートできます")

geolocator = Nominatim(user_agent="parking_search_app_v4")

location_input = st.text_input("目的地（住所や駅名、スポット名を入力）", placeholder="例：東京駅、渋谷区宇田川町")

sort_option = st.radio(
    "並び順を選択",
    ["距離が近い順", "時間料金が安い順 (円/h)", "当日最大料金が安い順 (円/日)"],
    horizontal=True
)

if st.button("検索する", type="primary") or location_input:
    if not location_input.strip():
        st.warning("目的地を入力してください。")
    else:
        with st.spinner("位置情報を取得して計算中..."):
            try:
                location = geolocator.geocode(location_input + ", 日本")
                
                if location is None:
                    st.error("入力された場所が見つかりませんでした。別の名称や住所でお試しください。")
                else:
                    target_lat = location.latitude
                    target_lon = location.longitude
                    
                    st.success(f"📍 目的地を認識しました: **{location.address}**")
                    st.markdown("---")
                    
                    encoded_keyword = urllib.parse.quote(location_input)
                    
                    # 確実にエラーにならない公式検索・Google検索連携URL
                    akippa_url = f"https://www.google.com/search?q=akippa+{encoded_keyword}"
                    toku_p_url = f"https://toku-p.earth-car.com/"
                    times_b_url = f"https://btimes.jp/"

                    # ※現在は画面動作テスト用のサンプルデータ（3件）です
                    raw_data = [
                        {
                            "サービス": "akippa",
                            "駐車場名": "akippa 周辺駐車場一覧",
                            "lat": target_lat + 0.0015,
                            "lon": target_lon + 0.0010,
                            "時間料金": 300,
                            "最大料金": 1500,
                            "予約URL": akippa_url
                        },
                        {
                            "サービス": "特P",
                            "駐車場名": "特P 周辺駐車場一覧",
                            "lat": target_lat - 0.0020,
                            "lon": target_lon - 0.0015,
                            "時間料金": 250,
                            "最大料金": 1200,
                            "予約URL": toku_p_url
                        },
                        {
                            "サービス": "タイムズのB",
                            "駐車場名": "タイムズのB 周辺駐車場一覧",
                            "lat": target_lat + 0.0035,
                            "lon": target_lon - 0.0005,
                            "時間料金": 400,
                            "最大料金": 1800,
                            "予約URL": times_b_url
                        }
                    ]
                    
                    target_point = (target_lat, target_lon)
                    for item in raw_data:
                        item_point = (item["lat"], item["lon"])
                        dist_m = int(geodesic(target_point, item_point).meters)
                        item["distance_m"] = dist_m
                        item["距離"] = f"{dist_m}m"
                    
                    df = pd.DataFrame(raw_data)
                    
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
                            
                            st.link_button(f"{row['サービス']}で「{location_input}」周辺を探す", row['予約URL'])
                            st.markdown("---")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
