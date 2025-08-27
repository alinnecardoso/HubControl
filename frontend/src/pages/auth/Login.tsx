// src/pages/auth/LoginPage.tsx
import React, { useState } from 'react';
import { Button, Form, Input, Typography, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import logo from '../../assets/logo-01.png';

const { Title, Text } = Typography;

type LoginFormValues = {
  email: string;
  password: string;
  remember?: boolean;
};

const Label: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span style={{ color: '#E6E8EA', fontWeight: 500 }}>{children}</span>
);

const RequiredLabel: React.FC<{ text: string }> = ({ text }) => (
  <span style={{ color: '#E6E8EA', fontWeight: 500 }}>
    <span style={{ color: '#F22987', marginRight: 6 }}>*</span>
    {text}
  </span>
);

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const onFinish = async (_values: LoginFormValues) => {
    try {
      setSubmitting(true);
      // TODO: autenticação real
      navigate('/');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    // FUNDO CLARO
    <div className="min-h-screen grid place-items-center px-6" style={{ background: '#F3F5F8' }}>
      {/* CARD ESCURO GRANDE */}
      <div
        style={{
          width: '100%',
          maxWidth: 820,               // maior, como no print
          backgroundColor: '#0D0D0D',
          border: '1px solid #1A1A1A',
          borderRadius: 18,
          boxShadow:
            '0 40px 80px rgba(0,0,0,.35), 0 16px 40px rgba(0,0,0,.28)', // sombra forte
          overflow: 'hidden',
        }}
      >
        {/* Barra superior em gradiente */}
        <div
          style={{
            height: 4,
            background:
              'linear-gradient(90deg,#F22987 0%,#5F328C 33%,#0D6BA6 66%,#6ACED9 100%)',
          }}
        />

        <div style={{ padding: 36 }}>
          {/* Logo */}
          <div className="flex items-center gap-3 mb-10">
            <img src={logo} alt="Logo" style={{ height: 46, width: 'auto' }} />
          </div>

          {/* Título e subtítulo */}
          <Title level={1} className="!m-0 !mb-4" style={{ color: '#E6E8EA', fontSize: 36, lineHeight: 1.2 }}>
            Gestão Inteligente
          </Title>
          <Text className="block !mb-24" style={{ color: '#C9CED6' }}>
            Faça login para continuar
          </Text>

          {/* Form */}
          <Form<LoginFormValues>
            name="login"
            layout="vertical"
            initialValues={{ remember: true }}
            onFinish={onFinish}
            requiredMark={false}
          >
            <Form.Item
              label={<RequiredLabel text="E-mail" />}
              name="email"
              rules={[
                { required: true, message: 'Por favor, insira seu e-mail!' },
                { type: 'email', message: 'E-mail inválido.' },
              ]}
              style={{ marginBottom: 20 }}
            >
              <Input
                size="large"
                prefix={<UserOutlined />}
                placeholder="seuemail@empresa.com"
                type="email"
                autoComplete="email"
                className="!rounded-xl"
                style={{
                  background: '#151515',
                  borderColor: '#262626',
                  color: '#E6E8EA',
                  height: 44,
                }}
              />
            </Form.Item>

            <Form.Item
              label={<RequiredLabel text="Senha" />}
              name="password"
              rules={[{ required: true, message: 'Por favor, insira sua senha!' }]}
              style={{ marginBottom: 8 }}
            >
              <Input.Password
                size="large"
                prefix={<LockOutlined />}
                placeholder="••••••••"
                autoComplete="current-password"
                className="!rounded-xl"
                style={{
                  background: '#151515',
                  borderColor: '#262626',
                  color: '#E6E8EA',
                  height: 44,
                }}
              />
            </Form.Item>

            <div className="flex items-center justify-between mb-16">
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox className="!text-[#C9CED6]">Lembrar-me</Checkbox>
              </Form.Item>
              <a className="text-sm" style={{ color: '#6ACED9' }}>
                Esqueci minha senha
              </a>
            </div>

            <Button
              type="primary"
              htmlType="submit"
              loading={submitting}
              size="large"
              className="!rounded-xl !border-0"
              style={{
                width: 110,
                height: 44,
                background: '#F22987', // sólido, como no print
              }}
            >
              Entrar
            </Button>
          </Form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
