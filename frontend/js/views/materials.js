const MaterialsView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getMaterials();
            } catch (e) {
                response = {
                    items: [
                        { id: '1', name: 'Cement Grade A', code: 'MAT-001', category: 'Construction', unit: 'Bag', is_active: true },
                        { id: '2', name: 'Steel Rods 12mm', code: 'MAT-002', category: 'Metal', unit: 'Ton', is_active: true },
                    ]
                };
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
                    <button class="btn btn-primary" onclick="MaterialsView.showCreateModal()">
                         <i data-lucide="package-plus"></i> Add Material
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'Catalogue is empty.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            lucide.createIcons();
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
                <div class="form-grid">
                    <div class="form-group">
                        <label>Unit of Measure</label>
                        <input type="text" name="unit" required placeholder="e.g. Ton, Bag, Meter">
                    </div>
                    <div class="form-group">
                        <label>HSN Code</label>
                        <input type="text" name="hsn_code" placeholder="Tax Category">
                    </div>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="2"></textarea>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Material</button>
                </div>
            </form>
        `;
        UI.openModal('Add Material to Catalogue', formHtml);
        
        document.getElementById('create-material-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            try {
                await api.createMaterial(data);
                UI.closeModal();
                MaterialsView.render();
            } catch (err) {
                alert('Failed to save material: ' + err.message);
            }
        };
    }
};
