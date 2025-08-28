import React from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag, Typography } from 'antd';
import { 
  UserOutlined, 
  HeartOutlined, 
  SmileOutlined,
  TrophyOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const CSCXDashboard: React.FC = () => {
  // Dados mock específicos para CS/CX - SEM informações de renovação de contratos
  const healthScoreData = [
    { 
      cliente: 'Empresa Alpha', 
      score: 85, 
      status: 'Saudável',
      ultimoContato: '2024-08-25',
      responsavel: 'Ana Silva'
    },
    { 
      cliente: 'Beta Corp', 
      score: 45, 
      status: 'Risco',
      ultimoContato: '2024-08-20',
      responsavel: 'Carlos Santos'
    },
    { 
      cliente: 'Gamma Ltd', 
      score: 92, 
      status: 'Excelente',
      ultimoContato: '2024-08-27',
      responsavel: 'Maria Costa'
    }
  ];

  const csatData = [
    {
      periodo: 'Agosto 2024',
      score: 4.2,
      respostas: 156,
      nps: 35
    },
    {
      periodo: 'Julho 2024', 
      score: 4.0,
      respostas: 142,
      nps: 28
    }
  ];

  const columns = [
    {
      title: 'Cliente',
      dataIndex: 'cliente',
      key: 'cliente',
    },
    {
      title: 'Health Score',
      dataIndex: 'score',
      key: 'score',
      render: (score: number) => (
        <Progress 
          percent={score} 
          size="small"
          strokeColor={score > 70 ? '#52c41a' : score > 50 ? '#faad14' : '#ff4d4f'}
        />
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'Excelente' ? 'green' : status === 'Saudável' ? 'blue' : 'red'}>
          {status}
        </Tag>
      )
    },
    {
      title: 'Último Contato',
      dataIndex: 'ultimoContato',
      key: 'ultimoContato',
    },
    {
      title: 'Responsável CS',
      dataIndex: 'responsavel',
      key: 'responsavel',
    }
  ];

  return (
    <div>
      <Title level={2} style={{ color: '#E6E8EA', marginBottom: '24px' }}>
        Dashboard CS/CX - Relacionamento com Clientes
      </Title>
      
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes Ativos"
              value={127}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Health Score Médio"
              value={74}
              suffix="%"
              prefix={<HeartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="CSAT Médio"
              value={4.2}
              suffix="/5"
              prefix={<SmileOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Clientes em Risco"
              value={8}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card 
            title="Health Score por Cliente"
            extra={<Tag color="blue">Atualizado em tempo real</Tag>}
          >
            <Table
              columns={columns}
              dataSource={healthScoreData}
              pagination={false}
              rowKey="cliente"
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Satisfação dos Clientes (CSAT)">
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Score Atual: </Text>
              <Tag color="green" style={{ fontSize: '14px' }}>4.2/5</Tag>
            </div>
            
            {csatData.map((item, index) => (
              <div key={index} style={{ marginBottom: '12px', padding: '8px', backgroundColor: 'rgba(255,255,255,0.02)', borderRadius: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <Text>{item.periodo}</Text>
                  <Text strong>{item.score}/5</Text>
                </div>
                <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                  {item.respostas} respostas • NPS: {item.nps}
                </div>
              </div>
            ))}
          </Card>

          <Card title="Ações Recomendadas" style={{ marginTop: '16px' }}>
            <div style={{ marginBottom: '12px' }}>
              <Tag color="red" style={{ marginBottom: '8px' }}>Urgente</Tag>
              <div style={{ fontSize: '14px' }}>
                Contatar Beta Corp - Score baixo há 7 dias
              </div>
            </div>
            <div style={{ marginBottom: '12px' }}>
              <Tag color="orange" style={{ marginBottom: '8px' }}>Médio</Tag>
              <div style={{ fontSize: '14px' }}>
                Agendar call de check-in com 5 clientes
              </div>
            </div>
            <div>
              <Tag color="green" style={{ marginBottom: '8px' }}>Oportunidade</Tag>
              <div style={{ fontSize: '14px' }}>
                Gamma Ltd - candidato para case de sucesso
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CSCXDashboard;