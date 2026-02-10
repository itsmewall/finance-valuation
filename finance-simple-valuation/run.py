import sys
from pathlib import Path

# Add src to python path so we can import modules
# Not strictly necessary if running as module, but good for script execution
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.pipeline.orchestrator import run_all

if __name__ == "__main__":
    run_all(ROOT_DIR)
