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

@app.route("/start", methods=["POST"])
def start_assistant():
    """
    啟動助手執行，立即返回 run_id 和 thread_id。
    """
    try:
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # 創建對話 Thread
        thread = client.beta.threads.create()

        # 添加用戶訊息
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        # 啟動助手執行
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )

        # 返回執行 ID 和執行狀態
        return jsonify({"thread_id": thread.id, "run_id": run.id, "status": run.status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status", methods=["GET"])
def check_status():
    """
    查詢助手執行狀態，並在完成時返回結果。
    """
    try:
        thread_id = request.args.get("thread_id")
        run_id = request.args.get("run_id")
        if not thread_id or not run_id:
            return jsonify({"error": "Missing 'thread_id' or 'run_id' in request"}), 400

        # 檢索執行結果
        run_result = wait_for_run_completion(thread_id=thread_id, run_id=run_id)

        # 提取回答
        assistant_reply = extract_assistant_reply(run_result)
        return jsonify({"status": "completed", "answer": assistant_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def wait_for_run_completion(thread_id, run_id, timeout=60, interval=5):
    """
    等待助手執行完成，並返回執行結果。
    - timeout: 最大等待時間（秒）
    - interval: 查詢間隔（秒）
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        run_result = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print("DEBUG: run_result status =", run_result.status)
        print("DEBUG: run_result tool_resources =", run_result.tool_resources)
        print("DEBUG: run_result truncation_strategy =", run_result.truncation_strategy)
        print("DEBUG: run_result metadata =", run_result.metadata)
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
        # 檢查 tool_resources 是否包含結果
        if run_result.tool_resources:
            print("DEBUG: Using tool_resources =", run_result.tool_resources)
            for tool_key, tool_data in run_result.tool_resources.items():
                if "result" in tool_data and "content" in tool_data["result"]:
                    return tool_data["result"]["content"]

        # 檢查 truncation_strategy.last_messages
        if run_result.truncation_strategy and run_result.truncation_strategy.last_messages:
            print("DEBUG: Using truncation_strategy.last_messages")
            last_message = run_result.truncation_strategy.last_messages[-1]
            if "content" in last_message:
                return last_message["content"]

        # 嘗試檢查其他可能的字段
        print("DEBUG: No valid content in known fields. Checking metadata...")
        if "metadata" in run_result and run_result.metadata:
            print("DEBUG: metadata =", run_result.metadata)
            return run_result.metadata.get("summary", "No valid content found in metadata")

        # 如果無法找到回答
        raise ValueError(f"No content found in tool_resources or other fields: {run_result}")
    except Exception as e:
        raise RuntimeError(f"Error while extracting assistant reply: {e}")

# Vercel 自動識別 `app`
app = app
