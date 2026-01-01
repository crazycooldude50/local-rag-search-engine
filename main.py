from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# 1. Configuration
DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"

app = FastAPI()

# 2. Load Resources (Done once when server starts)
print("Initializing Vector DB...")
embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL)
db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

print("Initializing LLM...")
llm = ChatOllama(model=LLM_MODEL)

# 3. Define the Prompt Template
prompt_template = ChatPromptTemplate.from_template("""
Answer the question based ONLY on the following context:
{context}

Question: {question}
""")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: QueryRequest):
    # Step A: Retrieve Context
    results = db.similarity_search(request.query, k=3)
    if not results:
        return {"answer": "I couldn't find any relevant information."}
    
    # Combine context
    context_text = "\n\n".join([doc.page_content for doc in results])
    
    # Step B: Generate Answer
    chain = prompt_template | llm
    response = chain.invoke({"context": context_text, "question": request.query})
    
    return {"answer": response.content, "sources": [doc.metadata for doc in results]}