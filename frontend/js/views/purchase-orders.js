const PurchaseOrdersView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getPurchaseOrders();
            } catch (e) {
                response = {
                    items: [
                        { id: '1', po_number: 'PO-2024-001', title: 'Q1 Steel Supply', total_amount: 500000, status: 'APPROVED', created_at: '2024-04-01' },
                        { id: '2', po_number: 'PO-2024-002', title: 'Cement Batch B', total_amount: 250000, status: 'PENDING', created_at: '2024-04-15' },
                    ]
                };
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
                    <button class="btn btn-primary" onclick="PurchaseOrdersView.showCreateModal()">
                        <i data-lucide="plus-circle"></i> Create PO
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No purchase orders found.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            lucide.createIcons();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },

    showCreateModal: () => {
        const formHtml = `
            <form id="create-po-form">
                <div class="form-group">
                    <label>PO Title</label>
                    <input type="text" name="title" required placeholder="e.g. Annual Steel Supply - Phase 1">
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
                <div class="form-grid">
                    <div class="form-group">
                        <label>Expected Delivery</label>
                        <input type="date" name="expected_delivery_date">
                    </div>
                    <div class="form-group">
                        <label>Currency</label>
                        <select name="currency">
                            <option value="INR">INR</option>
                            <option value="USD">USD</option>
                            <option value="EUR">EUR</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Terms & Conditions</label>
                    <textarea name="terms_and_conditions" rows="3"></textarea>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Draft Purchase Order</button>
                </div>
            </form>
        `;
        UI.openModal('Create New Purchase Order', formHtml);
        
        document.getElementById('create-po-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            data.line_items = []; // Basic implementation
            
            try {
                await api.createPurchaseOrder(data);
                UI.closeModal();
                PurchaseOrdersView.render();
            } catch (err) {
                alert('Failed to create PO: ' + err.message);
            }
        };
    }
};
