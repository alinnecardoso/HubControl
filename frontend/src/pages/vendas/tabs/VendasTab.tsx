import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Input,
  DatePicker,
  Select,
  Tag,
  Modal,
  Form,
  InputNumber,
  message,
  Row,
  Col,
  Tooltip,
  Typography
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  FilterOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { ColumnsType } from 'antd/es/table';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Text } = Typography;

interface Cliente {
  id: number;
  nome_principal: string;
  nickname: string;
}

interface Vendedor {
  id: number;
  nome: string;
  email: string;
}

interface Venda {
  id: number;
  data_venda: string;
  loja: string;
  cliente_id: number;
  vendedor_id: number;
  produto: string;
  valor_mensal: number;
  contrato_meses: number;
  forma_pagamento: string;
  canal_venda?: string;
  telefone_cliente?: string;
  percentual_variavel?: number;
  descricao?: string;
  info_adicional?: string;
  valor_total_contrato: number;
  valor_bonificacao: number;
  valor_total_com_bonificacao: number;
  is_recente: boolean;
  is_mes_atual: boolean;
  is_trimestre_atual: boolean;
  created_at: string;
  updated_at: string;
  cliente?: Cliente;
  vendedor?: Vendedor;
}

interface VendaForm {
  data_venda: string;
  loja: string;
  cliente_id: number;
  vendedor_id: number;
  produto: string;
  valor_mensal: number;
  contrato_meses: number;
  forma_pagamento: string;
  canal_venda?: string;
  telefone_cliente?: string;
  percentual_variavel?: number;
  descricao?: string;
  info_adicional?: string;
}

interface Filtros {
  data_inicio?: string;
  data_fim?: string;
  vendedor_id?: number;
  cliente_id?: number;
  loja?: string;
  produto?: string;
}

const VendasTab: React.FC = () => {
  const [vendas, setVendas] = useState<Venda[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentVenda, setCurrentVenda] = useState<Venda | null>(null);
  const [form] = Form.useForm();
  const [filtros, setFiltros] = useState<Filtros>({});
  
  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  // Estados para selects
  const [vendedores, setVendedores] = useState<Vendedor[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [lojas, setLojas] = useState<string[]>([]);
  const [produtos, setProdutos] = useState<string[]>([]);

  const loadVendas = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: ((currentPage - 1) * pageSize).toString(),
        limit: pageSize.toString(),
        ...(Object.entries(filtros).reduce((acc, [key, value]) => {
          if (value !== undefined) {
            acc[key] = value.toString();
          }
          return acc;
        }, {} as Record<string, string>))
      });
      
      const response = await fetch(`http://localhost:8004/api/v1/sales/vendas?${params}`);
      if (response.ok) {
        const data = await response.json();
        setVendas(data);
        
        // Extrai lojas e produtos únicos para filtros
        const lojasSet = new Set<string>();
        const produtosSet = new Set<string>();
        
        data.forEach((v: Venda) => {
          if (v.loja) lojasSet.add(v.loja);
          if (v.produto) produtosSet.add(v.produto);
        });
        
        setLojas(Array.from(lojasSet));
        setProdutos(Array.from(produtosSet));
      } else {
        message.error('Erro ao carregar vendas');
      }
    } catch (error) {
      message.error('Erro ao carregar vendas');
    }
    setLoading(false);
  };

  const loadVendedores = async () => {
    try {
      const response = await fetch('http://localhost:8004/api/v1/sales/vendedores');
      if (response.ok) {
        const data = await response.json();
        setVendedores(data);
      }
    } catch (error) {
      console.error('Erro ao carregar vendedores:', error);
    }
  };

  const loadClientes = async () => {
    try {
      const response = await fetch('http://localhost:8004/api/v1/sales/clientes');
      if (response.ok) {
        const data = await response.json();
        setClientes(data);
      }
    } catch (error) {
      console.error('Erro ao carregar clientes:', error);
    }
  };

  useEffect(() => {
    loadVendas();
    loadVendedores();
    loadClientes();
  }, [currentPage, pageSize, filtros]);

  const handleCreate = () => {
    setEditMode(false);
    setCurrentVenda(null);
    form.resetFields();
    form.setFieldsValue({
      data_venda: new Date().toISOString().split('T')[0],
      contrato_meses: 12,
      forma_pagamento: 'cartao'
    });
    setModalVisible(true);
  };

  const handleEdit = (record: Venda) => {
    setEditMode(true);
    setCurrentVenda(record);
    form.setFieldsValue({
      ...record,
      data_venda: new Date(record.data_venda).toISOString().split('T')[0]
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Confirmar exclusão',
      content: 'Tem certeza que deseja excluir esta venda?',
      onOk: async () => {
        try {
          const response = await fetch(`http://localhost:8004/api/v1/sales/vendas/${id}`, {
            method: 'DELETE'
          });
          if (response.ok) {
            message.success('Venda excluída com sucesso');
            loadVendas();
          } else {
            message.error('Erro ao excluir venda');
          }
        } catch (error) {
          message.error('Erro ao excluir venda');
        }
      }
    });
  };

  const handleSubmit = async (values: VendaForm) => {
    try {
      const url = editMode ? `http://localhost:8004/api/v1/sales/vendas/${currentVenda?.id}` : 'http://localhost:8004/api/v1/sales/vendas';
      const method = editMode ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(values)
      });
      
      if (response.ok) {
        message.success(`Venda ${editMode ? 'atualizada' : 'criada'} com sucesso`);
        setModalVisible(false);
        loadVendas();
      } else {
        const error = await response.json();
        message.error(error.detail || 'Erro ao salvar venda');
      }
    } catch (error) {
      message.error('Erro ao salvar venda');
    }
  };

  const handleViewDetails = (record: Venda) => {
    setCurrentVenda(record);
    setDetailModalVisible(true);
  };

  const handleFilterChange = (key: string, value: any) => {
    setFiltros(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFiltros({});
    setCurrentPage(1);
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

  const columns: ColumnsType<Venda> = [
    {
      title: 'Data',
      dataIndex: 'data_venda',
      key: 'data_venda',
      width: 120,
      render: (text: string) => formatDate(text),
      sorter: true
    },
    {
      title: 'Loja',
      dataIndex: 'loja',
      key: 'loja',
      width: 120,
      ellipsis: true
    },
    {
      title: 'Cliente',
      key: 'cliente',
      width: 150,
      ellipsis: true,
      render: (_, record: Venda) => (
        <Tooltip title={record.cliente?.nickname}>
          {record.cliente?.nome_principal || 'N/A'}
        </Tooltip>
      )
    },
    {
      title: 'Produto',
      dataIndex: 'produto',
      key: 'produto',
      width: 150,
      ellipsis: true
    },
    {
      title: 'Vendedor',
      key: 'vendedor',
      width: 120,
      ellipsis: true,
      render: (_, record: Venda) => record.vendedor?.nome || 'N/A'
    },
    {
      title: 'Valor Mensal',
      dataIndex: 'valor_mensal',
      key: 'valor_mensal',
      width: 120,
      render: (text: number) => formatCurrency(text),
      sorter: true
    },
    {
      title: 'Contrato',
      dataIndex: 'contrato_meses',
      key: 'contrato_meses',
      width: 80,
      render: (text: number) => `${text}m`
    },
    {
      title: 'Valor Total',
      dataIndex: 'valor_total_contrato',
      key: 'valor_total_contrato',
      width: 120,
      render: (text: number) => formatCurrency(text)
    },
    {
      title: 'Bonificação',
      dataIndex: 'valor_bonificacao',
      key: 'valor_bonificacao',
      width: 110,
      render: (text: number) => text > 0 ? formatCurrency(text) : '-'
    },
    {
      title: 'Status',
      key: 'status',
      width: 100,
      render: (_, record: Venda) => (
        <Space direction="vertical" size="small">
          {record.is_recente && <Tag color="green">Recente</Tag>}
          {record.is_mes_atual && <Tag color="blue">Mês Atual</Tag>}
        </Space>
      )
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record: Venda) => (
        <Space>
          <Tooltip title="Ver detalhes">
            <Button 
              type="text" 
              icon={<EyeOutlined />}
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          <Tooltip title="Editar">
            <Button 
              type="text" 
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Tooltip title="Excluir">
            <Button 
              type="text" 
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record.id)}
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
              Nova Venda
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Filtros */}
      <Card 
        title={<><FilterOutlined /> Filtros</>}
        size="small"
        style={{ marginBottom: '16px' }}
      >
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <RangePicker
              placeholder={['Data início', 'Data fim']}
              style={{ width: '100%' }}
              onChange={(dates) => {
                if (dates && dates[0] && dates[1]) {
                  handleFilterChange('data_inicio', dates[0].format('YYYY-MM-DD'));
                  handleFilterChange('data_fim', dates[1].format('YYYY-MM-DD'));
                } else {
                  handleFilterChange('data_inicio', undefined);
                  handleFilterChange('data_fim', undefined);
                }
              }}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Vendedor"
              style={{ width: '100%' }}
              allowClear
              onChange={(value) => handleFilterChange('vendedor_id', value)}
            >
              {vendedores.map(v => (
                <Option key={v.id} value={v.id}>{v.nome}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="Loja"
              style={{ width: '100%' }}
              allowClear
              onChange={(value) => handleFilterChange('loja', value)}
            >
              {lojas.map(loja => (
                <Option key={loja} value={loja}>{loja}</Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="Produto"
              prefix={<SearchOutlined />}
              onChange={(e) => handleFilterChange('produto', e.target.value || undefined)}
            />
          </Col>
        </Row>
        <Row style={{ marginTop: '8px' }}>
          <Col>
            <Button onClick={clearFilters}>Limpar Filtros</Button>
          </Col>
        </Row>
      </Card>

      {/* Tabela */}
      <Card>
        <Table
          columns={columns}
          dataSource={vendas}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            current: currentPage,
            pageSize,
            total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} de ${total} vendas`,
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
        title={editMode ? 'Editar Venda' : 'Nova Venda'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="data_venda"
                label="Data da Venda"
                rules={[{ required: true, message: 'Data é obrigatória' }]}
              >
                <Input type="date" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="loja"
                label="Loja"
                rules={[{ required: true, message: 'Loja é obrigatória' }]}
              >
                <Input placeholder="Nome da loja" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="cliente_id"
                label="Cliente"
                rules={[{ required: true, message: 'Cliente é obrigatório' }]}
              >
                <Select 
                  placeholder="Selecione o cliente"
                  showSearch
                  optionFilterProp="children"
                >
                  {clientes.map(cliente => (
                    <Option key={cliente.id} value={cliente.id}>
                      {cliente.nome_principal} ({cliente.nickname})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="vendedor_id"
                label="Vendedor"
                rules={[{ required: true, message: 'Vendedor é obrigatório' }]}
              >
                <Select 
                  placeholder="Selecione o vendedor"
                  showSearch
                  optionFilterProp="children"
                >
                  {vendedores.map(vendedor => (
                    <Option key={vendedor.id} value={vendedor.id}>
                      {vendedor.nome}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="produto"
                label="Produto/Serviço"
                rules={[{ required: true, message: 'Produto é obrigatório' }]}
              >
                <Input placeholder="Nome do produto ou serviço" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="valor_mensal"
                label="Valor Mensal"
                rules={[{ required: true, message: 'Valor mensal é obrigatório' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="0,00"
                  min={0}
                  precision={2}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="contrato_meses"
                label="Contrato (meses)"
                rules={[{ required: true, message: 'Duração do contrato é obrigatória' }]}
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={120}
                  placeholder="12"
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="forma_pagamento"
                label="Forma de Pagamento"
                rules={[{ required: true, message: 'Forma de pagamento é obrigatória' }]}
              >
                <Select placeholder="Selecione a forma de pagamento">
                  <Option value="cartao">Cartão de Crédito</Option>
                  <Option value="boleto">Boleto</Option>
                  <Option value="pix">PIX</Option>
                  <Option value="transferencia">Transferência</Option>
                  <Option value="dinheiro">Dinheiro</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="canal_venda"
                label="Canal de Venda"
              >
                <Select placeholder="Selecione o canal de venda">
                  <Option value="loja_fisica">Loja Física</Option>
                  <Option value="online">Online</Option>
                  <Option value="telefone">Telefone</Option>
                  <Option value="whatsapp">WhatsApp</Option>
                  <Option value="email">E-mail</Option>
                  <Option value="indicacao">Indicação</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="telefone_cliente"
                label="Telefone do Cliente"
              >
                <Input placeholder="(11) 99999-9999" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="percentual_variavel"
            label="Percentual Variável (%)"
            tooltip="Percentual de bonificação sobre o valor mensal"
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              max={100}
              precision={2}
              placeholder="0,00"
            />
          </Form.Item>

          <Form.Item
            name="descricao"
            label="Descrição"
          >
            <Input.TextArea rows={2} placeholder="Descrição da venda..." />
          </Form.Item>

          <Form.Item
            name="info_adicional"
            label="Informações Adicionais"
          >
            <Input.TextArea rows={2} placeholder="Informações adicionais..." />
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

      {/* Modal de Detalhes */}
      <Modal
        title="Detalhes da Venda"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            Fechar
          </Button>
        ]}
        width={600}
      >
        {currentVenda && (
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={12}>
                <Text strong>Data:</Text><br />
                <Text>{formatDate(currentVenda.data_venda)}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Loja:</Text><br />
                <Text>{currentVenda.loja}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Cliente:</Text><br />
                <Text>{currentVenda.cliente?.nome_principal || 'N/A'}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Vendedor:</Text><br />
                <Text>{currentVenda.vendedor?.nome || 'N/A'}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Produto:</Text><br />
                <Text>{currentVenda.produto}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Forma de Pagamento:</Text><br />
                <Text>{currentVenda.forma_pagamento}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Valor Mensal:</Text><br />
                <Text>{formatCurrency(currentVenda.valor_mensal)}</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Contrato:</Text><br />
                <Text>{currentVenda.contrato_meses} meses</Text>
              </Col>
              <Col xs={12}>
                <Text strong>Valor Total do Contrato:</Text><br />
                <Text strong style={{ color: '#52c41a' }}>
                  {formatCurrency(currentVenda.valor_total_contrato)}
                </Text>
              </Col>
              <Col xs={12}>
                <Text strong>Bonificação:</Text><br />
                <Text style={{ color: '#1890ff' }}>
                  {currentVenda.valor_bonificacao > 0 
                    ? formatCurrency(currentVenda.valor_bonificacao)
                    : 'Sem bonificação'
                  }
                </Text>
              </Col>
            </Row>

            {(currentVenda.descricao || currentVenda.info_adicional) && (
              <>
                <Space direction="vertical" style={{ marginTop: '16px', width: '100%' }}>
                  {currentVenda.descricao && (
                    <div>
                      <Text strong>Descrição:</Text><br />
                      <Text>{currentVenda.descricao}</Text>
                    </div>
                  )}
                  {currentVenda.info_adicional && (
                    <div>
                      <Text strong>Informações Adicionais:</Text><br />
                      <Text>{currentVenda.info_adicional}</Text>
                    </div>
                  )}
                </Space>
              </>
            )}

            <div style={{ marginTop: '16px' }}>
              <Space>
                {currentVenda.is_recente && <Tag color="green">Venda Recente</Tag>}
                {currentVenda.is_mes_atual && <Tag color="blue">Mês Atual</Tag>}
                {currentVenda.is_trimestre_atual && <Tag color="purple">Trimestre Atual</Tag>}
              </Space>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default VendasTab;