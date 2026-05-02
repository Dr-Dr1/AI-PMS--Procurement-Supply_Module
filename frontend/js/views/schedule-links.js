import { api } from '../api.js';
import { utils, UI } from '../utils.js';

export const ScheduleLinksView = {
    render: async () => {
        utils.showLoader();
        try {
            // In a real app, we'd fetch activities and their links. 
            // For now, let's show a list of schedule linkages.
            const response = { items: [] }; // Placeholder for list of links

            const headers = ['Activity', 'Material', 'Need Date', 'PO Delivery', 'Status'];
            const rows = [
                ['Station A - Concreting', 'Concrete (M40)', '2026-06-01', '2026-05-25', '<span class="badge badge-success">On Track</span>'],
                ['Pier 45 - Rebar Fixing', 'TMT Steel 16mm', '2026-05-15', '2026-05-20', '<span class="badge badge-error">Late (5 days gap)</span>'],
                ['Tunnel Boring Segment 1', 'Precast Segment', '2026-07-10', '2026-07-05', '<span class="badge badge-success">On Track</span>'],
            ];

            const html = `
                <div class="panel-header" style="margin-bottom: var(--space-md);">
                    <h2 class="panel-title">Schedule - Procurement Linkage (Expert A09)</h2>
                </div>
                <div class="alert alert-info" style="margin-bottom: var(--space-md);">
                    <i data-lucide="info"></i>
                    <span>This view bridges <strong>Activity.planned_start</strong> (Schedule) and <strong>PO.expected_delivery</strong> (Procurement). A gap occurs if delivery is later than the activity start date.</span>
                </div>
                ${utils.renderTable(headers, rows, 'No schedule links found.')}
                
                <div style="margin-top: 2rem;">
                    <h3>Gap Analysis</h3>
                    <div class="card-grid">
                        <div class="stat-card">
                            <span class="stat-label">Critical Gaps</span>
                            <span class="stat-value" style="color: var(--error-color);">1</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">On Track</span>
                            <span class="stat-value" style="color: var(--success-color);">2</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-label">Total Value at Risk</span>
                            <span class="stat-value">₹ 4.5 Cr</span>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();

        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    }
};
