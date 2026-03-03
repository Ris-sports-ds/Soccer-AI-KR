import streamlit as st
from google import genai
import requests

# ページ全体の設定
st.set_page_config(page_title="Soccer Strategy AI | 立正大学", page_icon="⚽", layout="wide")

# 🔑 【設定】合言葉はキャンパス住所
AUTH_PASSWORD = "magechi1700" 

# 📊 【Googleフォーム連携設定：完了済み】
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdxx_zBrf1bGgitplGxVAFl5boen6K2GixpBL3xrgPd9WzldQ/formResponse"

ENTRY_TEAM_NAME = "entry.1241656852"
ENTRY_STYLE = "entry.103383635"
ENTRY_ISSUES = "entry.107545070"
ENTRY_AI_RESULT = "entry.617877957"
ENTRY_ACTUAL_DATA = "entry.1793778765"
ENTRY_CONSENT = "entry.548337174"

# 🎓 立正大学スポーツデータサイエンス研究室ブランディング
st.markdown("<div style='text-align: right; color: #666; font-size: 0.9em;'>🎓 開発：立正大学スポーツデータサイエンス研究室</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 立正大学\n**スポーツデータサイエンス研究室**")
    st.caption("AIとデータを使って、市民スポーツをさらに楽しく、熱くするプロジェクトです。")
    st.divider()
    st.markdown("### 🔐 セキュリティ")
    user_password = st.text_input("合言葉を入力してください", type="password")
    st.divider()
    st.markdown("📱 **仲間へのシェア方法**\n「ダウンロード」ボタンから保存してLINE等で共有してください。")

# APIキー取得
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ システム設定エラー：APIキーが設定されていません。")
    st.stop()

if user_password != AUTH_PASSWORD:
    if user_password == "":
        st.info("👈 左側のサイドバーに「合言葉」を入力して開始してください。")
    else:
        st.error("❌ 合言葉が違います。")
    st.stop()

st.title("⚽ チーム戦略・KR診断システム")

# 🛡️ 研究倫理に関する詳細な説明（アカデミック版）
with st.expander("🔬 学術研究・教育活動へのデータ利用に関する説明（必ずお読みください）"):
    st.write("""
    **1. 研究の目的と活用方法** 本システムを通じて収集されたデータ（チームの課題、AIによる提案内容、分析結果等）は、立正大学スポーツデータサイエンス研究室において、スポーツパフォーマンスの最適化やコーチング指標（KPI/OKR）の有効性に関する研究に活用させていただきます。成果は学会発表、学術論文、および教育的著作物（書籍等）として公表する場合があります。

    **2. プライバシーの保護（匿名化の徹底）** 収集したデータからチーム名や個人名などの特定可能な情報はすべて削除し、統計的な数値や「チームA」といった符号に置き換えて処理します。公表に際して第三者に個別の情報が漏れることはありません。

    **3. 同意の任意性と撤回について** データの研究利用への同意は任意です。同意いただけない場合でも、本アプリのすべての機能をご利用いただけます。また、一度同意いただいた後でも、研究室までご連絡いただければデータの使用を停止し、削除いたします。

    **4. お問い合わせ先** 立正大学スポーツデータサイエンス研究室（責任者：データサイエンス学部 准教授）
    """)

st.warning("⚠️ **【ご注意】** 個人名、住所、電話番号などの機密性の高い個人情報は絶対に入力しないでください。")

tab1, tab2 = st.tabs(["📋 ① 事前ヒアリング (目標づくり)", "📊 ② 動画分析フィードバック (作戦会議)"])

# === タブ1：事前ヒアリング ===
with tab1:
    st.subheader("チームの今の状態と、目指すスタイルを教えてください")
    with st.form("pre_hearing_form"):
        col1, col2 = st.columns(2)
        with col1:
            team_name = st.text_input("🚩 チーム名", placeholder="例：立正熊谷サッカー団")
            style = st.text_input("🛡️ 理想のスタイル", placeholder="例：ポゼッション、前線からのハイプレスなど")
            strengths = st.text_area("⚔️ 自分たちの『強み』", placeholder="例：ドリブル突破できる選手が多い")
        with col2:
            issues = st.text_area("🤔 悩んでいること・課題", placeholder="例：立ち上がりの失点が多い")
            excitement = st.text_area("✨ ワクワクする瞬間", placeholder="例：パスが綺麗に繋がって相手を崩した時")
        
        st.divider()
        st.markdown("📑 **研究利用への同意**")
        consent_research = st.checkbox("上記「学術研究・教育活動へのデータ利用に関する説明」を理解・同意し、研究室へ映像分析を依頼します。")
        
        submitted_pre = st.form_submit_button("🚀 AIスポーツアナリストに相談する")

    if submitted_pre:
        if consent_research and not team_name:
            st.error("分析を依頼する場合は「チーム名」を必ず入力してください。")
        else:
            # 🤖 プロンプト必須5条件
            prompt_pre = f'''あなたは立正大学スポーツデータサイエンス研究室の「AIスポーツアナリスト」です。丁寧な「です・ます調」で回答してください。
            以下のルールを厳守してください：
            1. 冒頭で「**KR（Key Result）とは、チームの目標を達成するための具体的な数値指標（目印）のことです。**」と簡潔に説明する。
            2. 動画分析で注目すべき「3つの仮説KR」を提案する。
            3. プロ視点の「奥深い指標（例：セカンドボール回収率、デュエル勝率、即時奪回率など）」を積極的に組み込む。
            4. 専門用語には必ず（こぼれ球を拾う確率など）初心者にもわかる優しい解説を添える。
            5. 各KRの理由は、シンプルに2〜3文程度でまとめる。

            チーム名:{team_name}, スタイル:{style}, 強み:{strengths}, 課題:{issues}, ワクワク:{excitement}'''
            
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("分析中..."):
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_pre)
                    ai_text = response.text
                    st.success("✨ 事前診断が完了しました！")
                    st.markdown(ai_text)
                    
                    if consent_research:
                        payload = {ENTRY_TEAM_NAME: team_name, ENTRY_STYLE: style, ENTRY_ISSUES: issues, ENTRY_AI_RESULT: ai_text, ENTRY_CONSENT: "同意する（タブ1実行時）"}
                        requests.post(FORM_URL, data=payload)
                        st.toast("✅ 研究室へデータを共有しました！", icon="📩")
                    
                    st.download_button(label="📝 結果を保存（LINE共有用）", data=ai_text, file_name=f"{team_name}_事前診断.txt")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# === タブ2：動画分析フィードバック ===
with tab2:
    st.subheader("実際のデータを見て、作戦会議をしましょう")
    with st.form("post_analysis_form"):
        actual_team_name = st.text_input("🚩 チーム名（再入力）", key="tab2_team")
        actual_data = st.text_area("📹 動画分析でわかった『実際のデータ』", height=150)
        st.divider()
        st.markdown("📑 **研究利用への同意**")
        consent_share = st.checkbox("上記「学術研究・教育活動へのデータ利用に関する説明」を理解・同意し、診断結果を研究室と共有します。")
        submitted_post = st.form_submit_button("🔥 ギャップを分析し、目標を確定する")

    if submitted_post:
        prompt_post = f'''立正大学スポーツデータサイエンス研究室の「AIスポーツアナリスト」として回答してください。
        1. 冒頭で「KR（Key Result）とは〜」と説明を入れる。
        2. 理想と現実のギャップを指摘する。
        3. 明日からの『真のKR』を3つ提案する。
        4. 奥深い専門指標（セカンドボール回収率など）を含め、必ず優しい解説を添える。
        5. 理由はシンプルにまとめる。
        
        【実際のデータ】{actual_data}'''
        
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("分析中..."):
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_post)
                final_text = response.text
                st.balloons()
                st.success("✨ 最終レポートが完成しました！")
                st.markdown(final_text)
                
                if consent_share:
                    payload_post = {ENTRY_TEAM_NAME: actual_team_name, ENTRY_ACTUAL_DATA: actual_data, ENTRY_AI_RESULT: final_text, ENTRY_CONSENT: "同意する（タブ2実行時）"}
                    requests.post(FORM_URL, data=payload_post)
                    st.toast("✅ 研究室に分析結果を共有しました！", icon="📊")
                st.download_button(label="📝 結果を保存", data=final_text, file_name="最終レポート.txt")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
