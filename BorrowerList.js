import React, { useEffect, useState } from 'react';
import { getAllBorrowers, updateLoanStatusAndRefresh } from '../api/api.js';
import { 
  TextField, 
  Button, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  CircularProgress, 
  Snackbar, 
  Alert,
  TablePagination, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions 
} from '@mui/material';

const BorrowerList = () => {
  const [borrowers, setBorrowers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [selectedBorrower, setSelectedBorrower] = useState(null);
  const [snackbarMessage, setSnackbarMessage] = useState(null);
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  useEffect(() => {
    const fetchBorrowers = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getAllBorrowers();
        setBorrowers(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Error fetching borrowers:', error);
        setError('Failed to fetch borrowers. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBorrowers();
  }, []);

  const handleUpdateLoanStatuses = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await updateLoanStatusAndRefresh(setBorrowers);
      setSnackbarMessage('Loan statuses updated successfully!');
      setSnackbarSeverity('success');
    } catch (error) {
      console.error('Error updating loan statuses:', error);
      setSnackbarMessage('Failed to update loan statuses. Please try again.');
      setSnackbarSeverity('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  const handlePageChange = (event, newPage) => {
    setCurrentPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setCurrentPage(0);
  };

  const handleRowClick = (borrower) => {
    setSelectedBorrower(borrower);
  };

  const handleCloseDialog = () => {
    setSelectedBorrower(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbarMessage(null);
  };

  const filteredBorrowers = borrowers.filter(
    (borrower) =>
      borrower.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
      borrower.loanStatus.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const paginatedBorrowers = filteredBorrowers.slice(
    currentPage * rowsPerPage,
    currentPage * rowsPerPage + rowsPerPage
  );

  return (
    <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', color: '#1976d2' }}>Borrower List</h1>
      <TextField
        label="Search"
        variant="outlined"
        fullWidth
        margin="normal"
        value={searchQuery}
        onChange={handleSearchChange}
        placeholder="Search by address or status"
      />
      <Button
        variant="contained"
        color="primary"
        onClick={handleUpdateLoanStatuses}
        disabled={isLoading}
        style={{ marginBottom: '20px' }}
      >
        {isLoading ? <CircularProgress size={24} color="inherit" /> : 'Update Loan Statuses'}
      </Button>
      <TableContainer component={Paper} style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Table>
          <TableHead>
            <TableRow style={{ backgroundColor: '#1976d2' }}>
              <TableCell style={{ color: 'white' }}>Address</TableCell>
              <TableCell style={{ color: 'white' }}>Loan Amount</TableCell>
              <TableCell style={{ color: 'white' }}>Status</TableCell>
              <TableCell style={{ color: 'white' }}>Mortgage Value</TableCell>
              <TableCell style={{ color: 'white' }}>Monthly Income</TableCell>
              <TableCell style={{ color: 'white' }}>Credit Score</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : paginatedBorrowers.length > 0 ? (
              paginatedBorrowers.map((borrower, index) => (
                <TableRow
                  key={index}
                  hover
                  style={{ cursor: 'pointer', backgroundColor: index % 2 === 0 ? '#e3f2fd' : 'white' }}
                  onClick={() => handleRowClick(borrower)}
                >
                  <TableCell>{borrower.address}</TableCell>
                  <TableCell>{borrower.loanAmount}</TableCell>
                  <TableCell>{borrower.loanStatus}</TableCell>
                  <TableCell>{borrower.mortgageValue}</TableCell>
                  <TableCell>{borrower.monthlyIncome}</TableCell>
                  <TableCell>{borrower.creditScore}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No borrowers found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[5, 10, 15]}
        component="div"
        count={filteredBorrowers.length}
        rowsPerPage={rowsPerPage}
        page={currentPage}
        onPageChange={handlePageChange}
        onRowsPerPageChange={handleRowsPerPageChange}
      />

      {selectedBorrower && (
        <Dialog open={true} onClose={handleCloseDialog}>
          <DialogTitle>Borrower Details</DialogTitle>
          <DialogContent>
            <p><strong>Address:</strong> {selectedBorrower.address}</p>
            <p><strong>Loan Amount:</strong> {selectedBorrower.loanAmount}</p>
            <p><strong>Status:</strong> {selectedBorrower.loanStatus}</p>
            <p><strong>Mortgage Value:</strong> {selectedBorrower.mortgageValue}</p>
            <p><strong>Monthly Income:</strong> {selectedBorrower.monthlyIncome}</p>
            <p><strong>Credit Score:</strong> {selectedBorrower.creditScore}</p>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} color="primary">Close</Button>
          </DialogActions>
        </Dialog>
      )}

      {snackbarMessage && (
        <Snackbar
          open={true}
          autoHideDuration={3000}
          onClose={handleCloseSnackbar}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity}>
            {snackbarMessage}
          </Alert>
        </Snackbar>
      )}
    </div>
  );
};

export default BorrowerList;
