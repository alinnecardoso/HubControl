import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, Space, Typography, Badge } from 'antd';
import {
  DashboardOutlined,
  ShoppingCartOutlined,
  CustomerServiceOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  TrophyOutlined,
  CrownOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
  userRole?: string;
  userName?: string;
  userEmail?: string;
}

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
  roles: string[];
}

const MainLayout: React.FC<MainLayoutProps> = ({ 
  children, 
  userRole = 'VENDAS', 
  userName = 'Isaac Silva',
  userEmail = 'isaac@hubcontrol.com'
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Itens de menu baseados em roles
  const menuItems: MenuItem[] = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      path: '/dashboard',
      roles: ['VENDAS', 'CS_CX', 'DIRETORIA', 'ADMIN']
    },
    {
      key: 'vendas',
      icon: <ShoppingCartOutlined />,
      label: 'Vendas',
      path: '/vendas',
      roles: ['VENDAS', 'DIRETORIA', 'ADMIN']
    },
    {
      key: 'clientes',
      icon: <CustomerServiceOutlined />,
      label: 'Clientes',
      path: '/clientes',
      roles: ['CS_CX', 'VENDAS', 'DIRETORIA', 'ADMIN']
    },
    {
      key: 'contratos',
      icon: <TrophyOutlined />,
      label: 'Contratos',
      path: '/contratos',
      roles: ['CS_CX', 'DIRETORIA', 'ADMIN']
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics',
      path: '/analytics',
      roles: ['DIRETORIA', 'ADMIN']
    },
    {
      key: 'admin',
      icon: <SafetyCertificateOutlined />,
      label: 'Administração',
      path: '/admin',
      roles: ['ADMIN']
    },
    {
      key: 'configuracoes',
      icon: <SettingOutlined />,
      label: 'Configurações',
      path: '/configuracoes',
      roles: ['VENDAS', 'CS_CX', 'DIRETORIA', 'ADMIN']
    }
  ];

  // Filtra itens do menu baseado no role do usuário
  const getFilteredMenuItems = () => {
    return menuItems
      .filter(item => item.roles.includes(userRole))
      .map(item => ({
        key: item.key,
        icon: item.icon,
        label: item.label,
        onClick: () => navigate(item.path)
      }));
  };

  // Menu do perfil do usuário
  const profileMenu = {
    items: [
      {
        key: 'profile',
        icon: <UserOutlined />,
        label: 'Meu Perfil',
        onClick: () => navigate('/perfil')
      },
      {
        key: 'settings',
        icon: <SettingOutlined />,
        label: 'Configurações',
        onClick: () => navigate('/configuracoes')
      },
      {
        type: 'divider' as const
      },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: 'Sair',
        onClick: () => {
          // Implementar logout
          localStorage.removeItem('token');
          navigate('/login');
        }
      }
    ]
  };

  // Define o título da aplicação baseado no role
  const getAppTitle = () => {
    switch (userRole) {
      case 'VENDAS':
        return 'HubControl Sales';
      case 'CS_CX':
        return 'HubControl CS';
      case 'DIRETORIA':
        return 'HubControl Executive';
      case 'ADMIN':
        return 'HubControl Admin';
      default:
        return 'HubControl';
    }
  };

  // Define a cor do tema baseado no role
  const getThemeColor = () => {
    switch (userRole) {
      case 'VENDAS':
        return '#1890ff';
      case 'CS_CX':
        return '#52c41a';
      case 'DIRETORIA':
        return '#722ed1';
      case 'ADMIN':
        return '#f5222d';
      default:
        return '#1890ff';
    }
  };

  // Badge do role
  const getRoleBadge = () => {
    const roleConfig = {
      'VENDAS': { color: 'blue', icon: <ShoppingCartOutlined /> },
      'CS_CX': { color: 'green', icon: <CustomerServiceOutlined /> },
      'DIRETORIA': { color: 'purple', icon: <CrownOutlined /> },
      'ADMIN': { color: 'red', icon: <SafetyCertificateOutlined /> }
    };

    const config = roleConfig[userRole as keyof typeof roleConfig] || roleConfig.VENDAS;
    
    return (
      <Space>
        {config.icon}
        <Text style={{ color: 'white' }}>{userRole}</Text>
      </Space>
    );
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: getThemeColor(),
        }}
      >
        <div style={{ 
          height: 32, 
          margin: 16, 
          color: 'white',
          fontSize: collapsed ? 14 : 16,
          fontWeight: 'bold',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          {collapsed ? 'HC' : getAppTitle()}
        </div>
        
        <Menu
          mode="inline"
          selectedKeys={[location.pathname.split('/')[1] || 'dashboard']}
          items={getFilteredMenuItems()}
          style={{
            background: getThemeColor(),
            border: 'none'
          }}
          theme="dark"
        />
      </Sider>
      
      <Layout>
        <Header style={{ 
          padding: '0 16px', 
          background: '#fff', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: '16px',
                width: 64,
                height: 64,
              }}
            />
            {getRoleBadge()}
          </div>

          <Space size="middle">
            <Badge count={3} size="small">
              <Button 
                type="text" 
                icon={<BellOutlined />} 
                size="large"
              />
            </Badge>

            <Dropdown menu={profileMenu} placement="bottomRight">
              <Button type="text" style={{ padding: '4px 8px' }}>
                <Space>
                  <Avatar 
                    size="small" 
                    icon={<UserOutlined />}
                    style={{ backgroundColor: getThemeColor() }}
                  />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: '14px', fontWeight: 500 }}>{userName}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>{userEmail}</div>
                  </div>
                </Space>
              </Button>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ 
          margin: '24px 16px', 
          padding: 24, 
          minHeight: 280,
          background: '#f0f2f5'
        }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;