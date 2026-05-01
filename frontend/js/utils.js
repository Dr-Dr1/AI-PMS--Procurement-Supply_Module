export const utils = {
    formatCurrency: (amount, currency = 'INR') => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency,
        }).format(amount || 0);
    },

    formatDate: (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
    },

    getStatusBadge: (status) => {
        const s = status ? status.toLowerCase() : 'unknown';
        let className = 'badge-info';
        
        if (['active', 'approved', 'delivered', 'passed', 'completed'].includes(s)) className = 'badge-success';
        if (['pending', 'draft', 'scheduled', 'in_transit'].includes(s)) className = 'badge-warning';
        if (['rejected', 'failed', 'cancelled', 'inactive'].includes(s)) className = 'badge-danger';
        
        return `<span class="badge ${className}">${status}</span>`;
    },

    showLoader: (containerId = 'content-area') => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="loader-container">
                    <div class="loader"></div>
                </div>
            `;
        }
    },

    renderTable: (headers, rows, emptyMessage = 'No records found') => {
        if (!rows || rows.length === 0) {
            return `
                <div class="glass-panel" style="text-align: center; padding: 4rem;">
                    <div style="margin-bottom: 1rem; opacity: 0.5;">
                        <i data-lucide="folder-open" style="width: 48px; height: 48px;"></i>
                    </div>
                    <p style="color: var(--text-muted); font-size: 1.1rem;">${emptyMessage}</p>
                </div>
            `;
        }

        return `
            <div class="glass-panel" style="padding: 0; overflow: hidden;">
                <div class="data-table-container">
                    <table>
                        <thead>
                            <tr>
                                ${headers.map(h => `<th>${h}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map((row, idx) => `
                                <tr style="animation: slideIn 0.3s ease-out ${idx * 0.05}s both;">
                                    ${row.map(cell => `<td>${cell}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
};

export const UI = {
    openModal: (title, bodyHtml) => {
        const overlay = document.getElementById('modal-overlay');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');
        
        if (titleEl && bodyEl && overlay) {
            titleEl.innerText = title;
            bodyEl.innerHTML = bodyHtml;
            overlay.classList.add('active');
            if (window.lucide) window.lucide.createIcons();
        }
    },

    closeModal: () => {
        const overlay = document.getElementById('modal-overlay');
        if (overlay) overlay.classList.remove('active');
    },

    showToast: (message, type = 'info') => {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'info';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'alert-circle';
        if (type === 'warning') icon = 'alert-triangle';

        toast.innerHTML = `
            <i data-lucide="${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        if (window.lucide) window.lucide.createIcons();

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};
