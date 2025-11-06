# Complete Setup Guide - Agentic RAG with LlamaIndex

This guide will walk you through setting up the Agentic RAG application from scratch.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** installed
- **pip** package manager
- **Git** (for cloning the repository)
- A **Google API Key** (free tier available)

## Step-by-Step Setup

### Step 1: Get Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (you'll need this later)

**Note**: The free tier of Gemini API is generous and should be sufficient for testing and moderate use.

### Step 2: Clone the Repository

```bash
git clone https://github.com/PatrickAttankurugu/Agentic-RAG-with-LlamaIndex.git
cd Agentic-RAG-with-LlamaIndex
```

### Step 3: Create a Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements-new.txt
```

This will install:
- LlamaIndex and its components
- Google Generative AI (Gemini)
- HuggingFace Sentence Transformers
- Streamlit
- Other required packages

**Installation may take 5-10 minutes** as it downloads models and dependencies.

### Step 5: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in your text editor:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. Replace `your_google_api_key_here` with your actual Google API key:
   ```
   GOOGLE_API_KEY=AIzaSy...your_actual_key_here...
   ```

4. Save and close the file

### Step 6: Verify Your Setup

Run the backend test:

```bash
python rag_backend.py
```

You should see:
```
Initializing RAG Backend...
Backend initialized successfully!
Available documents: X
  - document1.pdf
  - document2.pdf
  ...
```

If you see errors, check the Troubleshooting section below.

### Step 7: Launch the Application

```bash
streamlit run app.py
```

The application will:
1. Start a local web server
2. Open your default browser automatically
3. Display the Agentic RAG interface at `http://localhost:8501`

## First-Time Usage

Once the app is running:

1. **Check API Status**: In the sidebar, verify "API Key: Configured" is shown
2. **Select Documents**: Choose 2-3 PDF files from the document list
3. **Choose Agent Mode**:
   - Select "Advanced" if you have 5+ documents
   - Select "Simple" for fewer documents
4. **Initialize**: Click "Initialize Agent"
5. **Start Asking**: Type a question like "Summarize the main findings of these papers"

## Using Your Own Documents

To analyze your own PDF files:

1. Copy your PDF files into the project directory:
   ```bash
   cp /path/to/your/paper.pdf .
   ```

2. Refresh the Streamlit app (press R in the browser)
3. Your new documents will appear in the selection list

## Troubleshooting

### Issue: "Google API key not found"

**Solution:**
- Ensure `.env` file exists in the project root
- Check that `GOOGLE_API_KEY` is set correctly (no quotes, no spaces)
- Verify the API key is valid at [Google AI Studio](https://makersuite.google.com/)

### Issue: ImportError or ModuleNotFoundError

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall requirements
pip install -r requirements-new.txt
```

### Issue: "Error loading model" or Embedding errors

**Solution:**
The first time you run the app, HuggingFace will download the embedding model (~100MB). This is normal and only happens once.

If it fails:
```bash
# Manually download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Issue: Out of memory errors

**Solution:**
- Reduce the number of documents loaded at once
- Use smaller PDFs
- Close other applications
- Adjust chunk size in `rag_backend.py` (line: `Settings.chunk_size = 512`)

### Issue: API rate limit exceeded

**Solution:**
- Google's free tier has limits on requests per minute
- Wait a few minutes between queries
- Consider upgrading to a paid tier for production use

## Advanced Configuration

### Changing the LLM Model

Edit `rag_backend.py`, line ~38:
```python
self.llm = Gemini(
    model="models/gemini-2.0-flash-exp",  # Try: gemini-pro, gemini-1.5-flash
    api_key=self.api_key,
    temperature=0.1  # 0.0 = deterministic, 1.0 = creative
)
```

### Changing the Embedding Model

Edit `rag_backend.py`, line ~44:
```python
self.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"  # Other options:
    # "sentence-transformers/all-MiniLM-L6-v2"  # Faster, smaller
    # "BAAI/bge-base-en-v1.5"  # Larger, more accurate
)
```

### Adjusting Chunk Size

Edit `rag_backend.py`, line ~51:
```python
Settings.chunk_size = 1024  # Smaller = more chunks, higher memory
                            # Larger = fewer chunks, less precise
```

## Performance Tips

1. **For faster initialization**: Use Simple mode with fewer documents
2. **For better quality**: Use Advanced mode with lower temperature (0.0-0.2)
3. **For large documents**: Increase chunk_size to 1536 or 2048
4. **For many documents**: Always use Advanced mode with tool retrieval

## Next Steps

- Explore the Jupyter notebooks for learning: `jupyter notebook`
- Read the main README.md for API usage examples
- Customize the Streamlit UI in `app.py`
- Add your own tools and functionality

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review the main README.md
3. Check the GitHub Issues page
4. Email: patricka.azuma@gmail.com

## System Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- Python 3.9+
- Internet connection (for API calls)

**Recommended:**
- 8GB RAM
- 5GB free disk space
- Python 3.10+
- Stable internet connection

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys private
- Regularly rotate your API keys
- Monitor your API usage at [Google Cloud Console](https://console.cloud.google.com/)

## What's Included

This project comes with:
- 12 research papers as sample documents
- Pre-configured Streamlit UI
- Advanced and Simple agent modes
- Router engine for single documents
- Complete documentation
- Jupyter notebooks for learning

Happy researching!
