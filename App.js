import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme'; // Assumes you have a theme.js file for MUI custom theme
import BorrowerList from './components/BorrowerList.js';

function App() {
    return (
        <ThemeProvider theme={theme}>
            <div>
                <BorrowerList />
            </div>
        </ThemeProvider>
    );
}

export default App;