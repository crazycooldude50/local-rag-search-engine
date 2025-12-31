import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# CONFIGURATION
# ---------------------------------------------------------
# Where your PDF is located. Put a real PDF in your folder!
DOC_PATH = "monopoly.pdf" 

# The folder where the database will be saved on your disk
DB_PATH = "./chroma_db"

# The specific model we downloaded for embeddings
EMBEDDING_MODEL = "nomic-embed-text"
# ---------------------------------------------------------

def main():
    # 1. Check if file exists
    if not os.path.exists(DOC_PATH):
        print(f"Error: File '{DOC_PATH}' not found. Please add a PDF to the folder.")
        return

    print("Step 1: Loading PDF...")
    loader = PyPDFLoader(DOC_PATH)
    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} pages.")

    # 2. Split the Text (Chunking)
    # Why? LLMs have a limit on how much text they can read. 
    # Overlap ensures we don't cut a sentence in half and lose context.
    print("Step 2: Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # Characters per chunk
        chunk_overlap=80,     # Overlap to keep context between chunks
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Initialize the Vector Store (ChromaDB)
    # This connects to Ollama to turn text into numbers (Vectors)
    print("Step 3: Creating Vector Store (this may take a moment)...")
    embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # This line actually sends data to Ollama, gets vectors, and saves to disk
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=DB_PATH
    )
    
    print(f"Success! Database saved to {DB_PATH}")

if __name__ == "__main__":
    main()