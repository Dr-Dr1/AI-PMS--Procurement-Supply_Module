const App = {
    init: () => {
        // Initialize Lucide icons on start
        lucide.createIcons();

        // Handle navigation
        window.addEventListener('hashchange', App.handleRoute);
        
        // Initial route
        App.handleRoute();

        console.log('AI-PMS Frontend Initialized');
    },

    handleRoute: () => {
        const hash = window.location.hash || '#dashboard';
        const page = hash.substring(1);
        
        // Update active link in sidebar
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === hash) {
                link.classList.add('active');
            }
        });

        // Update page title
        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            pageTitle.innerText = page.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        }

        // Route to correct view
        switch(page) {
            case 'dashboard':
                DashboardView.render();
                break;
            case 'vendors':
                VendorsView.render();
                break;
            case 'materials':
                MaterialsView.render();
                break;
            case 'purchase-orders':
                PurchaseOrdersView.render();
                break;
            case 'deliveries':
                DeliveriesView.render();
                break;
            case 'fat-tests':
                FATTestsView.render();
                break;
            default:
                DashboardView.render();
        }
    }
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', App.init);
