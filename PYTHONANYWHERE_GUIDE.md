# PythonAnywhere Deployment Guide

Deploying to **PythonAnywhere** is a bit different from Render. Follow these steps exactly.

## Step 1: Push latest code to GitHub
Make sure your latest changes (including the new `flask_app.py` I just created) are on GitHub.

```bash
git add .
git commit -m "Add PythonAnywhere configuration"
git push
```

## Step 2: Create PythonAnywhere Account & Consoles
1.  Log in to [PythonAnywhere](https://www.pythonanywhere.com/).
2.  Go to the **Consoles** tab.
3.  Click **Bash** to open a new terminal.

## Step 3: Clone your Code
In the Bash console, run:

```bash
# Clone your repository
git clone https://github.com/MohammedAnsari123/museum-management-system-using-flask.git mysite

# Go into the folder
cd mysite
```

## Step 4: Create Virtual Environment
Run these commands one by one:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies (This will take a few minutes)
pip install -r requirements.txt
```

## Step 5: Configure Web App
1.  Go to the **Web** tab (top right).
2.  Click **Add a new web app**.
3.  Select **Manual configuration** (NOTE: Do NOT select Flask, select Manual).
4.  Select **Python 3.10** (or whatever version matches your local env, 3.10 is safe).

## Step 6: Set up WSGI File
1.  Scroll down to the **Code** section on the Web tab.
2.  Click usually named `/var/www/yourusername_pythonanywhere_com_wsgi.py`.
3.  **DELETE EVERYTHING** in that file.
4.  Paste the following code:

```python
import sys
import os
from dotenv import load_dotenv

# path to your project
path = '/home/YOUR_USERNAME/mysite'
if path not in sys.path:
    sys.path.append(path)

# Load .env file
load_dotenv(os.path.join(path, '.env'))

from main import create_app

# Create app
application = create_app()
```
*Replace `YOUR_USERNAME` with your actual PythonAnywhere username.*

5.  Click **Save**.

## Step 7: Environment Variables (.env)
PythonAnywhere doesn't have an "Environment Variables" GUI like Render.
1.  Go to the **Files** tab.
2.  Navigate to `mysite`.
3.  Create a new file named `.env`.
4.  Paste the contents of your local `.env` file (MONGO_URI, etc.) into it.
5.  Save it.

## Step 8: Virtual Environment Path
1.  Go back to the **Web** tab.
2.  Scroll to the **Virtualenv** section.
3.  Enter the path: `/home/YOUR_USERNAME/mysite/venv`
4.  (Use your actual username).

## Step 9: Reload
Scroll to the top of the Web tab and click the big green **Reload** button.

## Step 10: Verify
Click the link to your site (e.g., `yourusername.pythonanywhere.com`).

**Troubleshooting:**
*   **Error Logs:** If it fails, check the **Error Log** link in the Web tab.
*   **Database:** Ensure MongoDB Atlas IP Whitelist is `0.0.0.0/0`.
