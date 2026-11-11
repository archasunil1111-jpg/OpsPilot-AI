
import os
import ollama
import chromadb
import pymupdf


# -----------------------------------
# 1. Initialize ChromaDB
# -----------------------------------

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="incident_knowledge"
)


# -----------------------------------
# 2. Extract text from documents
# -----------------------------------

def extract_text(file_path):
    """Extract text from Markdown or PDF documents."""

    if file_path.lower().endswith(".pdf"):

        document = pymupdf.open(file_path)

        text = ""

        for page in document:
            text += page.get_text() + "\n"

        document.close()

        return text

    elif file_path.lower().endswith(".md"):

        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    else:
        raise ValueError("Unsupported document format")


# -----------------------------------
# 3. Split text into chunks
# -----------------------------------

def split_text(text, chunk_size=700, overlap=100):
    """Split text into smaller overlapping chunks."""

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------------
# 4. Generate embeddings
# -----------------------------------

def create_embedding(text):
    """Generate embeddings using local Ollama model."""

    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]


# -----------------------------------
# 5. Add documents to ChromaDB
# -----------------------------------

def add_document(file_path):
    """Extract, split, embed and store a document."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    text = extract_text(file_path)

    if not text.strip():
        raise ValueError("The document contains no extractable text.")

    chunks = split_text(text)

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.upsert(
            ids=[f"{os.path.basename(file_path)}_{index}"],

            documents=[chunk],

            embeddings=[embedding],

            metadatas=[{
                "source": os.path.basename(file_path),
                "chunk": index
            }]
        )

    print(f"Successfully added {len(chunks)} chunks.")


# -----------------------------------
# 6. Search the knowledge base
# -----------------------------------

def search_knowledge(query, results_count=3):
    """Retrieve relevant knowledge for an incident."""

    if collection.count() == 0:
        return []

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(results_count, collection.count())
    )

    retrieved_chunks = []

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):

        retrieved_chunks.append({
            "content": document,
            "source": metadata["source"],
            "chunk": metadata["chunk"]
        })

    return retrieved_chunks


# -----------------------------------
# 7. Main execution and testing
# -----------------------------------

if __name__ == "__main__":

    guide_path = os.path.join(
        "data",
        "incident_troubleshooting_guide.md"
    )

    print("Processing technical knowledge document...")

    add_document(guide_path)

    print("\nTesting knowledge retrieval...")

    test_query = "Website is returning HTTP 503 errors"

    results = search_knowledge(test_query)

    if results:

        for index, result in enumerate(results, start=1):

            print(f"\n--- Retrieved Result {index} ---")

            print("Source:", result["source"])

            print("Chunk:", result["chunk"])

            print("Content:", result["content"])

    else:
        print("No relevant knowledge found.")
