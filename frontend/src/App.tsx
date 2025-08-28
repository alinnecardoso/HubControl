import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { Provider } from 'react-redux';
import { store } from './store/index.ts';
import ptBR from 'antd/locale/pt_BR';

// Styles
import './styles/global.css';

// Layouts
import MainLayout from './layouts/MainLayout.tsx';
import AuthLayout from './layouts/AuthLayout.tsx';

// Pages
import Login from './pages/auth/Login.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Clientes from './pages/clientes/Clientes.tsx';
import Vendas from './pages/vendas/Vendas.tsx';
import Contratos from './pages/contratos/Contratos.tsx';
import HealthScore from './pages/health-score/HealthScore.tsx';
import CSAT from './pages/csat/CSAT.tsx';
import MLChurn from './pages/ml/MLChurn.tsx';
import Usuarios from './pages/usuarios/Usuarios.tsx';

// Placeholder functions for role checking (will be replaced with actual logic)
const isAssessor = (): boolean => {
  return false; // Default to false for now
};

// Replace with actual logic to check if the user has the 'assessor' role
const isStaff = (): boolean => {
  // Replace with actual logic to check if the user has a staff role ('cs', 'diretoria', 'admin', 'financeiro')
  return false; // Default to false for now
};

const Formularios = () => <div>Formularios Page Placeholder</div>; // Temporary placeholder


const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ConfigProvider
        locale={ptBR}
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#F22987', // Use primary color from design spec
            borderRadius: 6,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          },
        }}
      >
        <BrowserRouter>
          <Routes>
            {/* Authentication Routes */}
            <Route path="/auth" element={<AuthLayout />}>
              <Route path="login" element={<Login />} />
              {/* Add other auth routes like signup, forgot password here if needed */}
            </Route>

            {/* Main Application Routes with MainLayout */}
            <Route
              path="/"
              element={<MainLayout />} // This route defines the MainLayout for its children
            >
              {/* Default redirect within MainLayout based on role */}
              <Route index element={<Dashboard />} />

              {/* Assessor Routes */}
              <Route path="formularios" element={<Formularios />} /> {/* Access /formularios */}

              {/* Staff Routes */}
              <Route path="clientes" element={<Clientes />} />
              <Route path="vendas" element={<Vendas />} />
              <Route path="contratos" element={<Contratos />} />
              <Route path="health-score" element={<HealthScore />} />
              <Route path="csat" element={<CSAT />} />
              <Route path="ml/churn" element={<MLChurn />} />
              <Route path="usuarios" element={<Usuarios />} />
              {/* Add other staff routes here (e.g., /adman, /dimensoes-health) */}
            </Route>

            {/* Add a Not Found page later */}
            {/* <Route path="*" element={<NotFound />} /> */}
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </Provider>
  );
};

export default App; 