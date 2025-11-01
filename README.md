**ChunkChat**

ChunkChat is a local desktop app that lets you chat with your documents. Upload a PDF, DOCX, or TXT file, and ask questions—ChunkChat answers using only the content of your document.
Features

Upload PDF, DOCX, or TXT files.

Splits documents into chunks for efficient processing.  
Uses AI models (e.g., Gemma3:1B) for context-aware answers.  
Colorful, dark-themed chat interface.  
Fully local; your data never leaves your machine.  

**Installation**

git clone https://github.com/your-username/chunkchat.git  
cd chunkchat  
python -m pip install ollama pypdf python-docx numpy  
ollama pull nomic-embed-text  
ollama pull gemma3:1b  
