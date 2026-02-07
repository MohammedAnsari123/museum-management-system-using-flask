# Deploying to DigitalOcean App Platform

This guide will help you deploy your Flask application to **DigitalOcean App Platform** using GitHub.

## Prerequisites

1.  **GitHub Account**: Your code must be pushed to a GitHub repository.
2.  **DigitalOcean Account**: Sign up at [digitalocean.com](https://www.digitalocean.com/). (You may need to add a payment method, but they often give free credits to new users).

## Step 1: Push Code to GitHub

Ensure your latest changes (including `requirements.txt` and `Procfile`) are pushed to GitHub:

```bash
git add .
git commit -m "Prepared for DigitalOcean deployment"
git push origin main
```

## Step 2: Create App on DigitalOcean

1.  Log in to your **DigitalOcean Control Panel**.
2.  Click **Create** (green button at top right) -> **Apps**.
3.  **Choose Source**: Select **GitHub**.
4.  **Authorize**: If not already connected, authorize DigitalOcean to access your GitHub account.
5.  **Select Repository**: Choose `museum-management-system-using-flask`.
6.  **Branch**: Select `main` and ensure "Autodeploy" is checked. Click **Next**.

## Step 3: Configure Resources

1.  **Edit Plan**:
    *   Click "Edit Plan" if needed.
    *   You can choose the **Basic** plan ($5/month) or a higher tier.
    *   DigitalOcean essentially manages the Docker container for you using the `Procfile`.
2.  **Environment Variables**:
    *   Click **Edit** next to "Environment Variables".
    *   Add your secrets here (copy from your local `.env` file):

    | Key | Value |
    | :--- | :--- |
    | `MONGO_URI` | `mongodb+srv://...` |
    | `SECRET_KEY` | `YourSecretKey...` |
    | `MAIL_SERVER` | `smtp.gmail.com` |
    | `MAIL_PORT` | `587` |
    | `MAIL_USE_TLS` | `True` |
    | `MAIL_USERNAME` | `ansarimohammed2006@gmail.com` |
    | `MAIL_PASSWORD` | `anoh eijn mogi lseg` |

3.  Click **Save**.
4.  Click **Next**.

## Step 4: Review and Create

1.  Review your settings.
2.  Click **Create Resources**.

## Step 5: Verification

1.  DigitalOcean will start building your app. You can watch the "Deployment Logs".
2.  Once the build is successful (green checkmark), you will see your **Live App URL** (something like `https://starfish-app-xxxxx.ondigitalocean.app`).
3.  Click the URL to open your deployed Museum Management System.

## Important Notes

*   **Database Access**: Ensure your MongoDB Atlas is configured to allow access from **Anywhere (0.0.0.0/0)** in Network Access, as DigitalOcean app IPs change.
*   **Build Command**: DigitalOcean automatically detects Python apps and runs `pip install -r requirements.txt`.
*   **Run Command**: It automatically detects the `Procfile` command `gunicorn ...`.
