# Deploying to Vercel

## Introduction

You are deploying to **Vercel**, which is an excellent serverless platform. I have created `wsgi.py` and `vercel.json` to make your Flask app compatible with Vercel.

## Answering Your Screenshot Question (Empty Columns)

In the Vercel "Import Project" screen (from your screenshot):

1.  **Build Command**: Leave this **EMPTY** (None). Vercel's Python builder handles this automatically.
2.  **Output Directory**: Leave this **EMPTY**.
3.  **Install Command**: Leave this as the default (`pip install -r requirements.txt`).

**So for those empty columns, just leave them as they are!**

## Deployment Steps

### Step 1: Push Config to GitHub

You need to push the new `wsgi.py` and `vercel.json` files to GitHub first.

```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

### Step 2: Import in Vercel

1.  Go to your **Vercel Dashboard**.
2.  Click **Add New...** -> **Project**.
3.  Import your `museum-management-system-using-flask` repository.
4.  **Framework Preset**: Select **Other** (or Flask if available, but "Other" works best with our `vercel.json`).
    *   *Note: If `vercel.json` is present, correct settings usually autoload.*

### Step 3: Environment Variables (Crucial!)

Expand the **Environment Variables** section and add all your secrets from `.env`.

| Key | Value |
| :--- | :--- |
| `MONGO_URI` | `mongodb+srv://...` |
| `SECRET_KEY` | `YourSecretKey...` |
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `True` |
| `MAIL_USERNAME` | `ansarimohammed2006@gmail.com` |
| `MAIL_PASSWORD` | `anoh eijn mogi lseg` |

### Step 4: Deploy

Click **Deploy**.

## Troubleshooting Vercel

*   **Function Timeout**: Vercel functions (serverless) have a 10-second timeout on the free tier. Heavy AI operations might time out.
*   **Static Files**: Flask static files usually work, but sometimes need specific handling in `vercel.json` if they fail to load.
