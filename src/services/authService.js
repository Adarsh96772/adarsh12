class AuthService {
  constructor() {
    this.token = localStorage.getItem('token');
    this.user = this.getUser();
    this.role = localStorage.getItem('role') || 'user';
  }

  setAuth(token, user) {
    this.token = token;
    this.user = user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }

  setRole(role) {
    this.role = role;
    localStorage.setItem('role', role);
  }

  getRole() {
    return this.role || localStorage.getItem('role') || 'user';
  }

  getToken() {
    return this.token || localStorage.getItem('token');
  }

  getUser() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch {
      return null;
    }
  }

  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch {
      return false;
    }
  }

  logout() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
  }

  getUserId() {
    return this.user?._id || this.user?.id || null;
  }

  getUserName() {
    return this.user?.name || 'Guest';
  }
}

export default new AuthService();