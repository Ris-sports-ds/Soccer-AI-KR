import streamlit as st
import google.generativeai as genai
import os

# ページのデザイン設定
st.set_page_config(page_title="Soccer Strategy AI", page_icon="⚽", layout="wide")

# 本番環境（Secrets）からAPIキーを読み込む設定
# キーの名前は後ほど設定する「GEMINI_API_KEY」に合わせます
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # 予備として直接入力欄も残しておきます
    api_key = st.sidebar.text_input("Gemini APIキーを入力", type="password")

st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    .stButton>button {
        width: 100%; 
        background: linear-gradient(to right, #FF4B2B, #FF416C); 
        color: white; 
        font-size: 20px; 
        border-radius: 10px;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- メイン画面 ---
st.title("⚽ チーム戦略診断：ワクワクをデータに。")
st.subheader("熊谷西サッカークラブ様・市民の皆様へ")

with st.form("soccer_form"):
    st.markdown("### 1. チームの『北極星』とワクワクの源泉")
    col1, col2 = st.columns(2)
    with col1:
        target = st.text_input("🏆 今シーズンの野望（目標）", placeholder="例：3部全勝優勝！")
    with col2:
        category = st.selectbox("カテゴリー", ["社会人リーグ", "大学・高校(強豪)", "高校(一般)", "ジュニアユース"])

    excitement = st.text_area("✨ プレーしていて『最高にワクワクする瞬間』は？", 
        placeholder="例：サイドを連動して崩し切ったとき！")

    st.markdown("---")
    st.markdown("### 2. 俺たちの『武器』と『こだわり』")
    col3, col4 = st.columns(2)
    with col3:
        strengths = st.multiselect("⚔️ チームの誇れる武器（複数選択）", 
            ["サイドのスピード", "圧倒的な運動量", "セットプレーの破壊力", "個のドリブル突破", "粘り強い守備", "中盤のパスワーク"])
    with col4:
        style = st.selectbox("🛡️ 理想のプレースタイル", 
            ["ポゼッション（保持）", "ハイプレス（奪取）", "堅守速攻（カウンター）", "サイド攻撃特化"])

    st.markdown("---")
    st.markdown("### 3. 乗り越えたい『壁』と『モヤモヤ』")
    issues = st.text_area("🤔 今、解決したい課題やモヤモヤする場面は？", 
        placeholder="例：後半20分以降に足が止まって失点する。")

    submitted = st.form_submit_button("🚀 AI戦略アナリストに相談する")

if submitted:
    if not api_key:
        st.error("⚠️ APIキーが設定されていません。")
    else:
        try:
            genai.configure(api_key=api_key)
            # 安定性の高い最新モデルを使用
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f'''
            あなたは情熱的なサッカーデータアナリストです。
            以下の情報を元に、ワクワクを最大化し、壁を突破するための3つの重要指標(KR)を提案してください。
            【チーム情報】目標:{target}, ワクワク:{excitement}, 武器:{strengths}, スタイル:{style}, 課題:{issues}
            '''

            with st.spinner("AIが戦略を練っています... ⚽"):
                response = model.generate_content(prompt)
                st.balloons()
                st.success("戦略レポートが完成しました！")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
