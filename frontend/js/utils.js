const utils = {
    formatCurrency: (amount, currency = 'INR') => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency,
        }).format(amount);
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

    showLoader: () => {
        document.getElementById('content-area').innerHTML = `
            <div class="loader-container">
                <div class="loader"></div>
            </div>
        `;
    },

    renderTable: (headers, rows, emptyMessage = 'No records found') => {
        if (!rows || rows.length === 0) {
            return `<div class="glass-panel" style="text-align: center; padding: 3rem;">
                <p style="color: var(--text-muted);">${emptyMessage}</p>
            </div>`;
        }

        return `
            <div class="glass-panel">
                <div class="data-table-container">
                    <table>
                        <thead>
                            <tr>
                                ${headers.map(h => `<th>${h}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map(row => `
                                <tr>
                                    ${row.map(cell => `<td>${cell}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    openModal: (title, bodyHtml) => {
        const overlay = document.getElementById('modal-overlay');
        const titleEl = document.getElementById('modal-title');
        const bodyEl = document.getElementById('modal-body');
        
        titleEl.innerText = title;
        bodyEl.innerHTML = bodyHtml;
        overlay.classList.add('active');
        lucide.createIcons();
    },

    closeModal: () => {
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.remove('active');
    }
};

// Global UI shorthand
const UI = {
    openModal: utils.openModal,
    closeModal: utils.closeModal
};
