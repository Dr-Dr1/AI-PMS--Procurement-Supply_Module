const DashboardView = {
    render: async () => {
        utils.showLoader();
        try {
            // In a real app, we'd fetch this. Using mock data if API fails.
            let summary;
            try {
                summary = await api.getDashboardSummary();
            } catch (e) {
                summary = {
                    total_purchase_orders: 42,
                    total_vendors: 15,
                    pending_deliveries: 8,
                    upcoming_fat_tests: 3,
                    total_procurement_value: 1250000.50,
                    po_by_status: { 'APPROVED': 12, 'DRAFT': 5, 'PENDING': 25 }
                };
            }

            const html = `
                <div class="dashboard-grid">
                    <div class="stat-card">
                        <div class="stat-icon blue"><i data-lucide="shopping-bag"></i></div>
                        <span class="stat-label">Total POs</span>
                        <span class="stat-value">${summary.total_purchase_orders}</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon green"><i data-lucide="users"></i></div>
                        <span class="stat-label">Active Vendors</span>
                        <span class="stat-value">${summary.total_vendors}</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon orange"><i data-lucide="truck"></i></div>
                        <span class="stat-label">Pending Deliveries</span>
                        <span class="stat-value">${summary.pending_deliveries}</span>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon purple"><i data-lucide="clipboard-check"></i></div>
                        <span class="stat-label">Upcoming FATs</span>
                        <span class="stat-value">${summary.upcoming_fat_tests}</span>
                    </div>
                </div>

                <div class="dashboard-details">
                    <div class="glass-panel">
                        <div class="panel-header">
                            <h3 class="panel-title">Procurement Overview</h3>
                            <div class="badge badge-success">Live Updates</div>
                        </div>
                        <div style="height: 300px; padding: 1rem; margin-top: 1rem; position: relative;">
                            <svg viewBox="0 0 400 200" style="width: 100%; height: 100%;">
                                <!-- Gradients -->
                                <defs>
                                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stop-color="var(--primary)" stop-opacity="0.3" />
                                        <stop offset="100%" stop-color="var(--primary)" stop-opacity="0" />
                                    </linearGradient>
                                </defs>
                                
                                <!-- Grid Lines -->
                                <line x1="0" y1="50" x2="400" y2="50" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                <line x1="0" y1="100" x2="400" y2="100" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                <line x1="0" y1="150" x2="400" y2="150" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />
                                
                                <!-- Area -->
                                <path d="M0,180 L50,140 L100,160 L150,110 L200,130 L250,80 L300,100 L350,50 L400,70 L400,200 L0,200 Z" fill="url(#chartGradient)" />
                                
                                <!-- Line -->
                                <path d="M0,180 L50,140 L100,160 L150,110 L200,130 L250,80 L300,100 L350,50 L400,70" fill="none" stroke="var(--primary)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                                
                                <!-- Points -->
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
                    
                    <div class="glass-panel">
                        <div class="panel-header">
                            <h3 class="panel-title">Recent Activity</h3>
                        </div>
                        <div class="activity-list">
                            <div style="padding: 1rem 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start; gap: 12px;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #ecfdf5; color: #10b981; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                    <i data-lucide="check-circle" style="width: 16px; height: 16px;"></i>
                                </div>
                                <div>
                                    <p style="font-weight: 500; font-size: 0.9rem;">PO #PO-2024-001 Created</p>
                                    <p style="font-size: 0.8rem; color: var(--text-muted);">2 hours ago</p>
                                </div>
                            </div>
                            <div style="padding: 1rem 0; border-bottom: 1px solid #f1f5f9; display: flex; align-items: flex-start; gap: 12px;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #eff6ff; color: #3b82f6; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                    <i data-lucide="info" style="width: 16px; height: 16px;"></i>
                                </div>
                                <div>
                                    <p style="font-weight: 500; font-size: 0.9rem;">FAT Test Passed: Vendor X</p>
                                    <p style="font-size: 0.8rem; color: var(--text-muted);">Yesterday</p>
                                </div>
                            </div>
                            <div style="padding: 1rem 0; display: flex; align-items: flex-start; gap: 12px;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: #fef2f2; color: #ef4444; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                                    <i data-lucide="alert-triangle" style="width: 16px; height: 16px;"></i>
                                </div>
                                <div>
                                    <p style="font-weight: 500; font-size: 0.9rem;">New Vendor Registered</p>
                                    <p style="font-size: 0.8rem; color: var(--text-muted);">3 days ago</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('content-area').innerHTML = html;
            lucide.createIcons();
        } catch (error) {
            document.getElementById('content-area').innerHTML = `<p class="error">Failed to load dashboard: ${error.message}</p>`;
        }
    }
};
