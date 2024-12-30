import requests

# URL for fetching data from Mockaroo
url = 'https://api.mockaroo.com/api/02402ed0?count=1000&key=fe081000'

# Make the request to Mockaroo
response = requests.get(url)

if response.status_code == 200:
    print("Raw response:", response.text)

    loan_data = response.json()  # Convert the response to JSON
    print(f"Fetched {len(loan_data)} records from Mockaroo.")
    print(f"First record: {loan_data[0]}")  # Print the first record
else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")
