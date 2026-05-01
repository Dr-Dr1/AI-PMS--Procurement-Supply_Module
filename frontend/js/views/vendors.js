import { api } from '../api.js';
import { utils, UI } from '../utils.js';

export const VendorsView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getVendors();
            } catch (e) {
                response = { items: [] };
            }

            const headers = ['Code', 'Name', 'Email', 'Tier', 'Status', 'Actions'];
            const rows = response.items.map(v => [
                v.code,
                v.name,
                v.contact_email || 'N/A',
                `<span class="badge" style="background: #eef2ff; color: #4338ca;">${v.vendor_tier || 'N/A'}</span>`,
                utils.getStatusBadge(v.vendor_status),
                `<button class="btn btn-secondary btn-sm" data-id="${v.id}">View</button>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Vendor Directory</h2>
                    <button class="btn btn-primary" id="add-vendor-btn">
                        <i data-lucide="user-plus"></i> Add Vendor
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No vendors registered yet.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();

            // Event Listeners
            document.getElementById('add-vendor-btn').onclick = () => VendorsView.showCreateModal();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },

    showCreateModal: () => {
        const formHtml = `
            <form id="create-vendor-form">
                <div class="form-group">
                    <label>Vendor Name</label>
                    <input type="text" name="name" required placeholder="e.g. Reliance Steel">
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Vendor Code</label>
                        <input type="text" name="code" required placeholder="V-001">
                    </div>
                    <div class="form-group">
                        <label>Tier</label>
                        <select name="vendor_tier">
                            <option value="BRONZE">Bronze</option>
                            <option value="SILVER">Silver</option>
                            <option value="GOLD" selected>Gold</option>
                            <option value="PLATINUM">Platinum</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Contact Email</label>
                    <input type="email" name="contact_email" placeholder="email@example.com">
                </div>
                <div class="form-group">
                    <label>Address</label>
                    <textarea name="address" rows="2"></textarea>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancel-modal-btn">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Vendor</button>
                </div>
            </form>
        `;
        UI.openModal('Register New Vendor', formHtml);
        
        document.getElementById('cancel-modal-btn').onclick = () => UI.closeModal();
        
        document.getElementById('create-vendor-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                await api.createVendor(data);
                UI.showToast('Vendor registered successfully!', 'success');
                UI.closeModal();
                VendorsView.render();
            } catch (err) {
                UI.showToast('Failed to register vendor: ' + err.message, 'error');
            }
        };
    }
};
