import { api } from '../api.js';
import { utils } from '../utils.js';

export const DashboardView = {
    render: async () => {
        utils.showLoader();
        try {
            let summary;
            try {
                summary = await api.getDashboardSummary();
            } catch (e) {
                // Mock fallback
                summary = {
                    total_purchase_orders: 42,
                    total_vendors: 15,
                    pending_deliveries: 8,
                    upcoming_fat_tests: 3,
                    total_procurement_value: 1250000.50,
                };
            }

            const html = `
                <div class="dashboard-grid">
                    ${['Total POs', 'Active Vendors', 'Pending Deliveries', 'Upcoming FATs'].map((label, idx) => {
                        const values = [summary.total_purchase_orders, summary.total_vendors, summary.pending_deliveries, summary.upcoming_fat_tests];
                        const icons = ['shopping-bag', 'users', 'truck', 'clipboard-check'];
                        const colors = ['blue', 'green', 'orange', 'purple'];
                        return `
                            <div class="stat-card" style="animation: slideIn 0.4s ease-out ${idx * 0.1}s both;">
                                <div class="stat-icon ${colors[idx]}"><i data-lucide="${icons[idx]}"></i></div>
                                <span class="stat-label">${label}</span>
                                <span class="stat-value">${values[idx]}</span>
                            </div>
                        `;
                    }).join('')}
                </div>

                <div class="dashboard-details">
                    <div class="glass-panel" style="animation: slideIn 0.5s ease-out 0.2s both;">
                        <div class="panel-header">
                            <h3 class="panel-title">Procurement Overview</h3>
                            <div class="badge badge-success">Live Updates</div>
                        </div>
                        <div style="height: 300px; padding: 1rem; margin-top: 1rem; position: relative;">
                            <svg viewBox="0 0 400 200" style="width: 100%; height: 100%;">
                                <defs>
                                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.3" />
                                        <stop offset="100%" stop-color="var(--primary)" stop-opacity="0" />
                                    </linearGradient>
                                </defs>
                                <line x1="0" y1="50" x2="400" y2="50" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                <line x1="0" y1="100" x2="400" y2="100" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                <line x1="0" y1="150" x2="400" y2="150" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                <path d="M0,180 L50,140 L100,160 L150,110 L200,130 L250,80 L300,100 L350,50 L400,70 L400,200 L0,200 Z" fill="url(#chartGradient)" />
                                <path d="M0,180 L50,140 L100,160 L150,110 L200,130 L250,80 L300,100 L350,50 L400,70" fill="none" stroke="var(--primary)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                                <circle cx="50" cy="140" r="4" fill="white" stroke="var(--primary)" stroke-width="2" />
                                <circle cx="150" cy="110" r="4" fill="white" stroke="var(--primary)" stroke-width="2" />
                                <circle cx="250" cy="80" r="4" fill="white" stroke="var(--primary)" stroke-width="2" />
                                <circle cx="350" cy="50" r="4" fill="white" stroke="var(--primary)" stroke-width="2" />
                            </svg>
                            <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 0.7rem; color: var(--text-muted);">
                                <span>JAN</span><span>FEB</span><span>MAR</span><span>APR</span><span>MAY</span><span>JUN</span><span>JUL</span><span>AUG</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="glass-panel" style="animation: slideIn 0.5s ease-out 0.3s both;">
                        <div class="panel-header">
                            <h3 class="panel-title">Recent Activity</h3>
                        </div>
                        <div class="activity-list">
                            ${[
                                { icon: 'check-circle', color: '#10b981', bg: '#ecfdf5', title: 'PO #PO-2024-001 Created', time: '2 hours ago' },
                                { icon: 'info', color: '#3b82f6', bg: '#eff6ff', title: 'FAT Test Passed: Vendor X', time: 'Yesterday' },
                                { icon: 'alert-triangle', color: '#ef4444', bg: '#fef2f2', title: 'New Vendor Registered', time: '3 days ago' }
                            ].map(item => `
                                <div style="padding: 1rem 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start; gap: 12px;">
                                    <div style="width: 32px; height: 32px; border-radius: 8px; background: ${item.bg}; color: ${item.color}; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                        <i data-lucide="${item.icon}" style="width: 16px; height: 16px;"></i>
                                    </div>
                                    <div>
                                        <p style="font-weight: 500; font-size: 0.9rem;">${item.title}</p>
                                        <p style="font-size: 0.8rem; color: var(--text-muted);">${item.time}</p>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('content-area').innerHTML = html;
            if (window.lucide) window.lucide.createIcons();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Failed to load dashboard: ${error.message}</p>`;
        }
    }
};
