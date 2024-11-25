from flask import Flask, request, jsonify
import os
import time
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
    """與 OpenAI 助手交互，檢索文件內的信息"""
    try:
        # 獲取用戶的問題
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # 調用助手功能
        response = query_openai_assistant(question)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def query_openai_assistant(question):
    """
    與 OpenAI 助手交互，從綁定的文件中檢索答案。
    """
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

        # 等待助手完成執行
        run_result = wait_for_run_completion(thread.id, run.id)

        # 提取助手的回答
        assistant_reply = extract_assistant_reply(run_result)
        return {"question": question, "answer": assistant_reply}
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve data from assistant: {e}")

def wait_for_run_completion(thread_id, run_id, timeout=60, interval=2):
    """
    等待助手執行完成，並返回執行結果。
    - timeout: 最大等待時間（秒）
    - interval: 查詢間隔（秒）
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        run_result = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print("DEBUG: run_result status =", run_result.status)
        if run_result.status == "completed":
            return run_result
        elif run_result.status in ["failed", "cancelled"]:
            raise RuntimeError(f"Run failed with status: {run_result.status}")
        time.sleep(interval)

    raise TimeoutError("Assistant run did not complete within the timeout period.")

def extract_assistant_reply(run_result):
    """
    提取助手的回答，根據返回數據的結構進行處理。
    """
    try:
        # 嘗試從完成的結果中提取 messages
        if hasattr(run_result, "messages"):
            return run_result.messages[-1]["content"]
        elif isinstance(run_result, dict) and "messages" in run_result:
            return run_result["messages"][-1]["content"]
        raise ValueError(f"Unexpected structure in completed run_result: {run_result}")
    except (IndexError, KeyError) as e:
        raise RuntimeError(f"Error while extracting assistant reply: {e}")

# Vercel 自動識別 `app`
app = app
