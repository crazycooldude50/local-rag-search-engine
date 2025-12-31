import argparse
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# CONFIGURATION
# ---------------------------------------------------------
DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
# ---------------------------------------------------------

def main():
    # 1. Prepare the DB Connection
    print("Loading database...")
    embedding_function = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_function)

    # 2. Get the Question from the User
    while True:
        print("\n" + "-"*40)
        query_text = input("Ask a question about your PDF (or type 'exit' to quit): ")
        
        if query_text.lower() == 'exit':
            break

        print(f"\nSearching for: '{query_text}'...")

        # 3. The Search (The Core Logic)
        # k=3 means "Give me the top 3 most relevant chunks"
        results = db.similarity_search(query_text, k=3)

        # 4. Show the Results
        if not results:
            print("No matches found.")
        else:
            print(f"Found {len(results)} relevant chunks:\n")
            for i, doc in enumerate(results):
                print(f"--- Result {i+1} ---")
                print(doc.page_content[:300] + "...") # Print first 300 chars
                print("\n")

if __name__ == "__main__":
    main()