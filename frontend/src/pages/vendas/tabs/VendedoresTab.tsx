import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Input,
  DatePicker,
  Select,
  Modal,
  Form,
  message,
  Row,
  Col,
  Tooltip,
  Typography,
  Tag,
  Statistic
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  DollarOutlined,
  UserOutlined,
  TrophyOutlined
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';

const { RangePicker } = DatePicker;
const { Text, Title } = Typography;

interface Vendedor {
  id: number;
  nome: string;
  email: string;
  equipe_vendas_id?: number;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

interface VendedorForm {
  nome: string;
  email: string;
  equipe_vendas_id?: number;
}

interface BonificacaoVendedor {
  vendedor_id: number;
  vendedor_nome: string;
  total_vendas: number;
  valor_total_vendas: number;
  valor_total_bonificacao: number;
  periodo_inicio: string;
  periodo_fim: string;
}

const VendedoresTab: React.FC = () => {
  const [vendedores, setVendedores] = useState<Vendedor[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [bonificacaoModalVisible, setBonificacaoModalVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentVendedor, setCurrentVendedor] = useState<Vendedor | null>(null);
  const [bonificacao, setBonificacao] = useState<BonificacaoVendedor | null>(null);
  const [form] = Form.useForm();
  const [bonificacaoForm] = Form.useForm();
  
  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  const loadVendedores = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: ((currentPage - 1) * pageSize).toString(),
        limit: pageSize.toString(),
      });
      
      const response = await fetch(`http://localhost:8004/api/v1/sales/vendedores?${params}`);
      if (response.ok) {
        const data = await response.json();
        setVendedores(data);
      } else {
        message.error('Erro ao carregar vendedores');
      }
    } catch (error) {
      message.error('Erro ao carregar vendedores');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadVendedores();
  }, [currentPage, pageSize]);

  const handleCreate = () => {
    setEditMode(false);
    setCurrentVendedor(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Vendedor) => {
    setEditMode(true);
    setCurrentVendedor(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirmar desativação',
      content: 'Tem certeza que deseja desativar este vendedor?',
      onOk: async () => {
        try {
          const response = await fetch(`http://localhost:8004/api/v1/sales/vendedores/${id}`, {
            method: 'DELETE'
          });
          if (response.ok) {
            message.success('Vendedor desativado com sucesso');
            loadVendedores();
          } else {
            message.error('Erro ao desativar vendedor');
          }
        } catch (error) {
          message.error('Erro ao desativar vendedor');
        }
      }
    });
  };

  const handleSubmit = async (values: VendedorForm) => {
    try {
      const url = editMode ? 
        `http://localhost:8004/api/v1/sales/vendedores/${currentVendedor?.id}` : 
        'http://localhost:8004/api/v1/sales/vendedores';
      const method = editMode ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success(`Vendedor ${editMode ? 'atualizado' : 'criado'} com sucesso`);
        setModalVisible(false);
        loadVendedores();
      } else {
        const error = await response.json();
        message.error(error.detail || 'Erro ao salvar vendedor');
      }
    } catch (error) {
      message.error('Erro ao salvar vendedor');
    }
  };

  const handleCalcularBonificacao = (vendedor: Vendedor) => {
    setCurrentVendedor(vendedor);
    bonificacaoForm.resetFields();
    setBonificacao(null);
    setBonificacaoModalVisible(true);
  };

  const handleBonificacaoSubmit = async (values: any) => {
    try {
      const params = new URLSearchParams({
        data_inicio: values.data_inicio,
        data_fim: values.data_fim
      });

      const response = await fetch(
        `http://localhost:8004/api/v1/sales/vendedores/${currentVendedor?.id}/bonificacao?${params}`
      );

      if (response.ok) {
        const data = await response.json();
        setBonificacao(data);
      } else {
        message.error('Erro ao calcular bonificação');
      }
    } catch (error) {
      message.error('Erro ao calcular bonificação');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const columns: ColumnsType<Vendedor> = [
    {
      title: 'Nome',
      dataIndex: 'nome',
      key: 'nome',
      ellipsis: true,
      sorter: true
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      ellipsis: true,
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      render: (_, record: Vendedor) => (
        <Tag color={record.ativo ? 'green' : 'red'}>
          {record.ativo ? 'Ativo' : 'Inativo'}
        </Tag>
      )
    },
    {
      title: 'Criado em',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (text: string) => formatDate(text),
      sorter: true
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record: Vendedor) => (
        <Space>
          <Tooltip title="Calcular Bonificação">
            <Button 
              type="text" 
              icon={<DollarOutlined />}
              onClick={() => handleCalcularBonificacao(record)}
            />
          </Tooltip>
          <Tooltip title="Editar">
            <Button 
              type="text" 
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="Desativar">
            <Button 
              type="text" 
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
              disabled={!record.ativo}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  return (
    <div>
      {/* Barra de ação */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={24}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Button 
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              Novo Vendedor
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Tabela */}
      <Card>
        <Table
          columns={columns}
          dataSource={vendedores}
          rowKey="id"
          loading={loading}
          scroll={{ x: 800 }}
          pagination={{
            current: currentPage,
            pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} de ${total} vendedores`,
            onChange: (page, size) => {
              setCurrentPage(page);
              setPageSize(size || 10);
            }
          }}
          size="small"
        />
      </Card>

      {/* Modal de Cadastro/Edição */}
      <Modal
        title={editMode ? 'Editar Vendedor' : 'Novo Vendedor'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="nome"
            label="Nome Completo"
            rules={[{ required: true, message: 'Nome é obrigatório' }]}
          >
            <Input placeholder="Nome completo do vendedor" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Email é obrigatório' },
              { type: 'email', message: 'Email inválido' }
            ]}
          >
            <Input placeholder="email@exemplo.com" />
          </Form.Item>

          <Form.Item
            name="equipe_vendas_id"
            label="Equipe de Vendas"
            tooltip="Campo opcional para futuras expansões"
          >
            <Input placeholder="ID da equipe (opcional)" type="number" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancelar
              </Button>
              <Button type="primary" htmlType="submit">
                {editMode ? 'Atualizar' : 'Salvar'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal de Bonificação */}
      <Modal
        title={`Bonificação - ${currentVendedor?.nome}`}
        open={bonificacaoModalVisible}
        onCancel={() => setBonificacaoModalVisible(false)}
        footer={null}
        width={700}
        destroyOnClose
      >
        <Form
          form={bonificacaoForm}
          layout="vertical"
          onFinish={handleBonificacaoSubmit}
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="data_inicio"
                label="Data de Início"
                rules={[{ required: true, message: 'Data de início é obrigatória' }]}
              >
                <Input type="date" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="data_fim"
                label="Data de Fim"
                rules={[{ required: true, message: 'Data de fim é obrigatória' }]}
              >
                <Input type="date" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              Calcular Bonificação
            </Button>
          </Form.Item>
        </Form>

        {bonificacao && (
          <Card style={{ marginTop: '16px' }}>
            <Title level={4}>Resultado da Bonificação</Title>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="Total de Vendas"
                    value={bonificacao.total_vendas}
                    prefix={<TrophyOutlined />}
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="Valor Total Vendas"
                    value={bonificacao.valor_total_vendas}
                    formatter={(value) => formatCurrency(Number(value))}
                    prefix={<DollarOutlined />}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="Total Bonificação"
                    value={bonificacao.valor_total_bonificacao}
                    formatter={(value) => formatCurrency(Number(value))}
                    prefix={<DollarOutlined />}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
            </Row>
            
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary">
                Período: {formatDate(bonificacao.periodo_inicio)} até {formatDate(bonificacao.periodo_fim)}
              </Text>
            </div>
          </Card>
        )}
      </Modal>
    </div>
  );
};

export default VendedoresTab;