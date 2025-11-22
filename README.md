# BOT GPT Backend 

## Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/bot-gpt-backend.git](https://github.com/YOUR_USERNAME/bot-gpt-backend.git)
cd bot-gpt-backend
```

### 2. Create a Virtual environment

Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Create a .env file

touch .env

### 5. Add api key to the .env file

GEMINI_API_KEY=AIzaSy...YourKeyHere...

### 6. Run the application

uvicorn app.main:app --reload

Once the server is running, access the interactive API docs (Swagger UI) at: 👉 http://127.0.0.1:8000/docs