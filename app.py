import streamlit as st
from google import genai

st.set_page_config(page_title="Soccer Strategy AI", page_icon="⚽", layout="wide")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ システム設定エラー：APIキーが設定されていません。")
    st.stop()

st.title("⚽ チーム戦略・KR診断システム")
st.markdown("チームの『主観（想い）』と映像データの『客観（事実）』を掛け合わせ、真の課題を抽出します。")

tab1, tab2 = st.tabs(["📋 ① 事前ヒアリング (仮説立案)", "📊 ② 動画分析フィードバック (確定診断)"])

# === タブ1：事前ヒアリング ===
with tab1:
    st.subheader("チームの現状認識と目指すスタイル")
    with st.form("pre_hearing_form"):
        col1, col2 = st.columns(2)
        with col1:
            style = st.selectbox("🛡️ スタイル", ["ポゼッション", "ハイプレス", "堅守速攻", "サイドアタック"])
            strengths = st.text_area("⚔️ 認識している『強み』", placeholder="例：中盤のパスワーク")
        with col2:
            issues = st.text_area("🤔 認識している『課題』", placeholder="例：終了間際の失点")
            excitement = st.text_area("✨ 『ワクワクする瞬間』", placeholder="例：パスを連動して相手を翻弄した時")
            
        submitted_pre = st.form_submit_button("🚀 分析すべき指標（仮説KR）を提案する")

    if submitted_pre:
        prompt_pre = f'''あなたはプロのスポーツアナリストです。以下の主観をもとに、今後の動画分析で「どの指標」に注目すべきか、3つの仮説KRを提案してください。
        スタイル:{style}, 強み:{strengths}, 課題:{issues}, ワクワク:{excitement}'''
        try:
            client = genai.Client(api_key=api_key)
            # 最新の「2.0」モデルを指定
            with st.spinner("事前の仮説KRを構築中..."):
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt_pre
                )
                st.success("事前診断が完了しました！")
                st.markdown(response.text)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            # 【探偵モード】何が使えるかGoogleに直接聞く
            try:
                client = genai.Client(api_key=api_key)
                available_models = [m.name for m in client.models.list() if 'gemini' in m.name]
                st.warning(f"💡 【調査結果】あなたのAPIキーで使えるモデルのリストはこちらです:\n{available_models}")
                st.info("※もしリストが空の場合は、APIキーを作成したプロジェクト自体に制限がかかっています。")
            except Exception:
                pass

# === タブ2：動画分析フィードバック ===
with tab2:
    st.subheader("分析結果とのギャップ検証")
    with st.form("post_analysis_form"):
        actual_data = st.text_area("📹 動画分析で判明した『実際のデータ』", placeholder="例：自陣パス成功率は高いが、敵陣への縦パスが少ない等", height=150)
        submitted_post = st.form_submit_button("🔥 ギャップを分析し、真のKRを確定する")

    if submitted_post:
        if not actual_data:
            st.warning("⚠️ 実際のデータを入力してください。")
        else:
            prompt_post = f'''あなたはプロのアナリストです。事前の自己認識と実際のデータを比較し、ギャップを指摘した上で、明日からの練習で追うべき『真のKR』を3つ提案して。
            【自己認識】スタイル:{style}, 強み:{strengths}, 課題:{issues}
            【実際のデータ】{actual_data}'''
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("ギャップ分析と最終KRを生成中..."):
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt_post
                    )
                    st.balloons()
                    st.success("最終レポートが完成しました！")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                # 【探偵モード】
                try:
                    client = genai.Client(api_key=api_key)
                    available_models = [m.name for m in client.models.list() if 'gemini' in m.name]
                    st.warning(f"💡 使えるモデルリスト:\n{available_models}")
                except Exception:
                    pass
