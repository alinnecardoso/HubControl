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
  Typography,
  theme,
} from 'antd'; // Import Menu types
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
  LogoutOutlined, // Keep LogoutOutlined for user menu
  SettingOutlined,
} from '@ant-design/icons';
import Logo from '../assets/logo-01.png'; // Import the logo
import { MenuItemType, MenuDividerType } from 'antd/es/menu/interface'; // Import specific types


const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // Menu items
  const menuItems: MenuItemType[] = [ // Explicitly type as MenuItemType[]
    { 
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/clientes',
      icon: <UserOutlined />, // Use UserOutlined component directly
      label: 'Clientes',
    },
    {
      key: '/vendas',
      icon: <ShoppingCartOutlined />, // Use ShoppingCartOutlined component directly
      label: 'Vendas',
    },
    {
      key: '/contratos',
      icon: <FileTextOutlined />, // Use FileTextOutlined component directly
      label: 'Contratos',
    },
    {
      key: '/health-score',
      icon: <HeartOutlined />, // Use HeartOutlined component directly
      label: 'Health Score',
    },
    {
      key: '/csat',
      icon: <SmileOutlined />, // Use SmileOutlined component directly
      label: 'CSAT',
    },
    {
      key: '/ml/churn',
      icon: <RobotOutlined />, // Use RobotOutlined component directly
      label: 'ML - Churn',
    },
    {
      key: '/usuarios',
      icon: <TeamOutlined />, // Use TeamOutlined component directly
      label: 'Usuários',
    },
  ];

  // User menu
  const userMenuItems: (MenuItemType | MenuDividerType)[] = [ // Explicitly type
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Meu Perfil',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Configurações',
    },
    {
      // Correctly define the divider type
      type: 'divider' as 'divider', // Explicitly cast to 'divider'
    },
    {
      key: 'logout',
      label: 'Sair',
      icon: <LogoutOutlined />, // Use LogoutOutlined component directly
      onClick: () => {
        // TODO: Implementar logout
        navigate('/auth/login');
      },
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} breakpoint="sm" collapsedWidth="0">
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: 'rgba(255, 255, 255, 0.1)',
          margin: 16,
          borderRadius: 6
        }}>
          <img src={Logo} alt="HubControl Logo" style={{ height: '32px', display: 'block', margin: '0 auto' }} />
        </div>
        
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      
      <Layout>
        <Header style={{ 
          padding: '0 16px', 
          background: colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
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
          
          <Space size="large">
            <Badge count={5} size="small">
              <Button 
                type="text" 
                icon={<BellOutlined />} 
                size="large"
              />
            </Badge>
            
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              arrow
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar 
                  icon={<UserOutlined />} 
                  style={{ backgroundColor: '#1890ff' }}
                />
                <span>Admin</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content
          className="p-6 md:p-6 sm:p-4 xs:p-2" // Use Tailwind responsive padding classes
          style={{ // Keep other styles
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 