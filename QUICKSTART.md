# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Google API key ([Get one free here](https://makersuite.google.com/app/apikey))

## Installation

### Option 1: Automated (Recommended)

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```bash
run.bat
```

The script will:
- Create a virtual environment
- Install all dependencies
- Set up environment files
- Launch the application

### Option 2: Manual

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 4. Run the app
streamlit run app.py
```

## First Steps

1. **Configure API Key**
   - Open `.env` file
   - Add your Google API key: `GOOGLE_API_KEY=your_key_here`

2. **Launch Application**
   - Run `./run.sh` (Unix) or `run.bat` (Windows)
   - Or: `streamlit run app.py`

3. **Use the App**
   - Browser opens at http://localhost:8501
   - Select 2-3 PDF documents from sidebar
   - Click "🚀 Initialize Agent"
   - Start asking questions!

## Example Queries

Try these questions:
- "Summarize the main findings of these papers"
- "What datasets are used for evaluation?"
- "Compare the methodologies in these papers"
- "What are the key contributions?"

## Troubleshooting

**Problem**: "API key not found"
- **Solution**: Check `.env` file has `GOOGLE_API_KEY=your_actual_key`

**Problem**: Missing dependencies
- **Solution**: Run `pip install -r requirements.txt`

**Problem**: Port already in use
- **Solution**: `streamlit run app.py --server.port 8502`

## Next Steps

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration
- Read [README.md](README.md) for features and API usage
- Explore Jupyter notebooks: `jupyter notebook`

## Need Help?

- Email: patricka.azuma@gmail.com
- Check: [Full Setup Guide](SETUP_GUIDE.md)
