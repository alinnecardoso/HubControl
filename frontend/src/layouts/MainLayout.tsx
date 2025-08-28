import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Badge,
  Space,
  theme,
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
import logo from '../assets/logo-01.png';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // Menu items
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/clientes',
      icon: <UserOutlined />,
      label: 'Clientes',
    },
    {
      key: '/vendas',
      icon: <ShoppingCartOutlined />,
      label: 'Vendas',
    },
    {
      key: '/contratos',
      icon: <FileTextOutlined />,
      label: 'Contratos',
    },
    {
      key: '/health-score',
      icon: <HeartOutlined />,
      label: 'Health Score',
    },
    {
      key: '/csat',
      icon: <SmileOutlined />,
      label: 'CSAT',
    },
    {
      key: '/ml/churn',
      icon: <RobotOutlined />,
      label: 'ML - Churn',
    },
    {
      key: '/usuarios',
      icon: <TeamOutlined />,
      label: 'Usuários',
    },
  ];

  // User menu para Dropdown (Ant Design v5)
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
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sair',
      onClick: () => navigate('/auth/login'),
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

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
          items={menuItems}
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
                  if (item && item.onClick) item.onClick();
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
                <span style={{ color: '#E6E8EA', fontWeight: 500 }}>Admin</span>
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