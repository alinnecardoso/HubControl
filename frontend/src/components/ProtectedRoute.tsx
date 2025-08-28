import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  requiredModules?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles = [],
  requiredModules = []
}) => {
  const location = useLocation();
  
  // Verificar se está autenticado
  if (!authService.isAuthenticated()) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  const currentUser = authService.getCurrentUser();
  
  if (!currentUser) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  // Verificar se tem o papel necessário
  if (requiredRoles.length > 0 && !requiredRoles.includes(currentUser.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  // Verificar se tem acesso ao módulo necessário
  if (requiredModules.length > 0) {
    const hasModuleAccess = requiredModules.some(module => 
      currentUser.permissions.modules.includes(module)
    );
    
    if (!hasModuleAccess) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;