from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import os

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Pro",  # safer working model
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

model = ChatHuggingFace(llm=llm)

query = "what does debales ai do?"

prompt = f"""
You are a strict query classifier.

Classify the query into ONLY one category:

- rag → if the query is ONLY about Debales AI (its features, services, use cases)
- serp → if the query is general knowledge and NOT related to Debales AI
- both → if the query involves Debales AI AND any external concept, technology, company, or general knowledge

Important rules:
- Do NOT overuse "both"
- Use "both" when answering requires BOTH:
  (1) knowledge about Debales AI AND
  (2) external/general knowledge
- Not only for comparisons — also for:
  - similarities
  - explanations involving external concepts
  - broader context questions

Examples:

Query: What does Debales AI do?
Answer: rag

Query: Compare Debales AI with OpenAI
Answer: both

Query: Is Debales AI similar to ChatGPT?
Answer: both

Query: Does Debales AI use machine learning?
Answer: both

Query: Who is the CEO of Google?
Answer: serp

Query: {query}

Answer:
"""

response = model.invoke(prompt)
print(response.content.strip())