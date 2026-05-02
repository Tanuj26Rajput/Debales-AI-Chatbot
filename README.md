# Debales AI Chatbot

A LangGraph-based AI assistant for answering questions about Debales AI. The chatbot uses Retrieval-Augmented Generation (RAG) for Debales-specific questions, SerpAPI/Google Search for general questions, and both sources for mixed questions.

## Objective

This project was built for the Debales AI intern assignment. It implements:

- RAG over Debales AI website pages
- SERP API tool calling for external/general queries
- A LangGraph workflow that routes each query to the correct path
- A CLI chatbot interface
- Debug logs that show which path the system is taking

## Architecture

```text
User question
    |
    v
app.py
    |
    v
LangGraph workflow
    |
    v
router_node
    |
    +-- rag  --> rag_node  --> final_node --> answer
    |
    +-- serp --> serp_node --> final_node --> answer
    |
    +-- both --> both_node --> final_node --> answer
```

## How Routing Works

Routing is handled in `bot_utils/router.py`.

The router classifies each query into one of three categories:

- `rag`: Questions only about Debales AI
- `serp`: General questions not related to Debales AI
- `both`: Questions that need both Debales AI knowledge and outside/general information

Example routing:

```text
What does Debales AI do?
-> rag

Who is the CEO of Google?
-> serp

Is Debales AI similar to ChatGPT?
-> both
```

The selected route is printed in the terminal:

```text
[router] route selected: rag
```

## RAG Flow

RAG files:

- `rag/ingest.py`
- `rag/retriever.py`

`rag/ingest.py` loads Debales AI website pages using `WebBaseLoader`.

Current pages:

- `https://debales.ai/`
- `https://debales.ai/ecommerce`
- `https://debales.ai/logistics`
- `https://debales.ai/integrations`
- `https://debales.ai/ai-agent`
- `https://debales.ai/blog`
- `https://debales.ai/case-studies`

The loaded documents are split into chunks using `RecursiveCharacterTextSplitter`.

`rag/retriever.py` creates embeddings using:

```text
intfloat/e5-small-v2
```

The embeddings are stored in a local FAISS vector index:

```text
faiss_index/
```

On later runs, the app loads the saved FAISS index instead of rebuilding it every time.

When a RAG query is received, the workflow performs maximum marginal relevance search and retrieves the most relevant Debales chunks:

```text
[rag] searching Debales knowledge base...
[rag] retrieved 5 document chunks
```

## SERP / Google Search Flow

SERP files:

- `bot_tools/serp_tool.py`

For non-Debales queries, the workflow uses SerpAPI through LangChain's `SerpAPIWrapper`.

Before searching, the query is rewritten into a more search-friendly version:

```text
[serp] rewriting query for Google search...
[serp] searching Google for: ...
[serp] search complete
```

The tool collects the top organic result snippets and source links. If no organic results are found, it checks SerpAPI's answer box.

## Mixed Query Flow

Mixed queries use both RAG and SERP.

Example:

```text
Is Debales AI similar to ChatGPT?
```

The workflow:

1. Searches the Debales FAISS knowledge base
2. Searches Google through SerpAPI
3. Combines both contexts
4. Sends the combined context to the final answer node

Debug output:

```text
[both] searching Debales knowledge base and Google...
[both:rag] retrieved 5 document chunks
[both:serp] searching Google for: ...
[both] combined RAG and SERP context
```

## Final Answer Generation

Final answer generation happens in `final_node` inside `graph/workflow.py`.

The model is instructed to answer only from the retrieved context:

```text
Use ONLY the provided context.
If answer is not present, say "I don't know".
```

This helps reduce hallucination and keeps the response grounded in either:

- Debales AI website content
- SERP search results
- Both sources together

## Project Structure

```text
.
|-- app.py
|-- README.md
|-- requirements.txt
|-- .env.example
|-- bot_utils/
|   |-- llm.py
|   `-- router.py
|-- bot_tools/
|   `-- serp_tool.py
|-- graph/
|   `-- workflow.py
|-- rag/
|   |-- ingest.py
|   `-- retriever.py
`-- faiss_index/
```

Important files:

- `app.py`: CLI entry point
- `bot_utils/llm.py`: Hugging Face LLM configuration
- `bot_utils/router.py`: Query classification logic
- `graph/workflow.py`: LangGraph nodes and edges
- `rag/ingest.py`: Debales website loading and chunking
- `rag/retriever.py`: Embeddings and FAISS retriever
- `bot_tools/serp_tool.py`: SerpAPI search tool

## Setup

### 1. Clone or open the project

```bash
cd "Debales AI Chatbot"
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then fill in:

```env
HUGGINGFACEHUB_API_TOKEN="your_huggingface_access_token"
SERPAPI_API_KEY="your_serpapi_api_key"
```

## How To Run

Run the CLI chatbot:

```bash
python app.py
```

Then ask a question:

```text
Ask something: What does Debales AI do?
```

Example debug output:

```text
[router] route selected: rag
[rag] searching Debales knowledge base...
[rag] retrieved 5 document chunks
[final] generating final answer from retrieved context...
[final] answer generated
```

## Example Prompts

Debales-only query:

```text
What does Debales AI do?
```

Expected route:

```text
rag
```

General query:

```text
Who is the CEO of Google?
```

Expected route:

```text
serp
```

Mixed query:

```text
Is Debales AI similar to ChatGPT?
```

Expected route:

```text
both
```

Unknown query:

```text
What is Debales AI's exact annual revenue?
```

Expected behavior:

```text
The assistant should say it does not know if the answer is not present in the retrieved context.
```

## Notes

- The first run can take longer because the app may scrape Debales pages and build the FAISS index.
- If `faiss_index/` already exists, the app loads the saved vector database.
- If `SERPAPI_API_KEY` is missing, external search will return a configuration message.
- The app is a simple CLI, but the LangGraph workflow can be reused in a web UI later.

## Assignment Coverage

| Requirement | Status |
| --- | --- |
| RAG over Debales AI content | Implemented |
| SERP API for external queries | Implemented |
| LangGraph workflow | Implemented |
| Debales queries route to RAG | Implemented |
| Non-Debales queries route to SERP | Implemented |
| Mixed queries use both | Implemented |
| No hallucination instruction | Implemented in final prompt |
| CLI or simple UI | CLI implemented |
| `.env.example` | Included |
| README setup instructions | Included |

