"""
Agentic RAG v2.0 - Streamlit Application Launcher

Run with: streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so all imports resolve
_project_root = str(Path(__file__).parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import and run the v2 application
from src.api.app_v2 import main  # noqa: E402

if __name__ == "__main__":
    main()
