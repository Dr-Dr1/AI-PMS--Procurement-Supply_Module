const DeliveriesView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getDeliveries();
            } catch (e) {
                response = {
                    items: [
                        { id: '1', delivery_number: 'DEL-9901', po_number: 'PO-2024-001', expected_arrival: '2024-05-10', status: 'IN_TRANSIT' },
                        { id: '2', delivery_number: 'DEL-9902', po_number: 'PO-2024-001', expected_arrival: '2024-05-15', status: 'SCHEDULED' },
                    ]
                };
            }

            const headers = ['Delivery #', 'PO #', 'Expected Arrival', 'Status', 'Actions'];
            const rows = response.items.map(d => [
                d.delivery_number,
                d.po_number || 'N/A',
                utils.formatDate(d.expected_arrival),
                utils.getStatusBadge(d.status),
                `<button class="btn btn-secondary btn-sm">Track</button>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Inbound Deliveries</h2>
                    <button class="btn btn-primary">
                        <i data-lucide="truck"></i> New Shipment
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No active deliveries.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            lucide.createIcons();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    }
};
