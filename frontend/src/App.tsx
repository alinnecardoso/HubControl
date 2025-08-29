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
import DashboardRouter from './components/DashboardRouter';

// Pages
import Login from './pages/auth/Login';
import Clientes from './pages/clientes/Clientes';
import GerenciarDados from './pages/vendas/GerenciarDados';
import Contratos from './pages/contratos/Contratos';
import HealthScore from './pages/health-score/HealthScore';
import CSAT from './pages/csat/CSAT';
import MLChurn from './pages/ml/MLChurn';
import Usuarios from './pages/usuarios/Usuarios';

// Componentes de Vendas (páginas separadas)
import DashboardVendasPage from './pages/vendas/DashboardVendas';
import RegistroVendasPage from './pages/vendas/RegistroVendas';
import GerenciarVendedoresPage from './pages/vendas/GerenciarVendedores';

// Dashboards Específicos
import DashboardVendas from './pages/dashboard/DashboardVendas';
import DashboardCS from './pages/dashboard/DashboardCS';
import DashboardExecutivo from './pages/dashboard/DashboardExecutivo';
import DashboardAdmin from './pages/dashboard/DashboardAdmin';

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
              <Route index element={<DashboardRouter />} />
              
              {/* Dashboards específicos por role */}
              <Route path="dashboard" element={<DashboardRouter />} />
              <Route path="dashboard/vendas" element={
                <ProtectedRoute requiredRoles={['vendas', 'admin']}>
                  <DashboardVendas />
                </ProtectedRoute>
              } />
              <Route path="dashboard/cs" element={
                <ProtectedRoute requiredRoles={['cs_cx', 'admin']}>
                  <DashboardCS />
                </ProtectedRoute>
              } />
              <Route path="dashboard/executivo" element={
                <ProtectedRoute requiredRoles={['diretoria', 'admin']}>
                  <DashboardExecutivo />
                </ProtectedRoute>
              } />
              <Route path="dashboard/admin" element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <DashboardAdmin />
                </ProtectedRoute>
              } />
              
              <Route path="clientes" element={
                <ProtectedRoute requiredModules={['clientes']}>
                  <Clientes />
                </ProtectedRoute>
              } />
              
              {/* Módulos de Vendas Separados */}
              <Route path="vendas/dashboard" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <DashboardVendasPage />
                </ProtectedRoute>
              } />
              
              <Route path="vendas/registro" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <RegistroVendasPage />
                </ProtectedRoute>
              } />
              
              <Route path="vendas/vendedores" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <GerenciarVendedoresPage />
                </ProtectedRoute>
              } />
              
              <Route path="vendas/dados" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <GerenciarDados />
                </ProtectedRoute>
              } />
              
              {/* Rota de compatibilidade - redireciona vendas para vendas/dashboard */}
              <Route path="vendas" element={
                <ProtectedRoute requiredModules={['vendas']}>
                  <DashboardVendasPage />
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