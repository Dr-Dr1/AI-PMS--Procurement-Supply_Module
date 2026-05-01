const API_BASE_URL = '/api/v1';

const api = {
    async fetch(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.message || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    },

    // Dashboard
    getDashboardSummary: () => api.fetch('/procurement/dashboard/summary'),

    // Vendors
    getVendors: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return api.fetch(`/procurement/vendors?${query}`);
    },
    getVendor: (id) => api.fetch(`/procurement/vendors/${id}`),
    createVendor: (data) => api.fetch('/procurement/vendors', { method: 'POST', body: JSON.stringify(data) }),
    updateVendor: (id, data) => api.fetch(`/procurement/vendors/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    // Materials
    getMaterials: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return api.fetch(`/procurement/materials?${query}`);
    },
    getMaterial: (id) => api.fetch(`/procurement/materials/${id}`),
    createMaterial: (data) => api.fetch('/procurement/materials', { method: 'POST', body: JSON.stringify(data) }),

    // Purchase Orders
    getPurchaseOrders: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return api.fetch(`/procurement/purchase-orders?${query}`);
    },
    getPurchaseOrder: (id) => api.fetch(`/procurement/purchase-orders/${id}`),
    createPurchaseOrder: (data) => api.fetch('/procurement/purchase-orders', { method: 'POST', body: JSON.stringify(data) }),
    updatePOStatus: (id, status, remarks) => api.fetch(`/procurement/purchase-orders/${id}/status`, { 
        method: 'PATCH', 
        body: JSON.stringify({ status, remarks }) 
    }),

    // Deliveries
    getDeliveries: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return api.fetch(`/procurement/deliveries?${query}`);
    },
    getDelivery: (id) => api.fetch(`/procurement/deliveries/${id}`),
    createDelivery: (data) => api.fetch('/procurement/deliveries', { method: 'POST', body: JSON.stringify(data) }),

    // FAT Tests
    getFATTests: (params = {}) => {
        const query = new URLSearchParams(params).toString();
        return api.fetch(`/procurement/fat-tests?${query}`);
    },
    getFATTest: (id) => api.fetch(`/procurement/fat-tests/${id}`),
    scheduleFAT: (data) => api.fetch('/procurement/fat-tests', { method: 'POST', body: JSON.stringify(data) }),
};
