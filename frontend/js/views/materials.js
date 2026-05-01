import { api } from '../api.js';
import { utils, UI } from '../utils.js';

export const MaterialsView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getMaterials();
            } catch (e) {
                response = { items: [] };
            }

            const headers = ['Code', 'Name', 'Category', 'Unit', 'Status', 'Actions'];
            const rows = response.items.map(m => [
                m.code,
                m.name,
                m.category,
                m.unit,
                utils.getStatusBadge(m.is_active ? 'ACTIVE' : 'INACTIVE'),
                `<button class="btn btn-secondary btn-sm">Edit</button>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Material Catalogue</h2>
                    <button class="btn btn-primary" id="add-material-btn">
                        <i data-lucide="package-plus"></i> Add Material
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'Catalogue is empty.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();

            document.getElementById('add-material-btn').onclick = () => MaterialsView.showCreateModal();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    },

    showCreateModal: () => {
        const formHtml = `
            <form id="create-material-form">
                <div class="form-group">
                    <label>Material Name</label>
                    <input type="text" name="name" required placeholder="e.g. Steel Beam I-Section">
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Code</label>
                        <input type="text" name="code" required placeholder="MAT-101">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <input type="text" name="category" placeholder="e.g. Structural">
                    </div>
                </div>
                <div class="form-group">
                    <label>Unit of Measure</label>
                    <input type="text" name="unit" required placeholder="e.g. Ton, Bag, Meter">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="cancel-modal-btn">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Material</button>
                </div>
            </form>
        `;
        UI.openModal('Add Material to Catalogue', formHtml);
        
        document.getElementById('cancel-modal-btn').onclick = () => UI.closeModal();
        
        document.getElementById('create-material-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                await api.createMaterial(data);
                UI.showToast('Material added to catalogue', 'success');
                UI.closeModal();
                MaterialsView.render();
            } catch (err) {
                UI.showToast('Failed to save material: ' + err.message, 'error');
            }
        };
    }
};
