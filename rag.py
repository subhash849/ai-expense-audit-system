from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


import pdfplumber

def load_policy(path):
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


def chunk_text(text):
    lines = text.split("\n")
    chunks = []
    current_category = ""

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # detect category headers
        if ":" in line and len(line.split()) == 1:
            current_category = line.replace(":", "").lower()
            continue

        if len(line) > 20:
            chunk = f"{current_category}: {line}"
            chunks.append(chunk)

    return chunks

def build_index(chunks):
    embeddings = model.encode(chunks)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index, embeddings


def retrieve(query, chunks, index, k=1):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), k)

    return [chunks[i] for i in indices[0]]