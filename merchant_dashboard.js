/**
 * Merchant Dashboard JavaScript
 * Handles all dashboard functionality
 */

// Global state
let currentMerchant = null;
let merchantEvents = [];

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    if (currentMerchant) {
        initializeEventListeners();
        loadMerchantData();
    }
});

/**
 * Check if merchant is authenticated
 */
async function checkAuth() {
    const merchantData = localStorage.getItem('merchantData');
    
    // Check if we're in demo mode (URL parameter)
    const urlParams = new URLSearchParams(window.location.search);
    
    if (!merchantData || urlParams.get('demo') === 'true') {
        if (urlParams.get('demo') === 'true') {
            // Demo mode - use sample data
            currentMerchant = {
                id: 1,
                fullName: 'Demo Merchant',
                companyName: 'Demo Event Company',
                email: 'demo@example.com',
                phone: '254712345678',
                userType: 'organizer'
            };
            document.getElementById('merchantName').textContent = `Welcome, ${currentMerchant.fullName} (Demo Mode)`;
            console.log('Running in demo mode');
            return;
        }
        
        // No merchant data - redirect to login
        console.log('No merchant data found. Redirecting to login...');
        window.location.href = 'index.html';
        return;
    }
    
    currentMerchant = JSON.parse(merchantData);
    
    // Verify merchant ID is valid (don't redirect, just use the stored ID)
    console.log('Logged in as merchant ID:', currentMerchant.id);
    
    document.getElementById('merchantName').textContent = `Welcome, ${currentMerchant.fullName || currentMerchant.companyName}`;
}

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Initialize sidebar toggle (hide/unhide sidebar)
    initializeSidebarToggle();

    // Tab navigation
    const sidebarLinks = document.querySelectorAll('.sidebar-menu li');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tab = link.dataset.tab;
            switchTab(tab);
            
            // Close sidebar on mobile after clicking
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
            }
        });
    });

    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.getElementById('sidebar');
    hamburger.addEventListener('click', () => {
        sidebar.classList.toggle('active');
        hamburger.classList.toggle('active');
    });

    // Mobile sidebar toggle button
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });
    };

    // Create event form
    const createEventForm = document.getElementById('createEventForm');
    createEventForm.addEventListener('submit', handleCreateEvent);

    // Edit event form
    const editEventForm = document.getElementById('editEventForm');
    editEventForm.addEventListener('submit', handleEditEvent);

    // Delete confirmation
    document.getElementById('confirmDeleteBtn').addEventListener('click', handleConfirmDelete);
    document.getElementById('cancelDeleteBtn').addEventListener('click', closeDeleteModal);

    // Event filters
    document.getElementById('eventStatusFilter').addEventListener('change', filterEvents);
    document.getElementById('eventSearch').addEventListener('input', filterEvents);

    // Create event button
    document.getElementById('createEventBtn').addEventListener('click', () => {
        switchTab('create-event');
    });

    // Logout
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);

    // Modal close buttons
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

/**
 * Switch between tabs
 */
function switchTab(tabId) {
    // Update sidebar
    document.querySelectorAll('.sidebar-menu li').forEach(li => {
        li.classList.remove('active');
        if (li.dataset.tab === tabId) {
            li.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.dashboard-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('active');
    document.getElementById('hamburger').classList.remove('active');

    // Load tab-specific data
    if (tabId === 'my-events') {
        loadMerchantEvents();
    } else if (tabId === 'overview') {
        loadOverviewStats();
    } else if (tabId === 'settings') {
        loadProfileData();
    }
}

/**
 * Load merchant data
 */
function loadMerchantData() {
    loadOverviewStats();
}

/**
 * Load overview statistics
 */
async function loadOverviewStats() {
    try {
        const response = await fetch(`api_get_merchant_events.py?merchantId=${currentMerchant.id}`);
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            const events = result.data;
            merchantEvents = events;

            // Calculate stats
            const totalEvents = events.length;
            const publishedEvents = events.filter(e => e.status === 'published').length;
            const totalTickets = events.reduce((sum, e) => sum + (e.tickets_sold || 0), 0);
            const totalRevenue = events.reduce((sum, e) => sum + (e.revenue || 0), 0);
            const totalViews = events.reduce((sum, e) => sum + (e.views || 0), 0);

            // Update UI
            document.getElementById('totalEvents').textContent = totalEvents;
            document.getElementById('totalTickets').textContent = totalTickets;
            document.getElementById('totalRevenue').textContent = `KSh ${totalRevenue.toLocaleString()}`;
            document.getElementById('totalViews').textContent = totalViews;

            // Update activity list
            updateActivityList(events);
        } else {
            // No events found for this merchant
            document.getElementById('totalEvents').textContent = '0';
            document.getElementById('totalTickets').textContent = '0';
            document.getElementById('totalRevenue').textContent = 'KSh 0';
            document.getElementById('totalViews').textContent = '0';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Update activity list
 */
function updateActivityList(events) {
    const activityList = document.getElementById('activityList');
    
    if (events.length === 0) {
        activityList.innerHTML = '<p class="no-data">No recent activity</p>';
        return;
    }

    const recentEvents = events.slice(0, 5);
    activityList.innerHTML = recentEvents.map(event => `
        <div class="activity-item">
            <div class="activity-icon">
                <i class="fas fa-calendar-alt"></i>
            </div>
            <div class="activity-details">
                <span class="activity-title">${event.title}</span>
                <span class="activity-date">${formatDate(event.event_date)}</span>
                <span class="activity-status status-${event.status}">${capitalizeFirst(event.status)}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Load merchant events
 */
async function loadMerchantEvents() {
    const container = document.getElementById('merchantEventsList');
    container.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i> Loading events...</div>';

    try {
        const response = await fetch(`api_get_merchant_events.py?merchantId=${currentMerchant.id}`);
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            merchantEvents = result.data;
            renderEventsList(merchantEvents);
        } else {
            // No events found for this merchant
            container.innerHTML = `
                <div class="no-events-message">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Events Found</h3>
                    <p>You haven't created any events yet.</p>
                    <button class="btn btn-primary" onclick="switchTab('create-event')">
                        <i class="fas fa-plus"></i> Create Your First Event
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading events:', error);
        container.innerHTML = '<p class="error-message">Failed to load events. Please try again.</p>';
    }
}

/**
 * Render events list
 */
function renderEventsList(events) {
    const container = document.getElementById('merchantEventsList');
    
    if (events.length === 0) {
        container.innerHTML = `
            <div class="no-events-message">
                <i class="fas fa-calendar-times"></i>
                <h3>No Events Found</h3>
                <p>You haven't created any events yet.</p>
                <button class="btn btn-primary" onclick="switchTab('create-event')">
                    <i class="fas fa-plus"></i> Create Your First Event
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = events.map(event => `
        <div class="event-manage-card" data-event-id="${event.id}">
            <div class="event-manage-image">
                ${event.image_url ? `<img src="${event.image_url}" alt="${event.title}">` : '<div class="no-image"><i class="fas fa-image"></i></div>'}
                <span class="event-status-badge status-${event.status}">${capitalizeFirst(event.status)}</span>
            </div>
            <div class="event-manage-details">
                <h3>${event.title}</h3>
                <p class="event-category"><i class="fas fa-tag"></i> ${capitalizeFirst(event.category)}</p>
                <p class="event-date"><i class="fas fa-calendar-alt"></i> ${formatDate(event.event_date)}</p>
                <p class="event-venue"><i class="fas fa-map-marker-alt"></i> ${event.venue_name || 'N/A'}</p>
                <p class="event-price"><i class="fas fa-ticket-alt"></i> Standard: KSh ${parseFloat(event.standard_price).toLocaleString()} | VIP: KSh ${parseFloat(event.vip_price).toLocaleString()}</p>
                <div class="event-stats">
                    <span><i class="fas fa-eye"></i> ${event.views || 0} views</span>
                    <span><i class="fas fa-ticket-alt"></i> ${event.tickets_sold || 0} sold</span>
                </div>
            </div>
            <div class="event-manage-actions">
                <button class="btn btn-primary btn-sm" onclick="openEditModal(${event.id})">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-outline btn-sm" onclick="openDeleteModal(${event.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Filter events
 */
function filterEvents() {
    const status = document.getElementById('eventStatusFilter').value;
    const search = document.getElementById('eventSearch').value.toLowerCase();

    let filtered = merchantEvents;

    if (status !== 'all') {
        filtered = filtered.filter(e => e.status === status);
    }

    if (search) {
        filtered = filtered.filter(e => 
            e.title.toLowerCase().includes(search) ||
            e.category.toLowerCase().includes(search) ||
            (e.venue_name && e.venue_name.toLowerCase().includes(search))
        );
    }

    renderEventsList(filtered);
}

/**
 * Handle create event form submission
 */
async function handleCreateEvent(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Add merchant ID
    data.organizerId = currentMerchant.id;

    // Show loading
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('api_create_event.py', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Event created successfully!', 'success');
            e.target.reset();
            switchTab('my-events');
            loadMerchantEvents();
            loadOverviewStats();
        } else {
            showToast(result.message || 'Failed to create event', 'error');
        }
    } catch (error) {
        console.error('Error creating event:', error);
        showToast('Failed to create event. Please try again.', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

/**
 * Open edit modal
 */
function openEditModal(eventId) {
    const event = merchantEvents.find(e => e.id === eventId);
    if (!event) return;

    document.getElementById('editEventId').value = event.id;
    document.getElementById('editEventTitle').value = event.title;
    document.getElementById('editEventCategory').value = event.category;
    document.getElementById('editEventDescription').value = event.description;
    document.getElementById('editEventDate').value = event.event_date.slice(0, 16);
    document.getElementById('editVenueName').value = event.venue_name || '';
    document.getElementById('editStandardPrice').value = event.standard_price;
    document.getElementById('editVipPrice').value = event.vip_price;
    document.getElementById('editEventStatus').value = event.status;

    document.getElementById('editEventModal').style.display = 'block';
}

/**
 * Handle edit event form submission
 */
async function handleEditEvent(e) {
    e.preventDefault();

    const eventId = document.getElementById('editEventId').value;
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    data.eventId = eventId;

    // Show loading
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('api_update_event.py', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Event updated successfully!', 'success');
            document.getElementById('editEventModal').style.display = 'none';
            loadMerchantEvents();
            loadOverviewStats();
        } else {
            showToast(result.message || 'Failed to update event', 'error');
        }
    } catch (error) {
        console.error('Error updating event:', error);
        showToast('Failed to update event. Please try again.', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

/**
 * Open delete confirmation modal
 */
function openDeleteModal(eventId) {
    document.getElementById('deleteEventId').value = eventId;
    document.getElementById('deleteConfirmModal').style.display = 'block';
}

/**
 * Close delete modal
 */
function closeDeleteModal() {
    document.getElementById('deleteConfirmModal').style.display = 'none';
}

/**
 * Handle delete confirmation
 */
async function handleConfirmDelete() {
    const eventId = document.getElementById('deleteEventId').value;
    const btn = document.getElementById('confirmDeleteBtn');
    
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
    btn.disabled = true;

    try {
        const response = await fetch('api_delete_event.py', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ eventId })
        });

        const result = await response.json();

        if (result.success) {
            showToast('Event deleted successfully!', 'success');
            closeDeleteModal();
            loadMerchantEvents();
            loadOverviewStats();
        } else {
            showToast(result.message || 'Failed to delete event', 'error');
        }
    } catch (error) {
        console.error('Error deleting event:', error);
        showToast('Failed to delete event. Please try again.', 'error');
    } finally {
        btn.innerHTML = '<i class="fas fa-trash"></i> Delete Event';
        btn.disabled = false;
    }
}

/**
 * Load profile data
 */
function loadProfileData() {
    document.getElementById('profileName').value = currentMerchant.fullName || '';
    document.getElementById('profileEmail').value = currentMerchant.email || '';
    document.getElementById('profilePhone').value = currentMerchant.phone || '';
    document.getElementById('profileCompany').value = currentMerchant.companyName || '';
}

/**
 * Handle logout
 */
function handleLogout() {
    localStorage.removeItem('merchantData');
    window.location.href = 'index.html';
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.querySelector('.toast-message').textContent = message;
    toast.className = `toast toast-${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Format date
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Capitalize first letter
 */
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Initialize sidebar toggle functionality (hide/unhide sidebar)
 */
function initializeSidebarToggle() {
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('sidebar');
    const dashboardMain = document.querySelector('.dashboard-main');
    
    if (!sidebarToggleBtn || !sidebar) return;
    
    // Check localStorage for saved state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    
    // Apply saved state
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        if (dashboardMain) {
            dashboardMain.classList.add('expanded');
        }
    }
    
    // Toggle sidebar on button click
    sidebarToggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        
        if (dashboardMain) {
            dashboardMain.classList.toggle('expanded');
        }
        
        // Save state to localStorage
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', isCollapsed);
    });
}
