from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_data():
    # debales pages 
    urls = [
        "https://debales.ai/",
        "https://debales.ai/ecommerce",
        "https://debales.ai/logistics",
        "https://debales.ai/integrations",
        "https://debales.ai/ai-agent",
        "https://debales.ai/blog",
        "https://debales.ai/case-studies"
    ]

    loader = WebBaseLoader(urls)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )
    
    chunks = splitter.split_documents(docs)
    return chunks
