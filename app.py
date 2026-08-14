import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# --- ページ基本設定 ---
st.set_page_config(page_title="パーキング横断検索", layout="centered", page_icon="🚗")

st.title("🚗 パーキング横断検索")
st.caption("入力した目的地からの「距離順」や「料金順」でソートできます")

# --- ジオコーダー（住所・駅名 ➔ 緯度経度 変換器）の準備 ---
geolocator = Nominatim(user_agent="parking_search_app_v1")

# --- 入力エリア ---
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
                # 住所から緯度経度を取得
                location = geolocator.geocode(location_input + ", 日本")
                
                if location is None:
                    st.error("入力された場所が見つかりませんでした。別の名称や住所でお試しください。")
                else:
                    target_lat = location.latitude
                    target_lon = location.longitude
                    
                    st.success(f"📍 目的地を認識しました: **{location.address}**")
                    st.markdown("---")
                    
                    # --- 各駐車場のサンプルデータ（ベースの緯度経度付き） ---
                    # ※東京駅周辺を基準としたサンプル（目的地の緯度経度に応じて距離が動的に変化します）
                    raw_data = [
                        {
                            "サービス": "akippa",
                            "駐車場名": "akippa 丸の内パーキング",
                            "lat": target_lat + 0.0015,
                            "lon": target_lon + 0.0010,
                            "時間料金": 300,
                            "最大料金": 1500,
                            "予約URL": f"https://www.akippa.com/search/keyword/{location_input}"
                        },
                        {
                            "サービス": "特P",
                            "駐車場名": "特P 大手町駐車場",
                            "lat": target_lat - 0.0020,
                            "lon": target_lon - 0.0015,
                            "時間料金": 250,
                            "最大料金": 1200,
                            "予約URL": "https://toku-p.earth-car.com/"
                        },
                        {
                            "サービス": "タイムズのB",
                            "駐車場名": "Bタイムズ 〇〇ビルステーション",
                            "lat": target_lat + 0.0035,
                            "lon": target_lon - 0.0005,
                            "時間料金": 400,
                            "最大料金": 1800,
                            "予約URL": "https://btimes.jp/"
                        },
                        {
                            "サービス": "akippa",
                            "駐車場名": "akippa 第二住宅駐車場",
                            "lat": target_lat - 0.0008,
                            "lon": target_lon + 0.0025,
                            "時間料金": 200,
                            "最大料金": 1000,
                            "予約URL": f"https://www.akippa.com/search/keyword/{location_input}"
                        }
                    ]
                    
                    # --- 動的距離計算 ---
                    target_point = (target_lat, target_lon)
                    for item in raw_data:
                        item_point = (item["lat"], item["lon"])
                        # geodesicで直線距離(メートル)を計算
                        dist_m = int(geodesic(target_point, item_point).meters)
                        item["distance_m"] = dist_m
                        item["距離"] = f"{dist_m}m"
                        
                        # akippa等の直接検索リンクを動的作成
                        if item["サービス"] == "akippa":
                            item["予約URL"] = f"https://www.akippa.com/search/keyword/{location_input}"
                        elif item["サービス"] == "特P":
                            item["予約URL"] = f"https://toku-p.earth-car.com/parking-search/{location_input}"
                    
                    df = pd.DataFrame(raw_data)
                    
                    # --- 並び替え（ソート） ---
                    if sort_option == "距離が近い順":
                        df = df.sort_values("distance_m")
                    elif sort_option == "時間料金が安い順 (円/h)":
                        df = df.sort_values("時間料金")
                    elif sort_option == "当日最大料金が安い順 (円/日)":
                        df = df.sort_values("最大料金")

                    st.subheader(f"検索結果（{sort_option}）")
                    
                    # カード形式で表示
                    for _, row in df.iterrows():
                        with st.container():
                            st.markdown(f"### 【{row['サービス']}】{row['駐車場名']}")
                            col1, col2, col3 = st.columns(3)
                            col1.metric("目的地まで", row['距離'])
                            col2.metric("1時間", f"{row['時間料金']}円")
                            col3.metric("最大", f"{row['最大料金']}円")
                            
                            st.link_button(f"{row['サービス']}で予約・空き確認", row['予約URL'])
                            st.markdown("---")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
