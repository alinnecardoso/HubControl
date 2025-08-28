import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import AdminDashboard from './dashboards/AdminDashboard';
import CSCXDashboard from './dashboards/CSCXDashboard';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const currentUser = authService.getCurrentUser();
  
  useEffect(() => {
    if (!currentUser) {
      navigate('/auth/login');
      return;
    }
    
    // Redirecionar usuários específicos para suas páginas principais
    const userRole = currentUser.role;
    
    if (userRole === 'vendas') {
      navigate('/vendas');
    } else if (userRole === 'financeiro') {
      navigate('/contratos');
    } else if (userRole === 'dataops') {
      navigate('/ml/churn');
    }
  }, [currentUser, navigate]);

  if (!currentUser) {
    return null;
  }

  // Renderizar dashboard específico baseado no papel
  switch (currentUser.role) {
    case 'admin':
      return <AdminDashboard />;
    case 'cs_cx':
      return <CSCXDashboard />;
    case 'diretoria':
      return <AdminDashboard />; // Diretoria vê tudo como admin
    default:
      return <AdminDashboard />; // Fallback
  }
};

export default Dashboard; 