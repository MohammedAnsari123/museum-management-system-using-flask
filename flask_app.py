
import sys
import os
from dotenv import load_dotenv

# Add project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)

# Load environment variables explicitly for PythonAnywhere
load_dotenv(os.path.join(project_home, '.env'))

from main import create_app

# Create the application instance
application = create_app()
