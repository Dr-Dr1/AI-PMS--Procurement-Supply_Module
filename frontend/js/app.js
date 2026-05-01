import { UI } from './utils.js';
import { DashboardView } from './views/dashboard.js';
import { VendorsView } from './views/vendors.js';
import { MaterialsView } from './views/materials.js';
import { PurchaseOrdersView } from './views/purchase-orders.js';
import { DeliveriesView } from './views/deliveries.js';
import { FATTestsView } from './views/fat-tests.js';

const App = {
    views: {
        dashboard: DashboardView,
        vendors: VendorsView,
        materials: MaterialsView,
        'purchase-orders': PurchaseOrdersView,
        deliveries: DeliveriesView,
        'fat-tests': FATTestsView
    },

    init: () => {
        // Initialize Lucide icons on start
        if (window.lucide) window.lucide.createIcons();

        // Handle navigation
        window.addEventListener('hashchange', App.handleRoute);
        
        // Listen for internal links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const target = e.currentTarget.getAttribute('data-link');
                if (target) {
                    window.location.hash = target;
                }
            });
        });

        // Close modal setup
        const closeBtn = document.getElementById('close-modal-btn');
        if (closeBtn) closeBtn.onclick = () => UI.closeModal();

        // Initial route
        App.handleRoute();

        console.log('AI-PMS Frontend Module System Initialized');
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
        const view = App.views[page] || DashboardView;
        view.render();
    }
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', App.init);
export default App;
