import tkinter as tk
from tkinter import filedialog, scrolledtext
import numpy as np
import ollama
from pypdf import PdfReader
from docx import Document
import os

# ---- App data ----
chunks = []
chunk_embeddings = []

# ---- Embedding utils ----
def get_embedding(text):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return np.array(response["embedding"])

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ---- Core logic ----
def load_document():
    global chunks, chunk_embeddings
    path = filedialog.askopenfilename(filetypes=[("Documents", "*.pdf *.txt *.docx")])
    if not path:
        return

    text = ""
    if path.endswith(".pdf"):
        reader = PdfReader(path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif path.endswith(".txt"):
        text = open(path, "r", encoding="utf-8").read()
    elif path.endswith(".docx"):
        doc = Document(path)
        for p in doc.paragraphs:
            text += p.text + "\n"

    # Split into small chunks
    chunks = [text[i:i + 800] for i in range(0, len(text), 800)]
    chat_box.insert(tk.END, f"📄 Loaded {len(chunks)} chunks from {os.path.basename(path)}\n", "info")

    # Compute embeddings
    chunk_embeddings = [get_embedding(chunk) for chunk in chunks]
    chat_box.insert(tk.END, "✅ Document embedded successfully!\n\n", "info")

def ask():
    query = entry.get().strip()
    if not query:
        return
    entry.delete(0, tk.END)

    if not chunks:
        chat_box.insert(tk.END, "⚠️ Load a document first.\n", "warning")
        return

    query_emb = get_embedding(query)
    similarities = [cosine_similarity(query_emb, emb) for emb in chunk_embeddings]
    top_indices = np.argsort(similarities)[-3:][::-1]
    context = "\n".join([chunks[i] for i in top_indices])

    chat_box.insert(tk.END, f"🧑 You: {query}\n", "user")

    prompt = f"Use the following document context to answer accurately.\n\n{context}\n\nQuestion: {query}"
    response = ollama.chat(model="gemma3:1b", messages=[{"role": "user", "content": prompt}])
    answer = response["message"]["content"]

    chat_box.insert(tk.END, f"🤖 AI: {answer}\n\n", "ai")
    chat_box.see(tk.END)

# ---- UI Setup ----
root = tk.Tk()
root.title("Local Document Chat (Ollama)")
root.geometry("820x650")
root.configure(bg="#1E1E2E")

title_label = tk.Label(
    root, text="📚 Local Document Chat",
    font=("Segoe UI", 18, "bold"), fg="#F8F8F2", bg="#1E1E2E"
)
title_label.pack(pady=10)

frame = tk.Frame(root, bg="#1E1E2E")
frame.pack(padx=10, pady=5, fill="x")

upload_btn = tk.Button(
    frame, text="Upload Document", command=load_document,
    bg="#6272A4", fg="white", activebackground="#7082b6",
    font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5
)
upload_btn.pack(side="left", padx=5)

ask_btn = tk.Button(
    frame, text="Ask", command=ask,
    bg="#50FA7B", fg="#1E1E2E", activebackground="#5efc89",
    font=("Segoe UI", 10, "bold"), relief="flat", padx=10, pady=5
)
ask_btn.pack(side="right", padx=5)

entry = tk.Entry(
    root, font=("Segoe UI", 11),
    bg="#2E2E3E", fg="#F8F8F2", insertbackground="white"
)
entry.pack(fill="x", padx=10, pady=5, ipady=6)

chat_box = scrolledtext.ScrolledText(
    root, wrap=tk.WORD, height=25,
    font=("Consolas", 11), bg="#282A36", fg="#F8F8F2",
    insertbackground="white", borderwidth=0
)
chat_box.pack(padx=10, pady=10, fill="both", expand=True)

# Add tag styles
chat_box.tag_config("user", foreground="#8BE9FD", font=("Consolas", 11, "bold"))
chat_box.tag_config("ai", foreground="#50FA7B")
chat_box.tag_config("info", foreground="#BD93F9", font=("Consolas", 10, "italic"))
chat_box.tag_config("warning", foreground="#FFB86C", font=("Consolas", 10, "italic"))

root.mainloop()
