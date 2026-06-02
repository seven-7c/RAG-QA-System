import ollama

def test_ollama_connection():
    try:
        response = ollama.chat(
            model="deepseek-r1:7b",
            messages=[
                {
                    "role": "user",
                    "content": "你好，请问你是谁？"
                }
            ]
        )
        print("Ollama连接测试成功！")
        print("模型响应:", response["message"]["content"])
        return True
    except Exception as e:
        print(f"Ollama连接失败: {e}")
        print("请确保Ollama已安装并运行，且deepseek-r1:7b模型已下载")
        return False

if __name__ == "__main__":
    test_ollama_connection()