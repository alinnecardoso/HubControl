import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { Provider } from 'react-redux';
import { store } from './store/index.ts';
import ptBR from 'antd/locale/pt_BR';

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

// Styles
import './styles/global.css';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ConfigProvider
        locale={ptBR}
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          },
        }}
      >
        <Router>
          <Routes>
            {/* Rotas de autenticação */}
            <Route path="/auth" element={<AuthLayout />}>
              <Route path="login" element={<Login />} />
            </Route>

            {/* Rotas principais com layout */}
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="clientes" element={<Clientes />} />
              <Route path="vendas" element={<Vendas />} />
              <Route path="contratos" element={<Contratos />} />
              <Route path="health-score" element={<HealthScore />} />
              <Route path="csat" element={<CSAT />} />
              <Route path="ml/churn" element={<MLChurn />} />
              <Route path="usuarios" element={<Usuarios />} />
            </Route>
          </Routes>
        </Router>
      </ConfigProvider>
    </Provider>
  );
};

export default App; 