/**
 * Serviço de Autenticação Frontend
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8005/api/v1';

// Configurar interceptor para incluir token automaticamente
axios.defaults.baseURL = API_BASE_URL;
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para lidar com erros de autenticação
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: {
    modules: string[];
    actions: string[];
    data_access: string;
  };
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface SignUpData {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

export interface SignInData {
  email: string;
  password: string;
}

export interface Role {
  value: string;
  name: string;
  description: string;
}

class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly USER_KEY = 'user_data';

  /**
   * Registrar novo usuário
   */
  async signUp(userData: SignUpData): Promise<AuthResponse> {
    try {
      const response = await axios.post('/auth/signup', userData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro no registro');
    }
  }

  /**
   * Fazer login
   */
  async signIn(credentials: SignInData): Promise<AuthResponse> {
    try {
      // Fazer requisição simples para evitar preflight CORS
      const response = await axios({
        method: 'post',
        url: '/auth/signin',
        data: credentials,
        headers: {
          'Content-Type': 'application/json'
        },
        withCredentials: false  // Desabilitar cookies para evitar preflight
      });
      const authData: AuthResponse = response.data;
      
      // Salvar token e dados do usuário
      localStorage.setItem(this.TOKEN_KEY, authData.access_token);
      localStorage.setItem(this.USER_KEY, JSON.stringify(authData.user));
      
      return authData;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro no login');
    }
  }

  /**
   * Fazer logout
   */
  signOut(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    window.location.href = '/auth/login';
  }

  /**
   * Verificar se está logado
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obter token atual
   */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Obter dados do usuário atual
   */
  getCurrentUser(): User | null {
    const userData = localStorage.getItem(this.USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Validar token atual
   */
  async validateToken(): Promise<boolean> {
    try {
      await axios.get('/auth/validate-token');
      return true;
    } catch {
      this.signOut();
      return false;
    }
  }

  /**
   * Obter informações atualizadas do usuário
   */
  async getUserInfo(): Promise<User> {
    try {
      const response = await axios.get('/auth/me');
      const user = response.data.user;
      
      // Atualizar cache local
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      
      return user;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao buscar dados do usuário');
    }
  }

  /**
   * Verificar se usuário tem acesso a um módulo
   */
  hasModuleAccess(moduleName: string): boolean {
    const user = this.getCurrentUser();
    return user?.permissions.modules.includes(moduleName) || false;
  }

  /**
   * Verificar se usuário tem uma permissão específica
   */
  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    return user?.permissions.actions.includes(permission) || false;
  }

  /**
   * Verificar se usuário tem um papel específico
   */
  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  /**
   * Verificar se usuário é admin
   */
  isAdmin(): boolean {
    return this.hasRole('admin');
  }

  /**
   * Obter papéis disponíveis no sistema (apenas admins)
   */
  async getAvailableRoles(): Promise<Role[]> {
    try {
      const response = await axios.get('/auth/roles');
      return response.data.roles;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao buscar papéis');
    }
  }

  /**
   * Listar usuários (apenas admins)
   */
  async listUsers(): Promise<User[]> {
    try {
      const response = await axios.get('/auth/users');
      return response.data.users;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao listar usuários');
    }
  }

  /**
   * Atualizar papel de usuário (apenas admins)
   */
  async updateUserRole(userId: string, newRole: string): Promise<void> {
    try {
      await axios.put('/auth/users/role', {
        user_id: userId,
        new_role: newRole
      });
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao atualizar papel');
    }
  }

  /**
   * Desativar usuário (apenas admins)
   */
  async deactivateUser(userId: string): Promise<void> {
    try {
      await axios.put(`/auth/users/${userId}/deactivate`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Erro ao desativar usuário');
    }
  }

  /**
   * Obter nome amigável do papel
   */
  getRoleName(role: string): string {
    const roleNames: { [key: string]: string } = {
      'admin': 'Administrador',
      'diretoria': 'Diretoria',
      'cs_cx': 'Customer Success/Experience',
      'financeiro': 'Financeiro',
      'vendas': 'Vendas',
      'dataops': 'DataOps'
    };
    
    return roleNames[role] || role;
  }

  /**
   * Obter cor do papel para UI
   */
  getRoleColor(role: string): string {
    const roleColors: { [key: string]: string } = {
      'admin': 'red',
      'diretoria': 'purple',
      'cs_cx': 'blue',
      'financeiro': 'green',
      'vendas': 'orange',
      'dataops': 'cyan'
    };
    
    return roleColors[role] || 'default';
  }
}

export const authService = new AuthService();