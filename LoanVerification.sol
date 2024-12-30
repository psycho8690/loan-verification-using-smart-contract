// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract LoanVerification {
    enum LoanStatus { Pending, Approved, Rejected }

    struct Borrower {
        uint loanAmount;
        LoanStatus loanStatus;
        uint mortgageValue;
        uint monthlyIncome;
        uint creditScore;
    }

    mapping(address => Borrower) public borrowers;
    mapping(address => bool) private existingBorrowers; // Track if a borrower is already added
    address[] public borrowerAddresses;

    event BorrowerUpdated(
        address indexed borrower,
        uint loanAmount,
        LoanStatus loanStatus,
        uint mortgageValue,
        uint monthlyIncome
    );

    function validateLoan(
        uint loanAmount,
        uint mortgageValue,
        uint monthlyIncome,
        uint creditScore
    ) public pure returns (bool) {
        if (mortgageValue >= loanAmount) {
            return true;
        }
        if ((monthlyIncome * 2 + creditScore * 10 + mortgageValue) >= loanAmount) {
            return true;
        }
        return false;
    }

    function addOrUpdateBorrower(
        address _borrower,
        uint256 _loanAmount,
        uint256 _mortgageValue,
        uint256 _monthlyIncome,
        uint256 _creditScore
    ) public {
        require(_borrower != address(0), "Invalid borrower address");
        require(_loanAmount > 0, "Loan amount must be greater than zero");

        // Only add to the array if the borrower is not already in the system
        if (!existingBorrowers[_borrower]) {
            borrowerAddresses.push(_borrower);
            existingBorrowers[_borrower] = true;
        }

        borrowers[_borrower] = Borrower(
            _loanAmount,
            LoanStatus.Pending,
            _mortgageValue,
            _monthlyIncome,
            _creditScore
        );

        emit BorrowerUpdated(
            _borrower,
            _loanAmount,
            LoanStatus.Pending,
            _mortgageValue,
            _monthlyIncome
        );
    }

    function getBorrower(address _borrower) public view returns (uint, LoanStatus, uint, uint, uint) {
        Borrower memory b = borrowers[_borrower];

        // Check if the borrower exists and return default values if not
        if (!existingBorrowers[_borrower]) {
            return (0, LoanStatus.Pending, 0, 0, 0); // Default values
        }

        return (b.loanAmount, b.loanStatus, b.mortgageValue, b.monthlyIncome, b.creditScore);
    }

    function updateLoanStatus(address _borrower, LoanStatus _loanStatus) public {
        require(existingBorrowers[_borrower], "Borrower not found");
        borrowers[_borrower].loanStatus = _loanStatus;

        emit BorrowerUpdated(
            _borrower,
            borrowers[_borrower].loanAmount,
            _loanStatus,
            borrowers[_borrower].mortgageValue,
            borrowers[_borrower].monthlyIncome
        );
    }

    function getAllBorrowers() public view returns (address[] memory, Borrower[] memory) {
        uint256 count = borrowerAddresses.length;

        if (count == 0) {
            return (new address[](0), new Borrower[](0));
   }

        Borrower[] memory allBorrowers = new Borrower[](count);
        for (uint i = 0; i < count; i++) {
            allBorrowers[i] = borrowers[borrowerAddresses[i]];
        }
        return (borrowerAddresses, allBorrowers);
    }

    function getBorrowerCount() public view returns (uint256) {
        return borrowerAddresses.length;
    }
}

   