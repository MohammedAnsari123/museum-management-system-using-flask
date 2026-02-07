# Deploying to Fly.io

This guide will walk you through deploying your Museum Management System to Fly.io using the Dockerfile we just created.

## Prerequisites

1.  **Install flyctl**: The Fly.io command-line tool.
    *   **Windows (PowerShell)**:
        ```powershell
        pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
        ```
        *If the above command doesn't work, try running it in a standard PowerShell window (not ensuring `pwsh` is installed).*
    *   Restart your terminal after installing to use the `fly` or `flyctl` command.

2.  **Sign up/Login**:
    ```bash
    fly auth signup
    # OR if you already have an account
    fly auth login
    ```

## Step 1: Initialize the App

Run the following command in your project directory:

```bash
fly launch
```

Follow the prompts:
*   **App Name**: Give it a unique name (e.g., `museum-system-yourname`).
*   **Region**: Choose a region close to you (e.g., `sin` for Singapore, or `bom` for Mumbai if available).
*   **Guest**: No
*   **Database**: No (We are using MongoDB Atlas).
*   **Redis**: No.

This will generate a `fly.toml` file.

## Step 2: Set Secrets (Environment Variables)

Fly.io needs to know your secret keys. Run the following commands (replace values with your actual secrets from your `.env` file):

```bash
fly secrets set SECRET_KEY="YourSecretKeyHere"
fly secrets set MONGO_URI="mongodb+srv://..."
fly secrets set MAIL_SERVER="smtp.gmail.com"
fly secrets set MAIL_PORT="587"
fly secrets set MAIL_USE_TLS="True"
fly secrets set MAIL_USERNAME="your-email@gmail.com"
fly secrets set MAIL_PASSWORD="your-app-password"
```

## Step 3: Deploy

Deploy the application:

```bash
fly deploy
```

This will build your Docker image and push it to Fly.io.

## Step 4: Verification

Once deployed, you can open your app:

```bash
fly open
```

## Troubleshooting

*   **Memory Issues**: The free tier has 512MB RAM. If the app crashes (OOM - Out Of Memory) because of the AI libraries (`torch`, `transformers`), you might need to:
    1.  Upgrade the VM size: `fly scale vm shared-cpu-1x --memory 1024` (This might incur costs).
    2.  Or, disable the heavy AI features in the code if they are not strictly necessary for the deployed version.
