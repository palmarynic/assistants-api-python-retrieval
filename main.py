import os
import json
from openai import OpenAI

# 初始化 OpenAI 客戶端
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY or EXISTING_ASSISTANT_ID")

client = OpenAI(api_key=API_KEY)

def handler(event, context):
    """
    Vercel 無伺服器函數的入口，實現 OpenAI 助手功能。
    """
    try:
        # 從請求中解析問題
        body = event.get("body", {})
        if isinstance(body, str):  # 如果是 JSON 字符串，轉換為字典
            body = json.loads(body)

        question = body.get("question")
        if not question:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'question' in request body"})
            }

        # 執行助手邏輯
        response = ask_openai_assistant(question)

        # 返回成功響應
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }
    except Exception as e:
        # 返回錯誤響應
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

def ask_openai_assistant(question):
    """
    與 OpenAI 助手交互並返回結果。
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

        # 獲取執行結果
        run_result = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )

        # 提取助手的回答
        assistant_reply = run_result.get("messages")[-1]["content"]

        return {"question": question, "answer": assistant_reply}
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with OpenAI Assistant: {e}")
