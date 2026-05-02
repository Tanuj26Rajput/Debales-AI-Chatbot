from bot_utils.llm import model 

def route_query(query): 
    # it decides which knowledge source to use.
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

    decision = model.invoke(prompt).content.strip().lower() 
    if decision == "both": 
        return "both" 
    elif decision == "rag": 
        return "rag" 
    else: 
        return "serp"
