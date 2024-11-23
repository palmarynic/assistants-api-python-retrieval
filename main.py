from flask import Flask, request, jsonify
import os
from openai import OpenAI

# 初始化 Flask 應用
app = Flask(__name__)

# 環境變數
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY or EXISTING_ASSISTANT_ID")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=API_KEY)

@app.route("/", methods=["GET"])
def home():
    """健康檢查接口"""
    return jsonify({"message": "Welcome to the OpenAI Assistant deployed on Vercel!"})

@app.route("/ask", methods=["POST"])
def ask_assistant():
    """與 OpenAI 助手交互的主要接口"""
    try:
        # 獲取用戶的問題
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # 調用助手功能
        response = ask_openai_assistant(question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def ask_openai_assistant(question):
    """處理與 OpenAI 助手的交互"""
    try:
        # 創建對話 Thread
        thread = client.beta.threads.create()

        # 添加用戶訊息
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
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

        # 返回助手的回答
        assistant_reply = run_result.get("messages")[-1]["content"]

        return {"question": question, "answer": assistant_reply}
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with OpenAI Assistant: {e}")

# Vercel 自動識別 `app`
app = app
