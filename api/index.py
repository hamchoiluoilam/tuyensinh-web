import sys
import os

# Add root directory to sys.path so imports work seamlessly on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
