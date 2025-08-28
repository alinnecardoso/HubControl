import React from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Typography, Progress, Alert } from 'antd';
import { 
  UserOutlined, 
  DollarOutlined, 
  FileTextOutlined,
  TeamOutlined,
  WarningOutlined,
  TrophyOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const AdminDashboard: React.FC = () => {
  // Dados administrativos completos - incluindo informações financeiras e contratos
  const contractData = [
    { 
      cliente: 'Empresa Alpha',
      valor: 'R$ 45.000',
      vencimento: '2024-12-15',
      status: 'Ativo',
      renovacao: 'Automática',
      responsavel: 'João Silva (Vendas)'
    },
    { 
      cliente: 'Beta Corp',
      valor: 'R$ 28.500', 
      vencimento: '2024-11-30',
      status: 'Vence em 90 dias',
      renovacao: 'Manual',
      responsavel: 'Ana Costa (CS)'
    },
    { 
      cliente: 'Gamma Ltd',
      valor: 'R$ 67.200',
      vencimento: '2025-03-20',
      status: 'Ativo',
      renovacao: 'Automática', 
      responsavel: 'Carlos Santos (Vendas)'
    }
  ];

  const userStats = [
    { setor: 'CS/CX', usuarios: 8, ativos: 7 },
    { setor: 'Vendas', usuarios: 12, ativos: 11 },
    { setor: 'Financeiro', usuarios: 4, ativos: 4 },
    { setor: 'DataOps', usuarios: 3, ativos: 3 },
    { setor: 'Diretoria', usuarios: 2, ativos: 2 }
  ];

  const contractColumns = [
    {
      title: 'Cliente',
      dataIndex: 'cliente',
      key: 'cliente',
    },
    {
      title: 'Valor Mensal',
      dataIndex: 'valor',
      key: 'valor',
      render: (valor: string) => <Text strong style={{ color: '#52c41a' }}>{valor}</Text>
    },
    {
      title: 'Vencimento',
      dataIndex: 'vencimento',
      key: 'vencimento',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'Ativo' ? 'green' : 'orange'}>
          {status}
        </Tag>
      )
    },
    {
      title: 'Renovação',
      dataIndex: 'renovacao',
      key: 'renovacao',
      render: (renovacao: string) => (
        <Tag color={renovacao === 'Automática' ? 'blue' : 'gold'}>
          {renovacao}
        </Tag>
      )
    },
    {
      title: 'Responsável',
      dataIndex: 'responsavel',
      key: 'responsavel',
    }
  ];

  const userColumns = [
    {
      title: 'Setor',
      dataIndex: 'setor',
      key: 'setor',
    },
    {
      title: 'Total de Usuários',
      dataIndex: 'usuarios',
      key: 'usuarios',
    },
    {
      title: 'Ativos',
      dataIndex: 'ativos',
      key: 'ativos',
      render: (ativos: number, record: any) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Text>{ativos}</Text>
          <Progress 
            percent={Math.round((ativos / record.usuarios) * 100)} 
            size="small" 
            showInfo={false}
            style={{ width: '60px' }}
          />
        </div>
      )
    }
  ];

  return (
    <div>
      <Title level={2} style={{ color: '#E6E8EA', marginBottom: '24px' }}>
        Dashboard Administrativo - Visão Completa
      </Title>
      
      <Alert
        message="Acesso Administrativo"
        description="Você tem acesso completo a todas as informações da empresa, incluindo dados financeiros e de contratos."
        type="info"
        showIcon
        style={{ marginBottom: '24px' }}
      />

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={4}>
          <Card>
            <Statistic
              title="Receita Mensal"
              value={187900}
              prefix="R$"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Contratos Ativos"
              value={47}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Usuários Sistema"
              value={29}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Renovações 90d"
              value={8}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Taxa Renovação"
              value={94.2}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={4}>
          <Card>
            <Statistic
              title="Ticket Médio"
              value={3998}
              prefix="R$"
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card 
            title="Contratos e Renovações"
            extra={<Tag color="red">Informação Confidencial</Tag>}
          >
            <Table
              columns={contractColumns}
              dataSource={contractData}
              pagination={false}
              rowKey="cliente"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Usuários por Setor">
            <Table
              columns={userColumns}
              dataSource={userStats}
              pagination={false}
              rowKey="setor"
              size="small"
            />
          </Card>

          <Card title="Alertas Administrativos" style={{ marginTop: '16px' }}>
            <div style={{ marginBottom: '12px' }}>
              <Tag color="red" style={{ marginBottom: '8px' }}>Crítico</Tag>
              <div style={{ fontSize: '14px' }}>
                3 contratos vencem em 30 dias - verificar renovação
              </div>
            </div>
            <div style={{ marginBottom: '12px' }}>
              <Tag color="orange" style={{ marginBottom: '8px' }}>Atenção</Tag>
              <div style={{ fontSize: '14px' }}>
                2 usuários inativos há mais de 30 dias
              </div>
            </div>
            <div>
              <Tag color="blue" style={{ marginBottom: '8px' }}>Info</Tag>
              <div style={{ fontSize: '14px' }}>
                Backup automático realizado com sucesso
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AdminDashboard;