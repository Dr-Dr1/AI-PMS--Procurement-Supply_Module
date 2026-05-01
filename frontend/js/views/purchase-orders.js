import { api } from '../api.js';
import { utils, UI } from '../utils.js';

export const PurchaseOrdersView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getPurchaseOrders();
            } catch (e) {
                response = { items: [] };
            }

            const headers = ['PO Number', 'Title', 'Amount', 'Date', 'Status', 'Actions'];
            const rows = response.items.map(po => [
                `<strong>${po.po_number}</strong>`,
                po.title,
                utils.formatCurrency(po.total_amount),
                utils.formatDate(po.created_at),
                utils.getStatusBadge(po.status),
                `<button class="btn btn-secondary btn-sm">View PO</button>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Purchase Orders</h2>
                    <button class="btn btn-primary" id="create-po-btn">
                        <i data-lucide="plus-circle"></i> Create PO
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No purchase orders found.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();

            document.getElementById('create-po-btn').onclick = () => PurchaseOrdersView.showCreateModal();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },

    showCreateModal: () => {
        const formHtml = `
            <form id="create-po-form">
                <div class="form-group">
                    <label>PO Title</label>
                    <input type="text" name="title" required placeholder="e.g. Annual Steel Supply">
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>PO Number</label>
                        <input type="text" name="po_number" required placeholder="PO-2024-XXX">
                    </div>
                    <div class="form-group">
                        <label>Vendor</label>
                        <select name="vendor_id" required>
                            <option value="">Select Vendor...</option>
                            <option value="1">Global Steel Ltd</option>
                            <option value="2">Tech Logistics</option>
                        </select>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancel-modal-btn">Cancel</button>
                    <button type="submit" class="btn btn-primary">Draft Purchase Order</button>
                </div>
            </form>
        `;
        UI.openModal('Create New Purchase Order', formHtml);
        
        document.getElementById('cancel-modal-btn').onclick = () => UI.closeModal();
        
        document.getElementById('create-po-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            data.line_items = []; 
            
            try {
                await api.createPurchaseOrder(data);
                UI.showToast('Purchase Order created!', 'success');
                UI.closeModal();
                PurchaseOrdersView.render();
            } catch (err) {
                UI.showToast('Failed to create PO: ' + err.message, 'error');
            }
        };
    }
};
