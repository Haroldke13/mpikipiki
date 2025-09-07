# app.py
import os
from dotenv import load_dotenv
from . import create_app

# Load environment variables
load_dotenv()

# Create the app using factory
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
