import { defineStore } from 'pinia';
import { api } from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('pims_token') || null,
    user: JSON.parse(localStorage.getItem('pims_user') || 'null')
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.rol === 'admin',
    isJefe: (state) => state.user?.rol === 'jefe'
  },
  actions: {
    async login(email, password) {
      const data = await api.login(email, password);
      this.token = data.access_token;
      this.user = data.user;
      localStorage.setItem('pims_token', data.access_token);
      localStorage.setItem('pims_user', JSON.stringify(data.user));
      return data;
    },
    async checkAuth() {
      if (!this.token) return false;
      try {
        const user = await api.getMe();
        this.user = user;
        localStorage.setItem('pims_user', JSON.stringify(user));
        return true;
      } catch (err) {
        this.logout();
        return false;
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('pims_token');
      localStorage.removeItem('pims_user');
    }
  }
});
