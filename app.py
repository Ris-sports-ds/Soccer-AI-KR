import streamlit as st
from google import genai

# ページ全体の設定
st.set_page_config(page_title="Soccer Strategy AI | 立正大学", page_icon="⚽", layout="wide")

# 🎓 ブランディング（右上とサイドバーに表示）
st.markdown("<div style='text-align: right; color: #666; font-size: 0.9em;'>🎓 開発：立正大学スポーツデータサイエンス研究室</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎓 立正大学\n**スポーツデータサイエンス研究室**")
    st.caption("AIとデータを使って、市民スポーツをさらに楽しく、熱くするプロジェクトです。")
    st.divider()
    st.markdown("📱 **仲間へのシェア方法**\n各診断結果の下にある「ダウンロード」ボタンからテキストを保存して、LINEに貼り付けると簡単に共有できます。")

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ システム設定エラー：APIキーが設定されていません。")
    st.stop()

st.title("⚽ チーム戦略・KR診断システム")
st.markdown("チームの『想い（ワクワク）』と、映像からわかる『事実（データ）』を掛け合わせて、明日からの目標を一緒に見つけましょう！")

tab1, tab2 = st.tabs(["📋 ① 事前ヒアリング (目標づくり)", "📊 ② 動画分析フィードバック (作戦会議)"])

# === タブ1：事前ヒアリング ===
with tab1:
    st.subheader("チームの今の状態と、目指すスタイルを教えてください")
    with st.form("pre_hearing_form"):
        col1, col2 = st.columns(2)
        with col1:
            style = st.selectbox("🛡️ 理想のスタイル", ["ポゼッション (ボールを大切に繋ぐ)", "ハイプレス (前からどんどん奪う)", "堅守速攻 (しっかり守って素早く攻める)", "サイドアタック (サイドから崩す)"])
            strengths = st.text_area("⚔️ 自分たちの『強み』", placeholder="例：中盤のパスワーク、最後まで走る体力")
        with col2:
            issues = st.text_area("🤔 悩んでいること・『課題』", placeholder="例：立ち上がりの失点、シュートが決まらない")
            excitement = st.text_area("✨ プレーしていて『最高にワクワクする瞬間』", placeholder="例：パスが綺麗に繋がって相手を崩した時")
            
        submitted_pre = st.form_submit_button("🚀 AIコーチに相談して、注目するデータを見つける")

    if submitted_pre:
        # 🤖 プロンプトのトーンを「優しく寄り添う」形に大幅修正
        prompt_pre = f'''あなたは立正大学スポーツデータサイエンス研究室が開発した、優しくて頼りになるAIスポーツアナリストです。
        小学生やサッカー初心者にもわかりやすい言葉遣いで、上から目線ではなく「〜してみるのはどうかな？」「〜を意識してみよう！」といった温かく寄り添うトーンで話してください。
        専門用語（KRなど）を使う場合は、「KR（目標を達成するための具体的な数字）」のように簡単な解説をつけてください。
        以下のチームの状況をもとに、今後の動画分析で「どんな数字」に注目すべきか、3つの仮説KRを提案してください。
        スタイル:{style}, 強み:{strengths}, 課題:{issues}, ワクワク:{excitement}'''
        
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("チームにぴったりの目標を考えています..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_pre
                )
                st.success("✨ 事前診断が完了しました！")
                st.markdown(response.text)
                
                # ⚠️ AIの免責事項
                st.info("⚠️ **【AIコーチからのアドバイスについて】**\nこの結果はAIがデータをもとに考えたヒントです。絶対の正解ではないので、チームの仲間や監督と話し合うための『叩き台』として使ってくださいね！")
                
                # 📱 ダウンロード＆印刷案内
                st.download_button(label="📝 結果をテキストで保存（LINE共有用）", data=response.text, file_name="事前診断レポート.txt", mime="text/plain")
                st.caption("💡 PDFで綺麗に保存したい場合は、ブラウザのメニューから「印刷」→「PDFとして保存」を選んでください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# === タブ2：動画分析フィードバック ===
with tab2:
    st.subheader("実際のデータを見て、作戦会議をしよう")
    with st.form("post_analysis_form"):
        actual_data = st.text_area("📹 動画分析でわかった『実際のデータ』", placeholder="例：自陣パス成功率は90%だったけど、相手ゴール前への縦パスは0回だった。", height=150)
        submitted_post = st.form_submit_button("🔥 ギャップを分析し、明日からの練習目標を決める")

    if submitted_post:
        if not actual_data:
            st.warning("⚠️ 実際のデータを入力してくださいね。")
        else:
            # 🤖 プロンプトのトーンを修正
            prompt_post = f'''あなたは立正大学スポーツデータサイエンス研究室が開発した、優しくて頼りになるAIアナリストです。
            小学生や初心者にもわかりやすい言葉で、寄り添うトーンで話してください。
            チームの「自分たちが思っていたこと」と、実際の映像から出た「リアルなデータ」を比べて、「実はこんなギャップがあったよ！」と優しく気づきを与えてください。
            その上で、明日からの練習で意識すべき具体的な『真のKR（具体的な数字の目標）』を3つ提案してください。最後は前向きに励ましてください。
            【自己認識】スタイル:{style}, 強み:{strengths}, 課題:{issues}
            【実際のデータ】{actual_data}'''
            
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("ギャップを分析して、最終レポートを作成中..."):
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_post
                    )
                    st.balloons()
                    st.success("✨ 最終レポートが完成しました！")
                    st.markdown(response.text)
                    
                    # ⚠️ AIの免責事項
                    st.info("⚠️ **【AIコーチからのアドバイスについて】**\nこの結果はAIがデータをもとに考えたヒントです。これを参考に、自分たちに一番合った練習方法を見つけていきましょう！")
                    
                    # 📱 ダウンロード＆印刷案内
                    st.download_button(label="📝 結果をテキストで保存（LINE共有用）", data=response.text, file_name="動画分析レポート.txt", mime="text/plain")
                    st.caption("💡 PDFで綺麗に保存したい場合は、ブラウザのメニューから「印刷」→「PDFとして保存」を選んでください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
