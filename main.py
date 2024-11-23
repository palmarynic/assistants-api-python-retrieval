import os
from openai import OpenAI

# 獲取環境變數
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY or EXISTING_ASSISTANT_ID")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=API_KEY)

# 主函數入口，作為 Vercel 無伺服器函數
def handler(event, context):
    try:
        # 測試問題
        question = event.get("question", "How long will it take us to be profitable?")
        
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
        return {"statusCode": 200, "body": assistant_reply}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
