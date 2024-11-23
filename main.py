import os
from openai import OpenAI

# 從環境變數中讀取 API Key 和助手 ID（在 Vercel 上配置環境變數）
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

# 確保環境變數已正確配置
if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY or EXISTING_ASSISTANT_ID")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=API_KEY)

# 建立 Flask 伺服器（如果需要提供 HTTP 接口，適合 Vercel 部署）
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the OpenAI Assistant deployed on Vercel!"

@app.route("/ask", methods=["POST"])
def ask_assistant():
    try:
        # 獲取用戶輸入內容
        user_input = request.json.get("question")
        if not user_input:
            return jsonify({"error": "Missing 'question' in request"}), 400

        # 創建對話 Thread
        thread = client.beta.threads.create()

        # 添加用戶訊息
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        # 執行助手
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )

        # 獲取執行結果
        run_result = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )

        # 返回助手的回應
        assistant_reply = run_result.get("messages")[-1]["content"]
        return jsonify({"answer": assistant_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 運行伺服器（Vercel 自動管理埠號）
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
