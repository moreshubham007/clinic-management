import axios from 'axios';
import { API_BASE_URL } from './config';
import { getAuthHeader } from './utils';

export const appointmentApi = {
  getAppointments: async (status = null) => {
    try {
      const headers = await getAuthHeader();
      const url = `${API_BASE_URL}/patient/appointments${status ? `?status=${status}` : ''}`;
      
      const response = await axios.get(url, { headers });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
}; 