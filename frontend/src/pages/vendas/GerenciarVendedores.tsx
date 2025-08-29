import React from 'react';
import { Typography } from 'antd';
import { TeamOutlined } from '@ant-design/icons';
import VendedoresTab from './tabs/VendedoresTab';

const { Title } = Typography;

const GerenciarVendedoresPage: React.FC = () => {
  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
        <TeamOutlined /> Gerenciar Vendedores
      </Title>
      <VendedoresTab />
    </div>
  );
};

export default GerenciarVendedoresPage;