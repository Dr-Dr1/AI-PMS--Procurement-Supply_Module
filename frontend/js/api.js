const API_BASE_URL = '/api/v1';

class ApiService {
    async request(endpoint, options = {}) {
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
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // Dashboard
    getDashboardSummary() {
        return this.request('/procurement/dashboard/summary');
    }

    // Vendors
    getVendors(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/procurement/vendors?${query}`);
    }
    createVendor(data) {
        return this.request('/procurement/vendors', { method: 'POST', body: JSON.stringify(data) });
    }

    // Materials
    getMaterials(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/procurement/materials?${query}`);
    }
    createMaterial(data) {
        return this.request('/procurement/materials', { method: 'POST', body: JSON.stringify(data) });
    }

    // Purchase Orders
    getPurchaseOrders(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/procurement/purchase-orders?${query}`);
    }
    createPurchaseOrder(data) {
        return this.request('/procurement/purchase-orders', { method: 'POST', body: JSON.stringify(data) });
    }

    // Deliveries
    getDeliveries(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/procurement/deliveries?${query}`);
    }

    // FAT Tests
    getFATTests(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/procurement/fat-tests?${query}`);
    }
}

export const api = new ApiService();
