import os
from openai import OpenAI

# 獲取環境變數
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise ValueError("Missing required environment variables: OPENAI_API_KEY or EXISTING_ASSISTANT_ID")

# 初始化 OpenAI 客戶端
client = OpenAI(api_key=API_KEY)

# 模擬簡單的助手邏輯
def ask_question(question):
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
    return run_result.get("messages")[-1]["content"]

# 測試範例
if __name__ == "__main__":
    question = "How long will it take us to be profitable?"
    answer = ask_question(question)
    print(f"Q: {question}\nA: {answer}")
