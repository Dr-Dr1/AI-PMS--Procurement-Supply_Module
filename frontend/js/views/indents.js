import { api } from '../api.js';
import { utils, UI } from '../utils.js';

export const IndentsView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getIndents();
            } catch (e) {
                response = { items: [] };
            }

            const headers = ['Number', 'Requested By', 'Need Date', 'Status', 'Actions'];
            const rows = response.items.map(i => [
                i.indent_number,
                i.requested_by,
                utils.formatDate(i.need_date),
                utils.getStatusBadge(i.status),
                `<div class="btn-group">
                    <button class="btn btn-secondary btn-sm view-btn" data-id="${i.id}">View</button>
                    ${i.status === 'APPROVED' ? `<button class="btn btn-primary btn-sm convert-btn" data-id="${i.id}">Convert to PO</button>` : ''}
                </div>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Material Requisitions (Indents)</h2>
                    <button class="btn btn-primary" id="add-indent-btn">
                        <i data-lucide="file-plus"></i> Create Indent
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No indents found.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();

            // Event Listeners
            document.getElementById('add-indent-btn').onclick = () => IndentsView.showCreateModal();
            
            document.querySelectorAll('.view-btn').forEach(btn => {
                btn.onclick = (e) => IndentsView.showDetails(e.currentTarget.getAttribute('data-id'));
            });

            document.querySelectorAll('.convert-btn').forEach(btn => {
                btn.onclick = (e) => IndentsView.showConvertModal(e.currentTarget.getAttribute('data-id'));
            });
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },

    showCreateModal: async () => {
        // Fetch materials for selection
        let materials = [];
        try {
            const res = await api.getMaterials();
            materials = res.items;
        } catch (e) {}

        const formHtml = `
            <form id="create-indent-form">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Indent Number</label>
                        <input type="text" name="indent_number" required placeholder="IND-2026-001">
                    </div>
                    <div class="form-group">
                        <label>Need Date</label>
                        <input type="date" name="need_date" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Requested By (Person ID)</label>
                    <input type="text" name="requested_by" required placeholder="UUID">
                </div>

                <div class="form-group">
                    <label>BOQ Reference</label>
                    <input type="text" name="boq_reference" placeholder="e.g. BOQ-CIV-01">
                </div>

                <div style="margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
                    <h4>Items</h4>
                    <div id="indent-items-container">
                        <div class="indent-item-row" style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <select name="material_id" required style="flex: 2;">
                                <option value="">Select Material...</option>
                                ${materials.map(m => `<option value="${m.id}">${m.name} (${m.unit})</option>`).join('')}
                            </select>
                            <input type="number" name="quantity" placeholder="Qty" required style="flex: 1;">
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>Remarks</label>
                    <textarea name="remarks" rows="2"></textarea>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancel-modal-btn">Cancel</button>
                    <button type="submit" class="btn btn-primary">Submit Indent</button>
                </div>
            </form>
        `;
        UI.openModal('Create Material Requisition', formHtml);
        
        document.getElementById('cancel-modal-btn').onclick = () => UI.closeModal();
        
        document.getElementById('create-indent-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const rawData = Object.fromEntries(formData.entries());
            
            const data = {
                indent_number: rawData.indent_number,
                requested_by: rawData.requested_by,
                need_date: rawData.need_date,
                boq_reference: rawData.boq_reference,
                remarks: rawData.remarks,
                items: [
                    {
                        material_id: rawData.material_id,
                        quantity: parseFloat(rawData.quantity),
                        unit: 'MT' // Simplified for demo
                    }
                ]
            };
            
            try {
                await api.createIndent(data);
                UI.showToast('Indent created successfully!', 'success');
                UI.closeModal();
                IndentsView.render();
            } catch (err) {
                UI.showToast('Failed to create indent: ' + err.message, 'error');
            }
        };
    },

    showDetails: async (indentId) => {
        utils.showLoader();
        try {
            const indent = await api.getIndent(indentId);
            const html = `
                <div class="indent-details">
                    <div class="form-grid">
                        <div><strong>Number:</strong> ${indent.indent_number}</div>
                        <div><strong>Status:</strong> ${utils.getStatusBadge(indent.status)}</div>
                        <div><strong>Need Date:</strong> ${utils.formatDate(indent.need_date)}</div>
                        <div><strong>Requested By:</strong> ${indent.requested_by}</div>
                    </div>
                    <h4 style="margin-top:1.5rem;">Items</h4>
                    ${utils.renderTable(['Material ID', 'Quantity', 'Unit'], indent.items.map(i => [i.material_id, i.quantity, i.unit]))}
                    <div style="margin-top:1.5rem;">
                        <strong>Remarks:</strong><p>${indent.remarks || 'None'}</p>
                    </div>
                </div>
            `;
            UI.openModal(`Indent Details: ${indent.indent_number}`, html);
        } catch (err) {
            UI.showToast('Error loading indent: ' + err.message, 'error');
        }
    },

    showConvertModal: async (indentId) => {
        // Fetch vendors for selection
        let vendors = [];
        try {
            const res = await api.getVendors();
            vendors = res.items;
        } catch (e) {}

        const formHtml = `
            <form id="convert-to-po-form">
                <div class="form-group">
                    <label>Select Vendor</label>
                    <select name="vendor_id" required>
                        <option value="">Choose Vendor...</option>
                        ${vendors.map(v => `<option value="${v.id}">${v.name} (${v.code})</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>PO Number</label>
                    <input type="text" name="po_number" required placeholder="PO-2026-XXXX">
                </div>
                <div class="alert alert-info">
                    <i data-lucide="info"></i>
                    <span>This will create a DRAFT Purchase Order using the items from the indent. Unit prices will be initialized to 0.</span>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancel-modal-btn">Cancel</button>
                    <button type="submit" class="btn btn-primary">Generate Purchase Order</button>
                </div>
            </form>
        `;
        UI.openModal('Convert Indent to PO', formHtml);
        if (window.lucide) window.lucide.createIcons();

        document.getElementById('cancel-modal-btn').onclick = () => UI.closeModal();

        document.getElementById('convert-to-po-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());

            try {
                await api.convertIndentToPO(indentId, data.vendor_id, data.po_number);
                UI.showToast('Purchase Order generated successfully!', 'success');
                UI.closeModal();
                IndentsView.render();
            } catch (err) {
                UI.showToast('Failed to generate PO: ' + err.message, 'error');
            }
        };
    }
};
