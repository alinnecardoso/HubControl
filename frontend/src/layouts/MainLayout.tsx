import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Badge,
  Space,
  Tag,
  message,
} from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  UserOutlined,
  ShoppingCartOutlined,
  FileTextOutlined,
  HeartOutlined,
  SmileOutlined,
  RobotOutlined,
  TeamOutlined,
  BellOutlined,
  LogoutOutlined,
  SettingOutlined,
  BarChartOutlined,
  ShoppingOutlined,
  DatabaseOutlined,
  PieChartOutlined,
} from '@ant-design/icons';
import { authService, User } from '../services/authService';
import logo from '../assets/logo-01.png';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Verificar autenticação e buscar dados do usuário
    const checkAuth = async () => {
      console.log('Verificando autenticação...');
      console.log('Token existe:', authService.isAuthenticated());
      
      if (!authService.isAuthenticated()) {
        console.log('Usuário não autenticado, redirecionando para login');
        navigate('/auth/login');
        return;
      }

      try {
        // Primeiro tentar obter usuário do localStorage
        const cachedUser = authService.getCurrentUser();
        console.log('Usuário no cache:', cachedUser);
        
        if (cachedUser) {
          setCurrentUser(cachedUser);
        } else {
          // Se não encontrar no cache, tentar buscar do servidor
          const user = await authService.getUserInfo();
          console.log('Usuário do servidor:', user);
          setCurrentUser(user);
        }
      } catch (error) {
        console.error('Erro ao buscar dados do usuário:', error);
        message.error('Sessão expirada, faça login novamente');
        authService.signOut();
      }
    };

    checkAuth();
  }, [navigate]);

  // Filtrar itens de menu baseado nas permissões do usuário
  const getFilteredMenuItems = () => {
    if (!currentUser) return [];

    const menuItems: any[] = [
      // Dashboard principal
      {
        key: '/',
        icon: <DashboardOutlined />,
        label: 'Dashboard Geral',
      },
    ];

    // Módulo Clientes (acessível a quase todos os setores)
    if (authService.hasModuleAccess('clientes')) {
      menuItems.push({
        key: '/clientes',
        icon: <UserOutlined />,
        label: 'Clientes',
      });
    }

    // Módulos de Vendas (itens separados no menu principal)
    if (authService.hasModuleAccess('vendas_dashboard')) {
      menuItems.push({
        key: '/vendas/dashboard',
        icon: <PieChartOutlined />,
        label: 'Dashboard Vendas',
      });
    }

    if (authService.hasModuleAccess('vendas_registro')) {
      menuItems.push({
        key: '/vendas/registro',
        icon: <ShoppingOutlined />,
        label: 'Registro de Vendas',
      });
    }

    if (authService.hasModuleAccess('vendas_vendedores')) {
      menuItems.push({
        key: '/vendas/vendedores',
        icon: <TeamOutlined />,
        label: 'Gerenciar Vendedores',
      });
    }

    if (authService.hasModuleAccess('vendas_dados')) {
      menuItems.push({
        key: '/vendas/dados',
        icon: <DatabaseOutlined />,
        label: 'Importar/Exportar Dados',
      });
    }

    // Módulo Contratos (Financeiro)
    if (authService.hasModuleAccess('contratos')) {
      menuItems.push({
        key: '/contratos',
        icon: <FileTextOutlined />,
        label: 'Contratos',
      });
    }

    // Módulo Health Score (CS/CX)
    if (authService.hasModuleAccess('health_score')) {
      menuItems.push({
        key: '/health-score',
        icon: <HeartOutlined />,
        label: 'Health Score',
      });
    }

    // Módulo CSAT (CS/CX)
    if (authService.hasModuleAccess('csat')) {
      menuItems.push({
        key: '/csat',
        icon: <SmileOutlined />,
        label: 'CSAT',
      });
    }

    // Módulo ML Churn (DataOps)
    if (authService.hasModuleAccess('ml_churn')) {
      menuItems.push({
        key: '/ml/churn',
        icon: <RobotOutlined />,
        label: 'Predição de Churn',
      });
    }

    // Módulo Usuários (apenas admin)
    if (authService.hasModuleAccess('usuarios')) {
      menuItems.push({
        key: '/usuarios',
        icon: <SettingOutlined />,
        label: 'Gerenciar Usuários',
      });
    }

    return menuItems;
  };

  // Menu do usuário
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Meu Perfil',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Configurações',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sair',
      onClick: () => handleLogout(),
    },
  ];

  const handleLogout = () => {
    message.success('Até logo!');
    authService.signOut();
  };

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  // Função para obter cor do papel
  const getRoleColor = (role: string) => {
    const colors: { [key: string]: string } = {
      'admin': 'red',
      'diretoria': 'purple',
      'cs_cx': 'blue',
      'financeiro': 'green',
      'vendas': 'orange',
      'dataops': 'cyan'
    };
    return colors[role] || 'default';
  };

  // Função para obter nome amigável do papel
  const getRoleName = (role: string) => {
    const names: { [key: string]: string } = {
      'admin': 'Administrador',
      'diretoria': 'Diretoria',
      'cs_cx': 'CS/CX',
      'financeiro': 'Financeiro',
      'vendas': 'Vendas',
      'dataops': 'DataOps'
    };
    return names[role] || role;
  };

  if (!currentUser) {
    return null; // Ou um loading spinner
  }

  return (
    <Layout style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{ 
          background: 'var(--bg-secondary)', 
          borderRight: '1px solid var(--border-light)', 
          boxShadow: 'var(--shadow-small)' 
        }}
      >
        <div style={{
          height: 72,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(255,255,255,0.05)',
          margin: 16,
          borderRadius: 'var(--radius-large)',
          transition: 'all 0.3s ease',
        }}>
          <img
            src={logo}
            alt="HubControl"
            style={{
              height: collapsed ? 32 : 40,
              transition: 'height 0.3s ease',
              filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))',
              objectFit: 'contain',
              maxWidth: '80%',
            }}
          />
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={getFilteredMenuItems()}
          onClick={handleMenuClick}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: 14,
            fontWeight: 500,
            padding: '0 8px',
          }}
        />
      </Sider>
      <Layout style={{ background: 'var(--bg-primary)' }}>
        <Header
          style={{
            padding: '0 var(--spacing-lg)',
            background: 'var(--bg-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: 'var(--shadow-small)',
            borderBottom: '1px solid var(--border-light)',
            height: 72,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '18px',
              width: 48,
              height: 48,
              color: 'var(--secondary-color)',
              borderRadius: 'var(--radius-medium)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(242, 41, 135, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          />
          <Space size="large">
            <Badge count={3} size="small" style={{ backgroundColor: 'var(--warning-color)' }}>
              <Button
                type="text"
                icon={<BellOutlined style={{ color: 'var(--accent-color)', fontSize: '18px' }} />}
                size="large"
                style={{ 
                  color: 'var(--accent-color)', 
                  background: 'transparent',
                  borderRadius: 'var(--radius-medium)',
                  width: 48,
                  height: 48,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(106, 206, 217, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              />
            </Badge>
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: ({ key }) => {
                  const item = userMenuItems.find(i => i.key === key);
                  if (item && 'onClick' in item && item.onClick) {
                    item.onClick();
                  }
                },
              }}
              placement="bottomRight"
              arrow
            >
              <Space 
                style={{ 
                  cursor: 'pointer', 
                  padding: 'var(--spacing-sm) var(--spacing-md)',
                  borderRadius: 'var(--radius-medium)',
                  transition: 'all 0.3s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              >
                <Avatar
                  icon={<UserOutlined />}
                  style={{ 
                    backgroundColor: 'var(--secondary-color)', 
                    color: 'white', 
                    boxShadow: 'var(--shadow-small)',
                    border: '2px solid rgba(255, 255, 255, 0.1)',
                  }}
                  size={42}
                />
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span style={{ 
                    color: 'var(--text-primary)', 
                    fontWeight: 600,
                    fontSize: '14px',
                    lineHeight: '1.2',
                  }}>
                    {currentUser.full_name}
                  </span>
                  <Tag 
                    color={getRoleColor(currentUser.role)} 
                    style={{ 
                      margin: '2px 0 0 0', 
                      fontSize: '11px',
                      fontWeight: 500,
                      borderRadius: 'var(--radius-small)',
                      border: 'none',
                    }}
                  >
                    {getRoleName(currentUser.role)}
                  </Tag>
                </div>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        <Content
          style={{
            margin: 'var(--spacing-lg)',
            padding: 'var(--spacing-xl)',
            minHeight: 'calc(100vh - 120px)',
            background: 'var(--bg-card)',
            borderRadius: 'var(--radius-xl)',
            color: 'var(--text-secondary)',
            boxShadow: 'var(--shadow-medium)',
            border: '1px solid var(--border-light)',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;