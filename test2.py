import asyncio
import json

import aiohttp


async def invoke_chute():
    api_token = "cpk_ec375cb3e934458fbebeebaabf0b5ecb.542a8764df495fa59e86c4a846970e1e.6cFExcSFgaUIqv4ONzES5OQfIyhzUEWX"  # Thay bằng API token thực tế của bạn

    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json"
    }
    
    body = {
        "model": "deepseek-ai/DeepSeek-V3-0324",
        "messages": [
            {
                "role": "user",
                "content": "Tell me a 250 word story."
            }
        ],
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    items = []
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://llm.chutes.ai/v1/chat/completions", 
            headers=headers,
            json=body
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = data.strip()
                        # Kiểm tra chunk không rỗng và không phải "[]"
                        if chunk and chunk != "[]":
                            parsed_chunk = json.loads(chunk)
                            # Kiểm tra choices có dữ liệu không
                            if "choices" in parsed_chunk and parsed_chunk["choices"]:
                                item = parsed_chunk["choices"][0]["delta"]["content"]
                                if item:  # Chỉ thêm nếu item không rỗng
                                    print(item, end="", flush=True)
                                    # Ở đây bạn có thể xử lý item nếu cần, không print
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                    except Exception as e:
                        print(f"Error processing chunk: {e}")
    
    # Trả về câu hoàn chỉnh
    return "".join(items)

# Hàm main để chạy và lấy kết quả
async def main():
    await invoke_chute()
 # In câu hoàn chỉnh sau khi xong

if __name__ == "__main__":
    asyncio.run(main())