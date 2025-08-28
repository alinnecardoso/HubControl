import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Typography, Alert, message } from 'antd';
import { LockOutlined, MailOutlined, LoginOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authService, SignInData } from '../../services/authService';
import logo from '../../assets/logo-01.png';

const { Title, Text } = Typography;

// Card de login maior e responsivo para mobile

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar se já está logado
    if (authService.isAuthenticated()) {
      navigate('/');
    }

    // Detectar se é mobile
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);

    return () => window.removeEventListener('resize', checkIsMobile);
  }, [navigate]);

  const onSignIn = async (values: SignInData) => {
    setLoading(true);
    setError(null);

    try {
      console.log('Tentando fazer login...', values);
      const response = await authService.signIn(values);
      console.log('Resposta do login:', response);
      
      message.success(`Bem-vindo, ${response.user.full_name}!`);
      
      // Redirecionar baseado no papel do usuário
      const userRole = response.user.role;
      console.log('Papel do usuário:', userRole);
      
      let redirectPath = '/';
      
      if (userRole === 'admin') {
        redirectPath = '/usuarios';
      } else if (userRole === 'diretoria') {
        redirectPath = '/';
      } else if (userRole === 'cs_cx') {
        redirectPath = '/health-score';
      } else if (userRole === 'vendas') {
        redirectPath = '/vendas';
      } else if (userRole === 'financeiro') {
        redirectPath = '/contratos';
      } else if (userRole === 'dataops') {
        redirectPath = '/ml/churn';
      }
      
      console.log('Redirecionando para:', redirectPath);
      
      // Aguardar um pouco para garantir que o token foi salvo e usar navigation
      setTimeout(() => {
        navigate(redirectPath, { replace: true });
      }, 500);
      
    } catch (error: any) {
      console.error('Erro no login:', error);
      setError(error.message || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      position: 'relative'
    }}>
      {/* Background Pattern */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundImage: `radial-gradient(circle at 25% 25%, #F22987 0%, transparent 50%), 
                          radial-gradient(circle at 75% 75%, #6ACED9 0%, transparent 50%)`,
        opacity: 0.1,
        pointerEvents: 'none'
      }}></div>
      
      <Card 
        style={{ 
          width: '100%', 
          maxWidth: isMobile ? '95%' : '800px',
          margin: isMobile ? '0 16px' : '0 16px',
          background: 'rgba(20, 20, 20, 0.95)',
          border: '1px solid #333',
          borderRadius: '20px',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
          backdropFilter: 'blur(20px)',
          position: 'relative',
          zIndex: 1
        }} 
        styles={{ 
          body: { 
            padding: isMobile ? '36px 28px' : '64px 60px'
          } 
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <img 
            src={logo} 
            alt="Logo" 
            style={{ 
              height: isMobile ? '75px' : '110px', 
              marginBottom: '32px',
              filter: 'drop-shadow(0 4px 12px rgba(242, 41, 135, 0.3))',
              maxWidth: '100%',
              objectFit: 'contain'
            }} 
          />
          <Title 
            level={3} 
            style={{ 
              margin: 0, 
              color: '#E6E8EA',
              fontWeight: '600',
              marginBottom: '8px'
            }}
          >
            Acesso ao Sistema
          </Title>
          <Text 
            style={{ 
              color: '#9CA3AF', 
              fontSize: '14px'
            }}
          >
            Entre com suas credenciais para continuar
          </Text>
        </div>

        {error && (
          <Alert 
            message={error} 
            type="error" 
            showIcon 
            closable 
            onClose={() => setError(null)}
            style={{ 
              marginBottom: '24px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '12px'
            }}
          />
        )}

        <Form
          name="signin"
          onFinish={onSignIn}
          autoComplete="off"
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Por favor, insira seu email!' },
              { type: 'email', message: 'Email inválido!' }
            ]}
          >
            <Input 
              prefix={<MailOutlined style={{ color: '#6ACED9' }} />} 
              placeholder="seu@email.com" 
              autoComplete="email"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid #333',
                borderRadius: '12px',
                color: '#E6E8EA',
                height: isMobile ? '52px' : '64px',
                fontSize: isMobile ? '16px' : '17px'
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Por favor, insira sua senha!' },
              { min: 6, message: 'Senha deve ter pelo menos 6 caracteres!' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#6ACED9' }} />}
              placeholder="Sua senha"
              autoComplete="current-password"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid #333',
                borderRadius: '12px',
                color: '#E6E8EA',
                height: isMobile ? '52px' : '64px',
                fontSize: isMobile ? '16px' : '17px'
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, marginTop: '32px' }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={loading}
              disabled={loading}
              icon={!loading ? <LoginOutlined /> : null}
              style={{
                height: isMobile ? '45px' : '45px',
                borderRadius: '14px',
                background: 'linear-gradient(135deg, #F22987 0%, #6ACED9 100%)',
                border: 'none',
                fontWeight: '600',
                fontSize: isMobile ? '16px' : '19px',
                boxShadow: '0 4px 15px rgba(242, 41, 135, 0.4)'
              }}
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: '32px' }}>
          <Text 
            style={{ 
              color: '#6B7280', 
              fontSize: '12px'
            }}
          >
            © 2025 - Sistema de Gestão Inteligente
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default Login;