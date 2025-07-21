// Restaurant Menu Mobile App
class RestaurantApp {
    constructor() {
        this.cart = [];
        this.cartTotal = 0;
        this.searchActive = false;
        this.sidebarOpen = false;
        
        this.init();
    }
    
    init() {
        // Wait for device ready
        document.addEventListener('deviceready', this.onDeviceReady.bind(this), false);
        
        // Initialize app if not running in Cordova (web browser)
        if (!window.cordova) {
            // Wait for DOM to be ready in web browsers
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeApp());
            } else {
                this.initializeApp();
            }
        }
    }
    
    onDeviceReady() {
        console.log('Device is ready');
        this.initializeApp();
        
        // Handle Android back button
        document.addEventListener("backbutton", this.onBackButton.bind(this), false);
        
        // Handle pause/resume
        document.addEventListener("pause", this.onPause.bind(this), false);
        document.addEventListener("resume", this.onResume.bind(this), false);
    }
    
    initializeApp() {
        this.setupEventListeners();
        this.setupTouchEvents();
        this.loadCategories();
        this.updateCartDisplay();
    }
    
    setupEventListeners() {
        // Menu toggle
        const menuToggle = document.getElementById('menuToggle');
        const closeSidebar = document.getElementById('closeSidebar');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        
        menuToggle?.addEventListener('click', () => this.toggleSidebar());
        closeSidebar?.addEventListener('click', () => this.closeSidebar());
        sidebarOverlay?.addEventListener('click', () => this.closeSidebar());
        
        // Search functionality
        const searchBtn = document.getElementById('searchBtn');
        const searchClose = document.getElementById('searchClose');
        const searchInput = document.getElementById('searchInput');
        
        searchBtn?.addEventListener('click', () => this.toggleSearch());
        searchClose?.addEventListener('click', () => this.closeSearch());
        searchInput?.addEventListener('input', (e) => this.handleSearch(e.target.value));
        
        // Category selection
        const categoryItems = document.querySelectorAll('.category-item');
        categoryItems.forEach(item => {
            item.addEventListener('click', () => this.selectCategory(item));
        });
        
        // Subcategory selection
        const subcategoryItems = document.querySelectorAll('.subcategory-item');
        subcategoryItems.forEach(item => {
            item.addEventListener('click', () => this.selectSubcategory(item));
        });
        
        // Add to cart buttons
        const addToCartBtns = document.querySelectorAll('.add-to-cart');
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.addToCart(btn.closest('.menu-item'));
            });
        });
        
        // Bottom navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => this.handleNavigation(item));
        });
        
        // Cart floating button
        const cartFloating = document.getElementById('cartFloating');
        cartFloating?.addEventListener('click', () => this.showCart());
    }
    
    setupTouchEvents() {
        // Add touch feedback to interactive elements
        const touchElements = document.querySelectorAll('.menu-item, .category-item, .subcategory-item, .nav-item, .btn');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.style.transform = 'scale(0.95)';
            });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.style.transform = '';
                }, 150);
            });
            
            element.addEventListener('touchcancel', () => {
                element.style.transform = '';
            });
        });
        
        // Swipe gestures for sidebar
        let startX, startY, distX, distY;
        
        document.addEventListener('touchstart', (e) => {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const touch = e.touches[0];
            distX = touch.clientX - startX;
            distY = touch.clientY - startY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            // Swipe right to open sidebar (from left edge)
            if (startX < 50 && distX > 100 && Math.abs(distY) < 100) {
                this.openSidebar();
            }
            
            // Swipe left to close sidebar
            if (this.sidebarOpen && distX < -100 && Math.abs(distY) < 100) {
                this.closeSidebar();
            }
            
            startX = startY = distX = distY = null;
        });
    }
    
    toggleSidebar() {
        if (this.sidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        const sidebar = document.getElementById('categoriesSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar?.classList.add('open');
        overlay?.classList.add('active');
        this.sidebarOpen = true;
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }
    
    closeSidebar() {
        const sidebar = document.getElementById('categoriesSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        sidebar?.classList.remove('open');
        overlay?.classList.remove('active');
        this.sidebarOpen = false;
        
        // Restore body scroll
        document.body.style.overflow = '';
    }
    
    toggleSearch() {
        const searchContainer = document.getElementById('searchContainer');
        const searchInput = document.getElementById('searchInput');
        
        if (this.searchActive) {
            this.closeSearch();
        } else {
            searchContainer?.classList.add('active');
            searchInput?.focus();
            this.searchActive = true;
        }
    }
    
    closeSearch() {
        const searchContainer = document.getElementById('searchContainer');
        const searchInput = document.getElementById('searchInput');
        
        searchContainer?.classList.remove('active');
        searchInput.value = '';
        this.searchActive = false;
        this.showAllMenuItems();
    }
    
    handleSearch(query) {
        const menuItems = document.querySelectorAll('.menu-item');
        const searchQuery = query.toLowerCase().trim();
        
        if (searchQuery === '') {
            this.showAllMenuItems();
            return;
        }
        
        menuItems.forEach(item => {
            const itemName = item.dataset.name?.toLowerCase() || '';
            const itemText = item.textContent.toLowerCase();
            
            if (itemName.includes(searchQuery) || itemText.includes(searchQuery)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    showAllMenuItems() {
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.style.display = 'block';
        });
    }
    
    selectCategory(categoryItem) {
        // Remove active class from all categories
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected category
        categoryItem.classList.add('active');
        
        // Close sidebar on mobile
        this.closeSidebar();
        
        // Filter menu items based on category
        const category = categoryItem.dataset.category;
        this.filterMenuByCategory(category);
        
        // Haptic feedback if available
        this.vibrate(50);
    }
    
    selectSubcategory(subcategoryItem) {
        // Remove active class from all subcategories
        document.querySelectorAll('.subcategory-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected subcategory
        subcategoryItem.classList.add('active');
        
        // Scroll subcategory into view
        subcategoryItem.scrollIntoView({
            behavior: 'smooth',
            inline: 'center',
            block: 'nearest'
        });
        
        // Haptic feedback
        this.vibrate(30);
    }
    
    filterMenuByCategory(category) {
        // This would filter menu items based on category
        // For now, we'll just show all items
        this.showAllMenuItems();
        
        // Add loading effect
        const menuGrid = document.getElementById('menuGrid');
        menuGrid?.classList.add('loading');
        
        setTimeout(() => {
            menuGrid?.classList.remove('loading');
        }, 500);
    }
    
    addToCart(menuItem) {
        const name = menuItem.dataset.name;
        const price = parseFloat(menuItem.dataset.price);
        
        // Find existing item in cart
        const existingItem = this.cart.find(item => item.name === name);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                name: name,
                price: price,
                quantity: 1
            });
        }
        
        this.updateCartDisplay();
        this.showCartAnimation(menuItem);
        this.vibrate(100);
    }
    
    updateCartDisplay() {
        const cartCount = document.getElementById('cartCount');
        const cartTotal = document.getElementById('cartTotal');
        const cartFloating = document.getElementById('cartFloating');
        
        // Calculate totals
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        this.cartTotal = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        // Update displays
        if (cartCount) cartCount.textContent = totalItems;
        if (cartTotal) cartTotal.textContent = `${this.cartTotal.toFixed(2)} €`;
        
        // Show/hide floating cart button
        if (cartFloating) {
            if (totalItems > 0) {
                cartFloating.classList.add('visible');
            } else {
                cartFloating.classList.remove('visible');
            }
        }
    }
    
    showCartAnimation(menuItem) {
        const rect = menuItem.getBoundingClientRect();
        const cartBtn = document.querySelector('.nav-item:nth-child(3)');
        
        if (!cartBtn) return;
        
        const cartRect = cartBtn.getBoundingClientRect();
        
        // Create animated element
        const animatedElement = document.createElement('div');
        animatedElement.innerHTML = '🛒';
        animatedElement.style.cssText = `
            position: fixed;
            top: ${rect.top + rect.height/2}px;
            left: ${rect.left + rect.width/2}px;
            font-size: 2rem;
            z-index: 10000;
            pointer-events: none;
            transition: all 0.6s ease;
            transform: scale(1);
        `;
        
        document.body.appendChild(animatedElement);
        
        // Animate to cart
        requestAnimationFrame(() => {
            animatedElement.style.top = `${cartRect.top + cartRect.height/2}px`;
            animatedElement.style.left = `${cartRect.left + cartRect.width/2}px`;
            animatedElement.style.transform = 'scale(0.5)';
            animatedElement.style.opacity = '0';
        });
        
        // Remove element after animation
        setTimeout(() => {
            document.body.removeChild(animatedElement);
        }, 600);
    }
    
    handleNavigation(navItem) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected nav item
        navItem.classList.add('active');
        
        // Handle navigation logic
        const navLabel = navItem.querySelector('.nav-label')?.textContent;
        
        switch (navLabel) {
            case 'Accueil':
                this.showHome();
                break;
            case 'Menu':
                this.showMenu();
                break;
            case 'Panier':
                this.showCart();
                break;
            case 'Profil':
                this.showProfile();
                break;
        }
        
        this.vibrate(30);
    }
    
    showHome() {
        console.log('Navigating to Home');
    }
    
    showMenu() {
        console.log('Navigating to Menu');
    }
    
    showCart() {
        console.log('Showing cart with items:', this.cart);
        
        // Create simple cart modal (for demo)
        const cartModal = this.createCartModal();
        document.body.appendChild(cartModal);
    }
    
    createCartModal() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            border-radius: 15px;
            padding: 20px;
            max-width: 400px;
            width: 100%;
            max-height: 80vh;
            overflow-y: auto;
        `;
        
        let cartHTML = '<h3>🛒 Votre Panier</h3>';
        
        if (this.cart.length === 0) {
            cartHTML += '<p>Votre panier est vide</p>';
        } else {
            this.cart.forEach(item => {
                cartHTML += `
                    <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee;">
                        <div>
                            <strong>${item.name}</strong><br>
                            <small>Quantité: ${item.quantity}</small>
                        </div>
                        <div>${(item.price * item.quantity).toFixed(2)} €</div>
                    </div>
                `;
            });
            cartHTML += `<div style="margin-top: 15px; font-size: 1.2rem; font-weight: bold; text-align: center;">Total: ${this.cartTotal.toFixed(2)} €</div>`;
        }
        
        cartHTML += '<button onclick="this.closest(\'div[style*=\"fixed\"]\').remove()" style="background: #ff6b6b; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin-top: 15px; width: 100%; font-size: 1rem;">Fermer</button>';
        
        content.innerHTML = cartHTML;
        modal.appendChild(content);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }
    
    showProfile() {
        console.log('Navigating to Profile');
    }
    
    loadCategories() {
        // This would load categories from API
        // For now, we'll use static data
        console.log('Categories loaded');
    }
    
    onBackButton() {
        if (this.searchActive) {
            this.closeSearch();
        } else if (this.sidebarOpen) {
            this.closeSidebar();
        } else {
            // Ask user if they want to exit (Cordova only)
            if (navigator.notification && navigator.app) {
                navigator.notification.confirm(
                    'Voulez-vous quitter l\'application?',
                    (buttonIndex) => {
                        if (buttonIndex === 1) {
                            navigator.app.exitApp();
                        }
                    },
                    'Quitter',
                    ['Oui', 'Non']
                );
            } else {
                // In web browser, just close search/sidebar or do nothing
                console.log('Back button pressed in web browser');
            }
        }
    }
    
    onPause() {
        console.log('App paused');
    }
    
    onResume() {
        console.log('App resumed');
    }
    
    vibrate(duration = 100) {
        // Vibration works on mobile devices and some modern browsers
        if (navigator.vibrate && 'vibrate' in navigator) {
            navigator.vibrate(duration);
        }
    }
    
    showNotification(message, title = 'Restaurant Menu') {
        if (navigator.notification) {
            navigator.notification.alert(message, null, title);
        } else {
            alert(message);
        }
    }
}

// Initialize app
const app = new RestaurantApp();

// Prevent zoom on double tap (iOS Safari)
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Prevent context menu on long press
document.addEventListener('contextmenu', (event) => {
    event.preventDefault();
});

// Service worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js')
        .then(registration => console.log('SW registered'))
        .catch(error => console.log('SW registration failed'));
}