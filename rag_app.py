import os
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIRS = [os.path.join(BASE_DIR, "doc"), os.path.join(BASE_DIR, "internet_docs")]
# Use an absolute path for FAISS index to ensure it survives in all environments
DB_DIR = os.path.abspath(os.path.join(BASE_DIR, "faiss_index_store"))
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# --- RAG Setup ---

def setup_rag():
    """Initializes RAG with persistence and multiple document sources."""
    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Check if vector database already exists on disk
    if os.path.exists(DB_DIR):
        print(f"✅ Loading existing vector database from: {DB_DIR}")
        try:
            vectorstore = FAISS.load_local(
                DB_DIR, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
            return vectorstore.as_retriever(search_kwargs={"k": 5})
        except Exception as e:
            print(f"❌ Error loading existing vector database: {e}. Re-indexing everything...")

    # Load documents from all specified directories
    all_documents = []
    for doc_path in DOC_DIRS:
        if os.path.exists(doc_path):
            print(f"📂 Loading documents from {doc_path}...")
            loader = DirectoryLoader(doc_path, glob="**/*.md", loader_cls=TextLoader)
            try:
                all_documents.extend(loader.load())
            except Exception as e:
                print(f"⚠️ Warning loading from {doc_path}: {e}")
        else:
            print(f"⚠️ Warning: Directory {doc_path} not found.")

    if not all_documents:
        print("❌ No documents found to index.")
        return None

    # Split documents into chunks
    print(f"📄 Total documents loaded: {len(all_documents)}. Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = text_splitter.split_documents(all_documents)

    # Create and save FAISS vector store
    print(f"🧠 Creating new vector store with {len(splits)} chunks and saving to disk...")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    # Save to local disk
    os.makedirs(os.path.dirname(DB_DIR), exist_ok=True)
    vectorstore.save_local(DB_DIR)
    print(f"💾 Vector database saved successfully at: {DB_DIR}")
    
    return vectorstore.as_retriever(search_kwargs={"k": 5})

# Initialize retriever globally
retriever = setup_rag()

def get_llm():
    """Configures the LLM using HuggingFace Inference API with a Chat architecture."""
    if not HUGGINGFACE_API_KEY:
        raise ValueError("HUGGINGFACE_API_KEY not found in .env file.")
    
    # Using Mistral-7B-Instruct-v0.2 as it's stable and supports 'conversational' task
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
        temperature=0.1,
        max_new_tokens=512,
        task="conversational"
    )
    
    # Wrap in ChatHuggingFace to handle the conversational architecture/payload correctly
    return ChatHuggingFace(llm=llm)

def format_docs(docs):
    """Formats retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

# --- Flask Routes ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MSME Financial StressScore Advisor</title>
    <style>
        :root {
            --primary: #4facfe;
            --secondary: #00f2fe;
            --bg: #0f1116;
            --card-bg: #1e2229;
            --text: #e0e0e0;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: var(--bg); 
            color: var(--text);
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        #chat-container { 
            width: 600px; 
            max-width: 95%;
            height: 700px;
            background: var(--card-bg); 
            display: flex;
            flex-direction: column;
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            overflow: hidden;
            border: 1px solid #3e4451;
        }
        .header {
            padding: 20px;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            color: white;
            text-align: center;
            font-weight: bold;
            font-size: 1.3rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        #messages { 
            flex-grow: 1;
            overflow-y: auto; 
            padding: 20px; 
            display: flex;
            flex-direction: column;
            gap: 15px;
            background: #161b22;
        }
        .message { 
            max-width: 80%;
            padding: 12px 16px; 
            border-radius: 12px; 
            line-height: 1.5;
            word-wrap: break-word;
            position: relative;
        }
        .user { 
            align-self: flex-end;
            background: var(--primary); 
            color: white; 
            border-bottom-right-radius: 2px;
        }
        .bot { 
            align-self: flex-start;
            background: #2b313e; 
            border-left: 4px solid var(--secondary);
            border-bottom-left-radius: 2px;
            color: #d1d5db;
        }
        .input-area {
            padding: 20px;
            background: var(--card-bg);
            display: flex;
            gap: 10px;
            border-top: 1px solid #3e4451;
        }
        input { 
            flex-grow: 1;
            padding: 12px 15px; 
            background: #0d1117;
            border: 1px solid #3e4451; 
            border-radius: 8px; 
            color: white;
            outline: none;
            font-size: 1rem;
        }
        input:focus { border-color: var(--primary); }
        button { 
            padding: 10px 25px; 
            background: linear-gradient(45deg, var(--primary), var(--secondary)); 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        button:active { transform: scale(0.95); }
        .typing { font-style: italic; color: #8b949e; font-size: 0.9rem; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #3e4451; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="chat-container">
        <div class="header">
            <span>📊</span> MSME RAG Advisor
        </div>
        <div id="messages">
            <div class="message bot">Hello! I'm your MSME Financial Stress Score Advisor. I've indexed your documents and I'm ready to help. What would you like to know?</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Ask about financial health, stress scores..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('userInput');

        function appendMessage(text, role) {
            const msg = document.createElement('div');
            msg.className = `message ${role}`;
            msg.innerText = text;
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return msg;
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            input.value = '';

            const typingMsg = appendMessage('Thinking...', 'bot typing');

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                
                typingMsg.innerText = data.response;
                typingMsg.className = 'message bot';
            } catch (error) {
                typingMsg.innerText = "I encountered an error. Please check the server logs.";
                typingMsg.className = 'message bot';
            }
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('message')
    
    if not retriever:
        return jsonify({"response": "I'm sorry, I couldn't initialize the document database. Please check the 'doc' folder."})

    try:
        llm = get_llm()
        
        # Chat-based prompt for modern architecture
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional MSME Financial Stress Score Advisor. Use the following context from indexed documents to answer the user's question accurately and helpfully. Context: {context}"),
            ("human", "{question}")
        ])
        
        # Build the chain
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        response = chain.invoke(user_query)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"response": f"I hit a snag: {str(e)}"})

if __name__ == '__main__':
    print("🚀 MSME Advisor starting at http://localhost:5000")
    if os.path.exists(DB_DIR):
        print(f"✅ Using persistent vector store from {DB_DIR}")
    else:
        print("⚡ First run: Creating and saving vector store...")
    
    # Disable debug mode to prevent the Flask reloader from double-initializing 
    # the heavy LangChain/Embeddings models, which causes the URL hanging issue.
    app.run(debug=False, host='0.0.0.0', port=5000)
