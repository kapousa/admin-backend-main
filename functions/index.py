# functions/index.py
from main import app  # Import the FastAPI app from main.py
from mangum import Mangum  # Mangum is the adapter to run ASGI apps in AWS Lambda

# Create a Mangum handler for the serverless function
handler = Mangum(app)
