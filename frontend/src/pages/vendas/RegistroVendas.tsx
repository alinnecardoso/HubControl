import React from 'react';
import { Typography } from 'antd';
import { ShoppingOutlined } from '@ant-design/icons';
import VendasTab from './tabs/VendasTab';

const { Title } = Typography;

const RegistroVendasPage: React.FC = () => {
  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
        <ShoppingOutlined /> Registro de Vendas
      </Title>
      <VendasTab />
    </div>
  );
};

export default RegistroVendasPage;