from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
import os

# 1. Configuration
# We use an environment variable for the base URL. 
# If running locally, it defaults to localhost. If in Docker, we will change it.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load Resources (Done once when server starts)
print("Initializing Vector DB...")
embedding_function = OllamaEmbeddings(
    model=EMBEDDING_MODEL, 
    base_url=OLLAMA_BASE_URL
)
db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

print("Initializing LLM...")
llm = ChatOllama(
    model=LLM_MODEL, 
    base_url=OLLAMA_BASE_URL 
)

# 3. Define the Prompt Template
# 3. Define the Prompt Template
prompt_template = ChatPromptTemplate.from_template("""
You are a helpful AI assistant. You are given a context that may contain information from multiple different documents.
Your goal is to answer the user's question accurately.

Instructions:
1. Look for the specific answer in the context below.
2. If the context contains information about different topics (e.g., different games or subjects), ONLY use the part that is relevant to the user's question.
3. Do not mention "the provided context" or "documents" in your answer. Just answer the question directly.

Context:
{context}

Question: {question}
""")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: QueryRequest):
    # Step A: Retrieve Context
    results = db.similarity_search(request.query, k=5)
    if not results:
        return {"answer": "I couldn't find any relevant information."}
    
    # Combine context
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    # Step B: Generate Answer
    chain = prompt_template | llm
    response = chain.invoke({"context": context_text, "question": request.query})
    
    return {"answer": response.content, "sources": [doc.metadata for doc in results]}