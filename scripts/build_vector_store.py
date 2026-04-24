"""
FAISS Vector Store Builder
Build a FAISS vector index from extracted document texts

Usage:
    python build_vector_store.py
    python build_vector_store.py -i extracted_texts.json -o ~/.literature_kb
"""
import json
import argparse
from pathlib import Path
from typing import List, Dict
import os
import sys

# 设置 Hugging Face 镜像（优先国内镜像，失败则回退）
def setup_hf_mirror():
    """设置 Hugging Face 镜像源"""
    mirrors = [
        ('https://hf-mirror.com', '国内镜像'),
        ('https://huggingface.co', '官方源'),
    ]

    for url, name in mirrors:
        os.environ['HF_ENDPOINT'] = url
        try:
            import urllib.request
            urllib.request.urlopen(f"{url}/", timeout=5)
            return url
        except:
            continue

    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    return 'https://hf-mirror.com'

setup_hf_mirror()

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle


class VectorStore:
    """FAISS-based vector store for document retrieval"""

    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

        print("Loading embedding model...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.dimension = 384

        self.index = None
        self.documents = []
        self.metadata = []

    def build_index(self, texts: List[str], metadata: List[Dict]):
        print(f"Encoding {len(texts)} text chunks...")

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype('float32'))

        self.documents = texts
        self.metadata = metadata

        print(f"Built index with {self.index.ntotal} vectors")

    def save(self):
        faiss.write_index(self.index, str(self.store_dir / 'index.faiss'))

        with open(self.store_dir / 'data.pkl', 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)

        print(f"Saved vector store to {self.store_dir}")

    def load(self):
        self.index = faiss.read_index(str(self.store_dir / 'index.faiss'))

        with open(self.store_dir / 'data.pkl', 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']

        print(f"Loaded index with {self.index.ntotal} vectors")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        scores, indices = self.index.search(query_embedding.astype('float32'), k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(scores[0][i])
                })

        return results


def chunk_text(text: str, min_size: int = 100, max_size: int = 1000) -> List[str]:
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 <= max_size:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para
        else:
            if len(current_chunk) >= min_size:
                chunks.append(current_chunk)
            current_chunk = para

    if len(current_chunk) >= min_size:
        chunks.append(current_chunk)

    return chunks


def build_knowledge_base(extracted_path: str = None, store_dir: str = None):
    if extracted_path is None:
        extracted_path = Path.cwd() / 'extracted_texts.json'
    else:
        extracted_path = Path(extracted_path)

    if store_dir is None:
        store_dir = Path.home() / '.literature_kb'
    else:
        store_dir = Path(store_dir)

    print(f"Extracted texts: {extracted_path}")
    print(f"Vector store directory: {store_dir}")

    if not extracted_path.exists():
        print(f"Error: Extracted texts file not found: {extracted_path}")
        print("Please run extract_documents.py first")
        return

    print("Loading extracted texts...")
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extracted_texts = json.load(f)

    print("Chunking texts...")
    texts = []
    metadata = []

    for item in extracted_texts:
        filename = item['filename']
        text = item['text']
        item_metadata = item.get('metadata', {})
        file_type = item.get('file_type', 'pdf')

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadata.append({
                'filename': filename,
                'chunk_index': i,
                'title': item_metadata.get('title', ''),
                'author': item_metadata.get('author', ''),
                'file_type': file_type,
            })

    print(f"Created {len(texts)} text chunks")

    store = VectorStore(str(store_dir))
    store.build_index(texts, metadata)
    store.save()

    print("\n" + "=" * 60)
    print("Vector store build complete!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Build FAISS vector index from extracted document texts'
    )
    parser.add_argument(
        '-i', '--input',
        help='Input JSON file path (default: ./extracted_texts.json)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Vector store directory (default: ~/.literature_kb)'
    )

    args = parser.parse_args()

    build_knowledge_base(
        extracted_path=args.input,
        store_dir=args.output
    )


if __name__ == '__main__':
    main()
