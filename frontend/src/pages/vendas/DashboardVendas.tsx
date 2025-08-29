import React from 'react';
import { Typography } from 'antd';
import { PieChartOutlined } from '@ant-design/icons';
import DashboardTab from './tabs/DashboardTab';

const { Title } = Typography;

const DashboardVendasPage: React.FC = () => {
  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px', color: 'var(--text-primary)' }}>
        <PieChartOutlined /> Dashboard de Vendas
      </Title>
      <DashboardTab />
    </div>
  );
};

export default DashboardVendasPage;