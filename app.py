import streamlit as st
from google import genai

# ページ全体の設定
st.set_page_config(page_title="Soccer Strategy AI | 立正大学", page_icon="⚽", layout="wide")

# 🔑 【設定】合言葉を「万吉1700」に設定しました
AUTH_PASSWORD = "magechi1700" 

# 🎓 ブランディング
st.markdown("<div style='text-align: right; color: #666; font-size: 0.9em;'>🎓 開発：立正大学スポーツデータサイエンス研究室</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 立正大学\n**スポーツデータサイエンス研究室**")
    st.caption("AIとデータを使って、市民スポーツをさらに楽しく、熱くするプロジェクトです。")
    st.divider()
    
    # 🔐 セキュリティ：合言葉入力
    st.markdown("### 🔐 セキュリティ")
    user_password = st.text_input("合言葉を入力してください", type="password")
    
    st.divider()
    st.markdown("📱 **仲間へのシェア方法**\n各診断結果の下にある「ダウンロード」ボタンからテキストを保存して、LINEに貼り付けると簡単に共有できます。")

# APIキーの取得
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ システム設定エラー：APIキーが設定されていません。")
    st.stop()

# ---------------------------------------------------------
# 🛡️ 合言葉チェック
# ---------------------------------------------------------
if user_password != AUTH_PASSWORD:
    if user_password == "":
        st.info("👈 左側のサイドバーに「合言葉」を入力して、システムを開始してください。")
    else:
        st.error("❌ 合言葉が違います。正しい言葉を入力してください。")
    st.stop()

# ---------------------------------------------------------
# ✅ メインコンテンツ（合言葉が正しい時のみ表示）
# ---------------------------------------------------------

st.title("⚽ チーム戦略・KR診断システム")

# ⚠️ 個人情報に関する注意喚起
st.warning("⚠️ **【入力に関するご注意】**\n分析の精度を高めるため、チーム名や戦術は詳しく入力いただけますが、**個人名、住所、電話番号などの機密性の高い個人情報は絶対に入力しないでください。**")

st.markdown("チームの『想い（ワクワク）』と、映像からわかる『事実（データ）』を掛け合わせて、明日からの目標を一緒に見つけましょう。")

tab1, tab2 = st.tabs(["📋 ① 事前ヒアリング (目標づくり)", "📊 ② 動画分析フィードバック (作戦会議)"])

# === タブ1：事前ヒアリング ===
with tab1:
    st.subheader("チームの今の状態と、目指すスタイルを教えてください")
    with st.form("pre_hearing_form"):
        col1, col2 = st.columns(2)
        with col1:
            style = st.text_input("🛡️ 理想のスタイル・こだわりの戦術", placeholder="例：ポゼッション、前線からのハイプレス、サイド攻撃、または独自のスタイル")
            strengths = st.text_area("⚔️ 自分たちの『強み』", placeholder="例：中盤のパスワーク、最後まで走る体力")
        with col2:
            issues = st.text_area("🤔 悩んでいること・『課題』", placeholder="例：立ち上がりの失点、シュートが決まらない")
            excitement = st.text_area("✨ プレーしていて『最高にワクワクする瞬間』", placeholder="例：パスが綺麗に繋がって相手を崩した時")
            
        submitted_pre = st.form_submit_button("🚀 AIスポーツアナリストに相談する")

    if submitted_pre:
        prompt_pre = f'''あなたは立正大学スポーツデータサイエンス研究室が開発した「AIスポーツアナリスト」です。
        丁寧な「です・ます調」で回答してください。
        
        以下のルールを厳守して出力してください：
        1. 冒頭で必ず「**KR（Key Result）とは、チームの目標を達成するための具体的な数値指標（目印）のことです。**」と簡潔な説明を入れる。
        2. 以下のチームの状況をもとに、今後の動画分析で注目すべき「3つの仮説KR」を提案する。
        3. 【重要】プロのアナリストならではの視点として、初心者では思いつきにくいが勝敗に直結する「奥深い指標（例：セカンドボール回収率、デュエル勝率、ボールを失った直後の即時奪回率、決定機を生み出すチャンスクリエイト数など）」も積極的にKRに組み込むこと。
        4. 【重要】その際、専門用語には必ず（こぼれ球を拾う確率、1対1の勝負など）初心者にもわかる優しい解説を添えること。
        5. 各KRの提案理由は、長文を避け、シンプルでわかりやすく（2〜3文程度で）まとめる。

        【チームの情報】
        スタイル・戦術:{style}, 強み:{strengths}, 課題:{issues}, ワクワク:{excitement}'''
        
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("分析中..."):
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_pre)
                st.success("✨ 事前診断が完了しました！")
                st.markdown(response.text)
                st.info("⚠️ **【AIスポーツアナリストからのアドバイスについて】**\nこの結果はAIがデータをもとに考えたヒントです。絶対の正解ではないので、チームの話し合いの『叩き台』として活用してください。")
                st.download_button(label="📝 結果を保存（LINE共有用）", data=response.text, file_name="事前診断レポート.txt", mime="text/plain")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# === タブ2：動画分析フィードバック ===
with tab2:
    st.subheader("実際のデータを見て、作戦会議をしましょう")
    with st.form("post_analysis_form"):
        actual_data = st.text_area("📹 動画分析でわかった『実際のデータ』", placeholder="例：自陣パス成功率は90%だったが、相手ゴール前への縦パスは0回だった。", height=150)
        submitted_post = st.form_submit_button("🔥 ギャップを分析し、目標を確定する")

    if submitted_post:
        prompt_post = f'''あなたは立正大学スポーツデータサイエンス研究室が開発した「AIスポーツアナリスト」です。
        シンプルかつ丁寧な「です・ます調」で回答してください。
        
        以下のルールを厳守して出力してください：
        1. 冒頭で「**KR（Key Result）とは、チームの目標を達成するための具体的な数値指標（目印）のことです。**」と簡潔な説明を入れる。
        2. チームの「自己認識」と映像からの「実際のデータ」を比較し、客観的なギャップを的確に指摘する。
        3. 明日からの練習で意識すべき具体的な『真のKR』を3つ提案する。
        4. 【重要】提案するKRには、プロ視点の奥深い指標（セカンドボール回収率、デュエル勝率など）を含め、必ず初心者にわかる優しい言葉で解説を添えること。
        5. 各KRの理由は長文を避け、シンプルにまとめる。

        【自己認識】スタイル・戦術:{style}, 強み:{strengths}, 課題:{issues}
        【実際のデータ】{actual_data}'''
        
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("最終レポートを作成中..."):
                response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_post)
                st.balloons()
                st.success("✨ 最終レポートが完成しました！")
                st.markdown(response.text)
                st.download_button(label="📝 結果を保存（LINE共有用）", data=response.text, file_name="動画分析レポート.txt", mime="text/plain")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
