"""
WSGI application entry point for Render.com deployment
This file redirects to the correct WSGI application
"""

import os
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the Django WSGI application
from config.wsgi import application

# Create app variable that gunicorn expects
app = application 