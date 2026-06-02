import os
import docx
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_DB_PATH, EMBED_MODEL_NAME

def load_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text()
    return text

def load_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def load_document(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def load_documents_from_folder(folder_path):
    documents = []
    filenames = []
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                text = load_document(file_path)
                if text.strip():
                    documents.append(text)
                    filenames.append(filename)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return documents, filenames

def split_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.create_documents([text])
    return chunks

def build_vector_db(documents, filenames, db_path=VECTOR_DB_PATH):
    all_chunks = []
    
    for doc, filename in zip(documents, filenames):
        chunks = split_text(doc)
        for chunk in chunks:
            chunk.metadata["source"] = filename
        all_chunks.extend(chunks)
    
    embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME)
    
    if os.path.exists(db_path):
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
        vector_db.add_documents(all_chunks)
    else:
        vector_db = Chroma.from_documents(
            documents=all_chunks,
            embedding=embeddings,
            persist_directory=db_path
        )
    
    vector_db.persist()
    return vector_db

def get_retriever(db_path=VECTOR_DB_PATH, k=3):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME)
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return vector_db.as_retriever(search_kwargs={"k": k})

def query_similar_documents(query, db_path=VECTOR_DB_PATH, k=3):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL_NAME)
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    docs = vector_db.similarity_search(query, k=k)
    return docs