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
    const allItems = [
      {
        key: '/',
        icon: <DashboardOutlined />,
        label: 'Dashboard',
        module: 'dashboard',
      },
      {
        key: '/clientes',
        icon: <UserOutlined />,
        label: 'Clientes',
        module: 'clientes',
      },
      {
        key: '/vendas',
        icon: <ShoppingCartOutlined />,
        label: 'Vendas',
        module: 'vendas',
      },
      {
        key: '/contratos',
        icon: <FileTextOutlined />,
        label: 'Contratos',
        module: 'contratos',
      },
      {
        key: '/health-score',
        icon: <HeartOutlined />,
        label: 'Health Score',
        module: 'health_score',
      },
      {
        key: '/csat',
        icon: <SmileOutlined />,
        label: 'CSAT',
        module: 'csat',
      },
      {
        key: '/ml/churn',
        icon: <RobotOutlined />,
        label: 'ML - Churn',
        module: 'ml_churn',
      },
      {
        key: '/usuarios',
        icon: <TeamOutlined />,
        label: 'Usuários',
        module: 'usuarios',
        adminOnly: true,
      },
    ];

    if (!currentUser) return [];

    return allItems.filter(item => {
      if (item.adminOnly && !authService.isAdmin()) {
        return false;
      }
      if (item.module && !authService.hasModuleAccess(item.module)) {
        return false;
      }
      return true;
    }).map(item => {
      // Remove custom properties before passing to Ant Design Menu
      const { adminOnly, module, ...menuItem } = item;
      return menuItem;
    });
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
    <Layout style={{ minHeight: '100vh', background: '#0a0a0a' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{ background: '#0D0D0D', borderRight: '1px solid #1A1A1A', boxShadow: '0 2px 8px #0004' }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(255,255,255,0.04)',
          margin: 16,
          borderRadius: 16,
        }}>
          <img
            src={logo}
            alt="HubControl"
            style={{
              height: collapsed ? 32 : 40,
              transition: 'height 0.2s',
              filter: 'drop-shadow(0 2px 6px #0008)',
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
            color: '#E6E8EA',
            fontSize: 16,
            borderRadius: 16,
          }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: '0 16px',
            background: '#141414',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 2px 8px #0008',
            borderBottom: '1px solid #1A1A1A',
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
              color: '#F22987',
            }}
          />
          <Space size="large">
            <Badge count={5} size="small">
              <Button
                type="text"
                icon={<BellOutlined style={{ color: '#6ACED9' }} />}
                size="large"
                style={{ color: '#6ACED9', background: 'transparent' }}
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
              <Space style={{ cursor: 'pointer' }}>
                <Avatar
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#F22987', color: 'white', boxShadow: '0 2px 8px #0004' }}
                />
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                  <span style={{ color: '#E6E8EA', fontWeight: 500 }}>
                    {currentUser.full_name}
                  </span>
                  <Tag 
                    color={getRoleColor(currentUser.role)} 
                    style={{ margin: 0, fontSize: '10px' }}
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
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: '#141414',
            borderRadius: 20,
            color: '#E6E8EA',
            boxShadow: '0 4px 24px #00000033',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;