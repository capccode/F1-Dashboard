import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import theme from './theme'; // Ensure this is the correct path to your theme
import DashboardComponent from './components/dashboard_component';

function App() {
  return (
    <ChakraProvider theme={theme}>
      {/* Render the DashboardComponent directly */}
      <DashboardComponent />
    </ChakraProvider>
  );
}

export default App;
