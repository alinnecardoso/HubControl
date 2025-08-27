// src/pages/dashboard/Dashboard.tsx
import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  UserOutlined,
  ShoppingCartOutlined,
  FileTextOutlined,
  HeartOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface DashboardStatsProps {
  totalClients: number;
  monthlySales: number;       // valor numérico (ex.: 12345.67)
  activeContracts: number;
  averageHealthScore: number; // 1..5
}

const DashboardStats: React.FC<DashboardStatsProps> = ({
  totalClients,
  monthlySales,
  activeContracts,
  averageHealthScore,
}) => {
  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title={<Text className="text-base sm:text-lg text-gray-600">Total de Clientes</Text>}
            value={totalClients}
            prefix={<UserOutlined className="text-xl sm:text-2xl" />}
            valueStyle={{ color: '#3f8600' }}
          />
        </Card>{' '}
      </Col>

      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title={<Text className="text-base sm:text-lg text-gray-600">Vendas do Mês</Text>}
            value={monthlySales}
            precision={2}
            // Se quiser moeda BRL antes do número, use formatter (descomente abaixo):
            // formatter={(val) => (typeof val === 'number'
            //   ? val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
            //   : val)}
            prefix={<ShoppingCartOutlined className="text-xl sm:text-2xl" />}
            valueStyle={{ color: '#cf1322' }}
          />
        </Card>{' '}
      </Col>

      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title={<Text className="text-base sm:text-lg text-gray-600">Contratos Ativos</Text>}
            value={activeContracts}
            prefix={<FileTextOutlined className="text-xl sm:text-2xl" />}
          />
        </Card>{' '}
      </Col>

      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title={<Text className="text-base sm:text-lg text-gray-600">Health Score Médio</Text>}
            value={averageHealthScore}
            precision={2}
            suffix="/5"
            prefix={<HeartOutlined className="text-xl sm:text-2xl" />}
            valueStyle={{
              color:
                averageHealthScore >= 4
                  ? '#3f8600' // verde
                  : averageHealthScore >= 3
                  ? '#faad14' // amarelo
                  : '#cf1322', // vermelho
            }}
          />
        </Card>{' '}
      </Col>
    </Row>
  );
};
export default DashboardStats;
