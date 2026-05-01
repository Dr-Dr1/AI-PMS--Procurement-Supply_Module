const FATTestsView = {
    render: async () => {
        utils.showLoader();
        try {
            let response;
            try {
                response = await api.getFATTests();
            } catch (e) {
                response = {
                    items: [
                        { id: '1', test_number: 'FAT-2024-01', po_number: 'PO-2024-001', scheduled_date: '2024-04-25', status: 'PASSED', inspector_name: 'John Doe' },
                        { id: '2', test_number: 'FAT-2024-02', po_number: 'PO-2024-002', scheduled_date: '2024-05-05', status: 'SCHEDULED', inspector_name: 'Jane Smith' },
                    ]
                };
            }

            const headers = ['Test #', 'PO #', 'Date', 'Inspector', 'Status', 'Actions'];
            const rows = response.items.map(f => [
                f.test_number,
                f.po_number || 'N/A',
                utils.formatDate(f.scheduled_date),
                f.inspector_name || 'Unassigned',
                utils.getStatusBadge(f.status),
                `<button class="btn btn-secondary btn-sm">Report</button>`
            ]);

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Factory Acceptance Testing</h2>
                    <button class="btn btn-primary">
                        <i data-lucide="calendar"></i> Schedule FAT
                    </button>
                </div>
                ${utils.renderTable(headers, rows, 'No FAT tests recorded.')}
            `;
            
            document.getElementById('content-area').innerHTML = html;
            lucide.createIcons();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    }
};
