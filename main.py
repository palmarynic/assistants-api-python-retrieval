from dotenv import load_dotenv
import os
from openai import OpenAI

# Step 1. 加載環境變數
load_dotenv()

# 顯式提供 API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 假設您已有一個助手的 ID
EXISTING_ASSISTANT_ID = os.getenv("EXISTING_ASSISTANT_ID")

# Step 3. 創建一個對話 Thread
thread = client.beta.threads.create()

# Step 4. 建立用戶訊息
message = client.beta.threads.messages.create(
    thread_id=thread.id,  # 使用創建的 thread_id
    role="user",
    content="How long will it take us to be profitable at our current monthly revenue if it stays consistent and how long will it take to make back the startup costs?",
)
print(message)

# Step 5. 執行已存在的助手
run = client.beta.threads.runs.create(
    thread_id=thread.id,  # 使用創建的 thread_id
    assistant_id=EXISTING_ASSISTANT_ID  # 使用已存在的助手 ID
)
print(run)

# Step 6. 檢索執行結果
run_result = client.beta.threads.runs.retrieve(
    thread_id=thread.id,  # 使用創建的 thread_id
    run_id=run.id  # 使用步驟 5 的 run_id
)
print(run_result)
