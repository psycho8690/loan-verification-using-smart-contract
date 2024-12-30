import axios from 'axios';

const API_URL = 'http://127.0.0.1:5001/api';

// Fetch all borrowers
export const getAllBorrowers = async () => {
  try {
    const response = await axios.get(`${API_URL}/get-all-borrowers`, {
      headers: {
        'Origin': 'http://localhost:3000',
      },
    });
    if (response.data && response.data.borrowers) {
      return response.data.borrowers;
    } else {
      console.warn('No borrowers found in the response:', response.data);
      return [];
    }
  } catch (error) {
    console.error('Error fetching borrowers:', error.response || error.message);
    throw error;
  }
};

// Sync all borrowers
export const syncAllBorrowers = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/sync-all`,
      {}, // No body is required for this endpoint
      {
        headers: {
          'Origin': 'http://localhost:3000',
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('Sync response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error syncing borrowers:', error.response || error.message);
    throw error;
  }
};

// Update loan statuses and refresh borrowers
export const updateLoanStatusAndRefresh = async (setBorrowers) => {
  try {
    // Update loan statuses
    const updateResponse = await axios.post(
      `${API_URL}/update-all-loan-statuses`,
      {}, // No body is required for this endpoint
      {
        headers: {
          'Origin': 'http://localhost:3000',
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('Loan statuses updated:', updateResponse.data);

    // Fetch updated borrowers
    const response = await axios.get(`${API_URL}/get-all-borrowers`, {
      headers: {
        'Origin': 'http://localhost:3000',
      },
    });
    if (response.data && response.data.borrowers) {
      setBorrowers(response.data.borrowers);
    } else {
      console.warn('No borrowers found in the refreshed data:', response.data);
      setBorrowers([]);
    }
  } catch (error) {
    console.error('Error updating loan statuses or refreshing:', error.response || error.message);
    throw error;
  }
};
