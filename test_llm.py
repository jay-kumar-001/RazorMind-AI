from langchain_ollama import ChatOllama
import time

llm = ChatOllama(model="qwen2.5:3b")

start = time.time()

response = llm.invoke("hello")

print(response.content)
print("TIME:", time.time() - start)