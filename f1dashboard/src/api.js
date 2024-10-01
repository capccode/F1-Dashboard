// frontend/f1dashboard/src/api.js

import axios from 'axios';

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/';

export const getTelemetry = (params) => {
  return axios.get(`${API_BASE_URL}telemetry_data/`, { params });
};

export const getGrandPrixOptions = (params) => {
  return axios.get(`${API_BASE_URL}grand_prix_options/`, { params });
};

export const getSessionOptions = (params) => {
  return axios.get(`${API_BASE_URL}session_options/`, { params });
};

export const getDriverOptions = (params) => {
  return axios.get(`${API_BASE_URL}driver_options/`, { params });
};

export const getLapInfo = (params) => {
  return axios.get(`${API_BASE_URL}lap_info/`, { params });
};