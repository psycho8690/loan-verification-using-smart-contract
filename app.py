from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3
from dotenv import load_dotenv
import json
import os
import time
import requests
import csv
import io

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers

        # Add necessary headers for CORS
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Access-Control-Allow-Methods"] = "OPTIONS, GET, POST, PUT, DELETE"
        headers["Access-Control-Allow-Headers"] = request.headers.get(
            "Access-Control-Request-Headers", "*"
        )
        return response

# Debugging
print(f"Current Working Directory: {os.getcwd()}")

# Load environment variables from the .env file
dotenv_path = os.path.join(os.getcwd(), "..", "env", "network.env")
print(f"Loading environment variables from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

# Retrieve the private key and account from environment variables
private_key = os.getenv("PRIVATE_KEY")
default_account = os.getenv("SEPOLIA_ACCOUNT")

if not private_key or not default_account:
    raise Exception("PRIVATE_KEY or SEPOLIA_ACCOUNT is not set in the environment variables")

# Blockchain setup - dynamic switching between Ganache and Sepolia
NETWORK = os.getenv("NETWORK", "ganache")

if NETWORK == "sepolia":
    SEPOLIA_URL = os.getenv("SEPOLIA_URL")
    web3 = Web3(Web3.HTTPProvider(SEPOLIA_URL))
    print("Connected to Sepolia Testnet")
else:
    GANACHE_URL = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    print("Connected to Ganache Local Network")

if not web3.is_connected():
    raise Exception("Failed to connect to the blockchain network")

# Set default account
web3.eth.default_account = Web3.to_checksum_address(default_account)

# Load the contract ABI and bytecode
contract_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "blockchain", "LoanVerification.json")

with open(contract_file_path, "r") as file:
    contract_data = json.load(file)

CONTRACT_ABI = contract_data["abi"]
CONTRACT_ADDRESS = Web3.to_checksum_address(contract_data["address"])
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Mockaroo API details
MOCKAROO_URL = "https://api.mockaroo.com/api/02402ed0?count=10&key=fe081000&seed=12345"

# Function to fetch data from Mockaroo API and convert CSV to JSON
def load_mock_data_from_mockaroo():
    try:
        response = requests.get(MOCKAROO_URL)
        print(f"Mockaroo Response Status Code: {response.status_code}")
        response.raise_for_status()

        csv_data = response.text
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        mock_data = [row for row in csv_reader]

        # Sort or limit the data to ensure consistency (e.g., first 10 entries sorted by a specific key)
        sorted_data = sorted(mock_data, key=lambda x: x.get("Borrower_Address", ""))[:10]
        print(f"Successfully fetched {len(sorted_data)} borrowers from Mockaroo")
        return sorted_data

    except requests.RequestException as e:
        print(f"Error fetching data from Mockaroo: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


# Helper function to safely process fields
def safe_int(value):
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return 0  # Default to 0 for invalid fields

# Retry decorator for web3 calls
def retry(max_attempts=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Retrying {func.__name__} due to error: {e} (Attempt {attempts}/{max_attempts})")
                    time.sleep(delay)
            raise Exception(f"Max retries exceeded for {func.__name__}")
        return wrapper
    return decorator

# Sync all borrowers to blockchain
@app.route('/api/sync-all', methods=['OPTIONS', 'POST'])
def sync_all_to_blockchain():
    if request.method == 'OPTIONS':
        print("CORS preflight request received")
        return jsonify({"message": "CORS preflight successful"}), 200

    try:
        print("Starting sync-all process...")
        mock_data = load_mock_data_from_mockaroo()  # Fetch data directly from Mockaroo
        print(f"Loaded {len(mock_data)} borrowers from Mockaroo")
        
        # Sort mock data by Borrower_Address for consistent ordering
        sorted_data = sorted(mock_data, key=lambda x: x.get("Borrower_Address", "").strip())
        
        # Process only the first 10 sorted borrowers
        batch_size = 10
        transactions = []

        for i in range(0, min(batch_size, len(sorted_data))):
            borrower = sorted_data[i]
            borrower_address = borrower.get("Borrower_Address", "").strip()
            if not borrower_address:
                print(f"Skipping borrower due to missing address: {borrower}")
                continue

            try:
                borrower_address = Web3.to_checksum_address(borrower_address)
                # Check if borrower exists in the blockchain
                existing_borrower = contract.functions.getBorrower(borrower_address).call()
                if existing_borrower[0] > 0:  # Loan amount > 0 indicates existence
                    print(f"Skipping existing borrower: {borrower_address}")
                    continue
            except Exception as e:
                # Log the error, but proceed to add the borrower
                print(f"Borrower does not exist, adding new: {borrower_address}. Error: {e}")

            # Parse and validate borrower fields
            loan_amount = safe_int(borrower.get("Loan_Amount"))
            mortgage_value = safe_int(borrower.get("Mortgage_Value"))
            monthly_income = safe_int(borrower.get("Monthly_Income"))
            credit_score = safe_int(borrower.get("Credit_Score"))

            if loan_amount == 0 and mortgage_value == 0 and monthly_income == 0 and credit_score == 0:
                print(f"Skipping borrower due to invalid data: {borrower}")
                continue

            try:
                nonce = web3.eth.get_transaction_count(web3.eth.default_account, 'pending')
                tx = contract.functions.addOrUpdateBorrower(
                    borrower_address,
                    loan_amount,
                    mortgage_value,
                    monthly_income,
                    credit_score
                ).build_transaction({
                    'from': web3.eth.default_account,
                    'nonce': nonce,
                    'gas': 300000,
                    'gasPrice': web3.to_wei('20', 'gwei'),
                })

                signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                transactions.append(tx_hash.hex())
                print(f"Transaction successful for {borrower_address}, Tx Hash: {tx_hash.hex()}")

            except Exception as e:
                print(f"Error processing borrower {borrower_address}: {e}")
                continue

        print("All borrowers synced successfully")
        return jsonify({"message": "All borrowers synced successfully", "transactions": transactions}), 200

    except Exception as e:
        print(f"Error syncing all: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Get all borrowers
@app.route('/api/get-all-borrowers', methods=['GET'])
@retry(max_attempts=5, delay=2)
def get_all_borrowers():
    try:
        # Fetch data from the smart contract using web3
        borrower_addresses, borrower_details = contract.functions.getAllBorrowers().call()

        # Debug information
        print(f"Borrower Addresses: {borrower_addresses}")
        print(f"Borrower Details: {borrower_details}")

        # Check if no borrowers are available
        if not borrower_addresses:
            return jsonify({"message": "No borrowers found"}), 200

        # Format response data
        borrowers = [
            {
                "address": borrower_addresses[i],
                "loanAmount": borrower_details[i][0],
                "loanStatus": "Pending" if borrower_details[i][1] == 0 else ("Approved" if borrower_details[i][1] == 1 else "Rejected"),
                "mortgageValue": borrower_details[i][2],
                "monthlyIncome": borrower_details[i][3],
                "creditScore": borrower_details[i][4],
            }
            for i in range(len(borrower_addresses))
        ]

        return jsonify({"borrowers": borrowers}), 200

    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return jsonify({"error": "Connection error while fetching data from blockchain"}), 500
    except Exception as e:
        print(f"Error in get-all-borrowers: {e}")
        return jsonify({"error": str(e)}), 500



# Update loan statuses for all borrowers
@app.route('/api/update-all-loan-statuses', methods=['POST'])
def update_all_loan_statuses():
    try:
        print("Starting update of all loan statuses...")
        borrower_addresses, borrower_details = contract.functions.getAllBorrowers().call()
        transactions = []

        for i, borrower_address in enumerate(borrower_addresses):
            try:
                loan_amount = int(borrower_details[i][0])
                mortgage_value = int(borrower_details[i][2])
                monthly_income = int(borrower_details[i][3])
                credit_score = int(borrower_details[i][4])

                print(f"Processing borrower: {borrower_address}")
                print(f"Details - Loan Amount: {loan_amount}, Mortgage Value: {mortgage_value}, "
                      f"Monthly Income: {monthly_income}, Credit Score: {credit_score}")

                is_valid = False
                for attempt in range(5):  # Retry logic
                    try:
                        is_valid = contract.functions.validateLoan(
                            loan_amount, mortgage_value, monthly_income, credit_score
                        ).call()
                        break
                    except Exception as e:
                        print(f"Retrying validation for {borrower_address} due to error: {e} (Attempt {attempt+1}/5)")
                        time.sleep(2)

                loan_status = 1 if is_valid else 2
                print(f"Loan validation result for {borrower_address}: {'Approved' if is_valid else 'Rejected'}")

                for attempt in range(5):  # Retry logic for transactions
                    try:
                        nonce = web3.eth.get_transaction_count(web3.eth.default_account, 'pending')
                        tx = contract.functions.updateLoanStatus(
                            borrower_address, loan_status
                        ).build_transaction({
                            'from': web3.eth.default_account,
                            'nonce': nonce,
                            'gas': 300000,
                            'gasPrice': web3.to_wei('20', 'gwei'),
                        })

                        signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
                        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                        transactions.append(tx_hash.hex())
                        print(f"Transaction successful for {borrower_address}, Tx Hash: {tx_hash.hex()}")
                        break
                    except Exception as e:
                        print(f"Retrying transaction for {borrower_address} due to error: {e} (Attempt {attempt+1}/5)")
                        time.sleep(2)

            except Exception as e:
                print(f"Error processing borrower {borrower_address}: {e}")
                continue

        return jsonify({"message": "All loan statuses updated successfully", "transactions": transactions}), 200

    except Exception as e:
        print(f"Error updating loan statuses: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)
