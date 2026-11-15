
import os
import re
import hashlib

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
# 2. Extract Text from Documents
# -----------------------------------

def extract_text(file_path):
    """Extract text from Markdown or PDF documents."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if file_path.lower().endswith(".pdf"):

        document = pymupdf.open(file_path)

        try:
            pages = [
                page.get_text()
                for page in document
            ]

            return "\n\n".join(pages)

        finally:
            document.close()

    elif file_path.lower().endswith(".md"):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    else:
        raise ValueError(
            "Unsupported document format."
        )


# -----------------------------------
# 3. Split Text into Meaningful Chunks
# -----------------------------------

def split_text(text, chunk_size=900, overlap=120):
    """
    Split documents into chunks while trying to keep
    headings and their related paragraphs together.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""
    current_section = "General"

    for paragraph in paragraphs:

        # Identify Markdown headings.
        heading_match = re.match(
            r"^#{1,6}\s+(.+)",
            paragraph
        )

        if heading_match:
            current_section = heading_match.group(1).strip()

        # Keep the section heading in the chunk.
        if heading_match and not current_chunk.strip():
            current_chunk = paragraph
            continue

        candidate = (
            current_chunk + "\n\n" + paragraph
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:

            current_chunk = candidate

        else:

            if current_chunk.strip():

                chunks.append({
                    "content": current_chunk.strip(),
                    "section": current_section
                })

            # Handle unusually long paragraphs.
            if len(paragraph) > chunk_size:

                start = 0

                while start < len(paragraph):

                    end = start + chunk_size

                    piece = paragraph[start:end].strip()

                    if piece:
                        chunks.append({
                            "content": piece,
                            "section": current_section
                        })

                    start += chunk_size - overlap

                current_chunk = ""

            else:

                current_chunk = paragraph

    if current_chunk.strip():

        chunks.append({
            "content": current_chunk.strip(),
            "section": current_section
        })

    return chunks


# -----------------------------------
# 4. Generate Embeddings
# -----------------------------------

def create_embedding(text):
    """Generate embeddings using the local Ollama model."""

    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]


# -----------------------------------
# 5. Add a Document to ChromaDB
# -----------------------------------

def add_document(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    text = extract_text(file_path)

    if not text.strip():
        raise ValueError(
            f"The document is empty: {file_path}"
        )

    chunks = split_text(text)

    if not chunks:
        raise ValueError(
            f"No usable chunks found: {file_path}"
        )

    filename = os.path.basename(file_path)

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    print(f"Creating embeddings for {filename}...")

    for index, chunk in enumerate(chunks):

        content = chunk["content"]

        embedding = create_embedding(content)

        ids.append(f"{filename}_{index}")

        documents.append(content)

        embeddings.append(embedding)

        metadatas.append({
            "source": filename,
            "chunk": index,
            "section": chunk["section"]
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Successfully added {len(chunks)} chunks "
        f"from {filename}."
    )


# -----------------------------------
# 6. Process All Knowledge Documents
# -----------------------------------

def process_knowledge_documents():

    data_folder = "data"

    if not os.path.isdir(data_folder):

        raise FileNotFoundError(
            "The data folder was not found."
        )

    supported_files = [
        filename
        for filename in os.listdir(data_folder)
        if filename.lower().endswith((".md", ".pdf"))
    ]

    if not supported_files:

        print("No Markdown or PDF documents found.")

        return

    print("\nProcessing knowledge documents...")

    for filename in sorted(supported_files):

        file_path = os.path.join(
            data_folder,
            filename
        )

        print(f"\nProcessing: {filename}")

        # Remove previous chunks for this document.
        old_results = collection.get(
            where={"source": filename}
        )

        old_ids = old_results["ids"]

        if old_ids:

            collection.delete(ids=old_ids)

            print("Removed previous document chunks.")

        # Add updated document content.
        add_document(file_path)

    print("\nAll knowledge documents processed.")

    print(
        "Total knowledge chunks:",
        collection.count()
    )


# -----------------------------------
# 7. Search the Knowledge Base
# -----------------------------------

def search_knowledge(query, results_count=3):
    """
    Search for relevant knowledge using semantic similarity.

    Returns content, source, chunk number, section,
    and ChromaDB distance for each retrieved result.
    """

    if not query or not query.strip():
        return []

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],

        n_results=min(
            results_count,
            total_chunks
        ),

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_chunks.append({

            "content": document,

            "source": metadata.get(
                "source",
                "Unknown"
            ),

            "chunk": metadata.get(
                "chunk",
                -1
            ),

            "section": metadata.get(
                "section",
                "General"
            ),

            "distance": distance

        })

    return retrieved_chunks


# -----------------------------------
# 8. Test Knowledge Retrieval
# -----------------------------------

def test_retrieval(query, test_name):

    print(f"\nTesting {test_name} retrieval...")

    results = search_knowledge(
        query,
        results_count=3
    )

    if not results:

        print("No results found.")

        return

    for index, result in enumerate(
        results,
        start=1
    ):

        print(f"\nResult {index}")

        print("Source:", result["source"])

        print("Section:", result["section"])

        print("Chunk:", result["chunk"])

        print("Distance:", result["distance"])

        print("Content:", result["content"])


# -----------------------------------
# 9. Main Execution
# -----------------------------------

if __name__ == "__main__":

    process_knowledge_documents()

    test_retrieval(
        "Website returning HTTP 503 Service Unavailable errors",
        "HTTP 503"
    )

    test_retrieval(
        "Application cannot connect to database. "
        "Database connection failure and network errors.",
        "Database"
    )

    test_retrieval(
        "Multiple users cannot log in. "
        "Authentication service timeout, identity provider "
        "unavailable, SSO and token validation errors.",
        "Authentication"
    )

    print("\nKnowledge base testing completed.")
