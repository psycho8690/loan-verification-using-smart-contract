# Loan Verification System

A blockchain-powered loan verification system that allows borrowers to register their details, checks the validity of loan requests using predefined conditions, and updates loan statuses accordingly. The system leverages Ethereum smart contracts deployed on the Sepolia Testnet, integrated with a Flask API.

---

## Features

- Add or update borrower details.
- Validate loan requests based on mortgage value, monthly income, and credit score.
- Retrieve all borrower details or specific borrower information.
- Update loan statuses for all borrowers in one endpoint.
- Delete borrower data.
- Integration with Mockaroo API for sample borrower data in CSV format (converted to JSON).
- Full blockchain integration with smart contracts.

---

## Technologies Used

- **Ethereum Blockchain** (Smart Contracts using Solidity).
- **Flask** (Backend API).
- **Web3.py** (Blockchain interaction).
- **Mockaroo API** (Sample data generation).
- **Ganache/Metamask** (Testing environment).

---

## Prerequisites

1. Python 3.x installed.
2. Node.js and npm installed for Ganache CLI.
3. Metamask setup for the Sepolia Testnet.
4. Flask dependencies installed:
   ```bash
   pip install flask flask-cors web3 python-dotenv
   ```
5. Environment variables configured in `network.env`:
   ```env
   PRIVATE_KEY=your_private_key
   SEPOLIA_ACCOUNT=your_account_address
   SEPOLIA_URL=https://eth-sepolia.g.alchemy.com/v2/your_api_key
   CONTRACT_ADDRESS=deployed_contract_address
   NETWORK=sepolia
   ```

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/loan-verification-project.git
cd loan-verification-project
```

### 2. Virtual Environment Setup

```bash
python3 -m venv env
source env/bin/activate  # For Linux/Mac
env\Scripts\activate   # For Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Smart Contract Deployment

- Update `deploy.py` to point to the correct directory and private key.
- Run the deployment script:
  ```bash
  python deploy.py
  ```
- Copy the deployed contract address into `network.env` and `LoanVerification.json`.

### 5. Run the Flask API

```bash
cd api
python app.py
```

### 6. Testing with Postman

- Use Postman to test all endpoints:
  - Sync All Borrowers (`POST /api/sync-all`)
  - Get All Borrowers (`GET /api/get-all-borrowers`)
  - Update Loan Status (`POST /api/update-loan-status`)
  - Delete Borrower (`DELETE /api/delete-borrower/<address>`)

---

## API Endpoints

### 1. Sync All Borrowers

- **Endpoint:** `/api/sync-all`
- **Method:** `POST`
- **Description:** Fetches data from Mockaroo API, validates, and syncs borrower details to the blockchain.

### 2. Get All Borrowers

- **Endpoint:** `/api/get-all-borrowers`
- **Method:** `GET`
- **Description:** Retrieves all borrower details from the blockchain.

### 3. Update Loan Status

- **Endpoint:** `/api/update-loan-status`
- **Method:** `POST`
- **Description:** Updates loan statuses for all borrowers based on validation logic.

### 4. Delete Borrower

- **Endpoint:** `/api/delete-borrower/<address>`
- **Method:** `DELETE`
- **Description:** Deletes a specific borrower from the blockchain.

---

## Developer Notes

1. **Deploy.py and App.py Updates:** Ensure the contract address in `deploy.py` is correctly updated in `network.env` and `LoanVerification.json`.
2. **Environment Directory:** Double-check directory paths in both `deploy.py` and `app.py`.
3. **Flask CORS:** Install `Flask-CORS` and include:
   ```python
   from flask_cors import CORS
   CORS(app)
   ```
4. **Testing with Postman:** Verify all endpoints using Postman.
5. **Mockaroo Data Handling:** Ensure Mockaroo data (CSV) is converted to JSON for syncing. Handle missing or invalid data (e.g., `null`, empty strings, etc.).
6. **Checksum for Ethereum Addresses:** Always convert addresses to checksum format using:
   ```python
   Web3.to_checksum_address(address)
   ```
7. **Metamask or Ganache:** Switch between Metamask VM or Ganache VM based on the environment.

---

## Project Status

### Day 10 of the Challenge

- **Completed:**
  - Smart contract deployment and integration.
  - Flask API with all required endpoints.
  - Testing on Sepolia Testnet.

- **Next Steps:**
  - Frontend integration.
  - Final testing and deployment.
  - Presentation or documentation polish.

---

## Future Enhancements

1. Implement user authentication for API security.
2. Add frontend with React or Angular for better user experience.
3. Enhance validation logic in the smart contract.
4. Add support for other blockchain networks like Polygon or Binance Smart Chain.

---

## License

This project is licensed under the MIT License.

