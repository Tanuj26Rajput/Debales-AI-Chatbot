from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rag.ingest import load_data
from dotenv import load_dotenv
import os

load_dotenv()

def create_vectorstore():
    docs = load_data()

    # embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name = "intfloat/e5-small-v2",
        encode_kwargs = {"normalize_embeddings": True}
    )

    db = FAISS.from_documents(docs, embeddings)
    db.save_local("faiss_index")
    return db

def get_retriever():
    embeddings = HuggingFaceEmbeddings(
        model_name = "intfloat/e5-small-v2",
        encode_kwargs = {"normalize_embeddings": True}
    )
    # Reuse the saved FAISS index when it exists, otherwise build it once.
    if os.path.exists("faiss_index"):
        db = FAISS.load_local(
            "faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        db = create_vectorstore()

    return db.as_retriever()
