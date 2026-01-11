from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(model="openai/gpt-oss-120b")

res = llm.invoke("Who is the CEO of Google?")

print(res.content)