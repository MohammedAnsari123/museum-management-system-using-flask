# Deployment Guide - Museum Management System

This guide will help you deploy your Flask application to **Render.com**, a cloud platform that offers a free tier for web services.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account to host your code.
2.  **Render Account**: Sign up at [render.com](https://render.com) (you can sign up with GitHub).
3.  **MongoDB Atlas Account**: You already have this.

## Important Note on AI Models

> [!WARNING]
> This project uses large AI models (in the `models/` directory). **These files are too large for GitHub (Limit 100MB).**
>
> 1.  I have updated `.gitignore` to exclude the `models/` folder.
> 2.  **On Render**, the application will try to download these models automatically using `transformers` if they are not found.
> 3.  **Performance Note**: Downloading models on the free tier of Render might be slow or run out of memory. If that happens, you might need to switch to a smaller model (like `Qwen/Qwen2.5-0.5B-Instruct` or `HuggingFaceTB/SmolLM2-135M-Instruct`) in your code.

## Step 1: Push Code to GitHub

If you haven't already pushed your code to GitHub, follow these steps in your terminal (VS Code):

```bash
# Initialize git if not already done
git init

# Add all files (respecting new .gitignore)
git add .

# Commit changes
git commit -m "Ready for deployment (Models ignored)"

# Create a new repository on GitHub.com and copy the URL
# Link your local repo to GitHub (replace URL with your actual one)
git remote add origin https://github.com/YOUR_USERNAME/museum-management-system.git

# Push code
git branch -M main
git push -u origin main
```

## Step 2: Create Web Service on Render

1.  Log in to your **Render Dashboard**.
2.  Click **New +** button and select **Web Service**.
3.  Connect your GitHub account and select the `museum-management-system` repository.
4.  **Configure the Service**:
    *   **Name**: `museum-management-system` (or any unique name)
    *   **Region**: Singapore (or nearest to India)
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt` (Render usually detects this)
    *   **Start Command**: `gunicorn "main:create_app()"` (Render should detect this from the `Procfile` I created)
    *   **Instance Type**: Free

## Step 3: Configure Environment Variables

**Crucial Step:** You must provide your secret keys to Render.

1.  Scroll down to the **Environment Variables** section on the setup page (or go to the "Environment" tab after creation).
2.  Add the following keys and values from your local `.env` file:

| Key | Value |
| :--- | :--- |
| `MONGO_URI` | `mongodb+srv://newuser:admin1234@cluster0.kjp1d40.mongodb.net/museum_management_system_1` |
| `SECRET_KEY` | `Musuem_Management_system_Created_By_Mohammed_Ansari_2025` |
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `True` |
| `MAIL_USERNAME` | `ansarimohammed2006@gmail.com` |
| `MAIL_PASSWORD` | `anoh eijn mogi lseg` |

3.  Click **Create Web Service**.

## Step 4: Whitelist Render IP (Important!)

Since your MongoDB Atlas is restricted by IP, Render needs access.

1.  **Allow Access from Anywhere**:
    *   This is the easiest way for dynamic cloud IPs.
    *   Go to **MongoDB Atlas** -> **Network Access**.
    *   Click **Add IP Address**.
    *   Select **Allow Access from Anywhere** (`0.0.0.0/0`).
    *   *Note: This makes your DB accessible from any IP, but it is still protected by your username/password.*

## Step 5: Verification

1.  Render will start building your app. This takes a few minutes.
2.  Watch the "Logs" tab.
3.  Once you see "Your service is live", click the URL provided (e.g., `https://museum-system.onrender.com`).
4.  Test the chatbot and login features.

## Troubleshooting

*   **Build Failed?** Check the logs. Usually checks for missing requirements. I updated `requirements.txt` to include `gunicorn` and `certifi`.
*   **Database Error?** Check the logs for "Timeout" or "SSL Handshake". Ensure you allowed `0.0.0.0/0` in MongoDB Atlas.
