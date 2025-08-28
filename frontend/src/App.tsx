import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { Provider } from 'react-redux';
import { store } from './store/index';
import ptBR from 'antd/locale/pt_BR';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Components
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/auth/Login';
import Dashboard from './pages/Dashboard';
import Clientes from './pages/clientes/Clientes';
import Vendas from './pages/vendas/Vendas';
import Contratos from './pages/contratos/Contratos';
import HealthScore from './pages/health-score/HealthScore';
import CSAT from './pages/csat/CSAT';
import MLChurn from './pages/ml/MLChurn';
import Usuarios from './pages/usuarios/Usuarios';

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
              
              <Route path="clientes" element={
                <ProtectedRoute requiredModules={['clientes']}>
                  <Clientes />
                </ProtectedRoute>
              } />
              
              <Route path="vendas" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <Vendas />
                </ProtectedRoute>
              } />
              
              <Route path="contratos" element={
                <ProtectedRoute requiredModules={['contratos']}>
                  <Contratos />
                </ProtectedRoute>
              } />
              
              <Route path="health-score" element={
                <ProtectedRoute requiredModules={['health_score']}>
                  <HealthScore />
                </ProtectedRoute>
              } />
              
              <Route path="csat" element={
                <ProtectedRoute requiredModules={['csat']}>
                  <CSAT />
                </ProtectedRoute>
              } />
              
              <Route path="ml/churn" element={
                <ProtectedRoute requiredModules={['ml_churn']}>
                  <MLChurn />
                </ProtectedRoute>
              } />
              
              <Route path="usuarios" element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <Usuarios />
                </ProtectedRoute>
              } />
            </Route>
          </Routes>
        </Router>
      </ConfigProvider>
    </Provider>
  );
};

export default App; 