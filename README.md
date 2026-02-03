# Museum Management System

A comprehensive web-based application for managing museums, bookings, and visitor engagement, featuring an AI-powered chatbot.

## 🚀 Features

### 👤 User Panel
*   **Browse Museums**: View detailed information about various museums.
*   **Book Tickets**: Secure booking system with QR code generation for tickets.
*   **Museum Map**: Interactive map integration to locate museums.
*   **Chatbot**: AI-powered assistant to answer queries about history and museums.
*   **Review System**: Leave ratings and reviews for visited museums.

### 🛡️ Admin Panel
*   **Dashboard**: Overview of total bookings, revenue, and active users.
*   **Manage Museums**: Add, edit, or remove museum listings.
*   **Manage Bookings**: View and manage visitor bookings.
*   **Analytics**: Visual reports on visitor trends and system usage.

### 🤖 AI Integration
*   **Chatbot**: Integrated using NLP (Transformers/HuggingFace) to provide intelligent responses.
*   **Context Aware**: Capable of answering specific questions based on the museum database.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **Database**: MongoDB (Atlas)
*   **Frontend**: HTML5, CSS3, JavaScript
*   **AI/ML**: PyTorch, Transformers, Sentence-Transformers
*   **Tools**: Git, Visual Studio Code

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/museum-management-system.git
    cd museum-management-system
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory and add the following:
    ```env
    MONGO_URI=your_mongodb_connection_string
    SECRET_KEY=your_secret_key
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_app_password
    ```

5.  **Run the Application**
    ```bash
    python main.py
    ```
    Access the app at `http://127.0.0.1:5000`

## 📂 Project Structure

```
Museum Management System/
├── models/             # Database models
├── modules/            # Helper modules (Chatbot, etc.)
├── routes/             # Flask blueprints (User, Admin, Chatbot)
├── static/             # CSS, JS, Images
├── templates/          # HTML Templates
├── scripts/            # Utility scripts (Seeding, Import)
├── main.py             # Application entry point
├── db.py               # Database connection
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## 🚀 Deployment

This project is configured for deployment on **Render.com**.

For detailed deployment instructions, please read [DEPLOYMENT.md](DEPLOYMENT.md).

## 🤝 Contribution

Contributions are welcome! Please fork the repository and create a pull request.

## 📄 License

This project is licensed under the MIT License.
