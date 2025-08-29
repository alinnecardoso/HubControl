import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';
import DashboardVendas from '../pages/dashboard/DashboardVendas';
import DashboardCS from '../pages/dashboard/DashboardCS';
import DashboardExecutivo from '../pages/dashboard/DashboardExecutivo';
import DashboardAdmin from '../pages/dashboard/DashboardAdmin';

const DashboardRouter: React.FC = () => {
  // Verificar se está autenticado
  if (!authService.isAuthenticated()) {
    return <Navigate to="/auth/login" replace />;
  }

  const currentUser = authService.getCurrentUser();
  
  if (!currentUser) {
    return <Navigate to="/auth/login" replace />;
  }

  // Mapeamento de roles para dashboards (usando valores do backend)
  const getDashboardByRole = (role: string) => {
    switch (role) {
      case 'vendas':
        return <DashboardVendas />;
      case 'cs_cx':
        return <DashboardCS />;
      case 'diretoria':
        return <DashboardExecutivo />;
      case 'admin':
        return <DashboardAdmin />;
      case 'financeiro':
        return <DashboardExecutivo />; // Financeiro usa dashboard executivo
      case 'dataops':
        return <DashboardCS />; // DataOps usa dashboard similar ao CS
      default:
        // Se role desconhecido, redireciona para dashboard executivo
        return <DashboardExecutivo />;
    }
  };

  return getDashboardByRole(currentUser.role);
};

export default DashboardRouter;