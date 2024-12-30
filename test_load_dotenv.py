
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = os.path.join(os.getcwd(), "..", "env", "network.env")
load_dotenv(dotenv_path=dotenv_path)

# Print all environment variables to debug
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Get the private key
private_key = os.getenv("PRIVATE_KEY")
print(f"Private Key Loaded: {private_key}")