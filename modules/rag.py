import chromadb
from sentence_transformers import SentenceTransformer
import uuid

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_store")

# Split text into overlapping chunks.
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Embed and store document chunks in ChromaDB.
def build_knowledge_base(doc_id, text):
    collection = chroma_client.get_or_create_collection(name=doc_id)
    chunks = chunk_text(text)
    embeddings = embedding_model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    return len(chunks)

# Retrieve the most relevant chunks for a query.
def retrieve(doc_id, query, top_k=3):
    collection = chroma_client.get_or_create_collection(name=doc_id)
    query_embedding = embedding_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return "\n\n".join(results["documents"][0])