import React, { useState } from 'react';
import {
  Card,
  Tabs,
  Typography
} from 'antd';
import {
  DashboardOutlined,
  ShoppingOutlined,
  TeamOutlined,
  DatabaseOutlined
} from '@ant-design/icons';

// Import tab components
import DashboardTab from './tabs/DashboardTab';
import VendasTab from './tabs/VendasTab';
import VendedoresTab from './tabs/VendedoresTab';
import GerenciarDados from './GerenciarDados';

const { Title } = Typography;

const Vendas: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabItems = [
    {
      key: 'dashboard',
      label: (
        <span>
          <DashboardOutlined />
          Dashboard
        </span>
      ),
      children: <DashboardTab />
    },
    {
      key: 'vendas',
      label: (
        <span>
          <ShoppingOutlined />
          Registro de Vendas
        </span>
      ),
      children: <VendasTab />
    },
    {
      key: 'vendedores',
      label: (
        <span>
          <TeamOutlined />
          Gerenciar Vendedores
        </span>
      ),
      children: <VendedoresTab />
    },
    {
      key: 'dados',
      label: (
        <span>
          <DatabaseOutlined />
          Dados/Importação
        </span>
      ),
      children: <GerenciarDados />
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2} style={{ marginBottom: '24px' }}>
        <ShoppingOutlined /> Gestão de Vendas
      </Title>
      
      <Card>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
          tabBarStyle={{ marginBottom: '24px' }}
        />
      </Card>
    </div>
  );
};

export default Vendas;