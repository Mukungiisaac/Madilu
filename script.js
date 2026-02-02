// Ticket Booking System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation (Hamburger Menu)
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        
        // Close menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
    }
    
    // DOM Elements
    const modal = document.getElementById('ticketModal');
    const closeModal = document.querySelector('.close-modal');
    const bookingForm = document.getElementById('bookingForm');
    const bookingStep = document.getElementById('bookingStep');
    const paymentStep = document.getElementById('paymentStep');
    const successStep = document.getElementById('successStep');
    const backToBooking = document.getElementById('backToBooking');
    const closeSuccess = document.getElementById('closeSuccess');
    const downloadReceipt = document.getElementById('downloadReceipt');
    const emailReceipt = document.getElementById('emailReceipt');
    const getTicketButtons = document.querySelectorAll('.get-tickets');
    
    // Payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method');
    const mpesaForm = document.getElementById('mpesaForm');
    const cardForm = document.getElementById('cardForm');
    
    // Current booking data
    let currentBooking = {
        eventName: '',
        price: 0,
        vipPrice: 0,
        fullName: '',
        email: '',
        phone: '',
        standardQty: 0,
        vipQty: 0,
        ticketType: 'mixed',
        idNumber: '',
        totalPrice: 0
    };
    
    // Initialize
    init();
    
    function init() {
        // Fetch events from API
        fetchEvents();
        
        // Add click handlers to all "Get Tickets" buttons
        getTicketButtons.forEach(button => {
            button.addEventListener('click', function() {
                const eventId = this.getAttribute('data-id');
                const eventName = this.getAttribute('data-event');
                const price = parseInt(this.getAttribute('data-price'));
                const vipPrice = parseInt(this.getAttribute('data-vip-price'));
                
                currentBooking.eventName = eventName;
                currentBooking.eventId = eventId;
                currentBooking.price = price;
                currentBooking.vipPrice = vipPrice;
                currentBooking.totalPrice = price;
                
                // Update modal content
                document.getElementById('modalEventName').textContent = eventName;
                document.querySelector('.price-display').textContent = price.toLocaleString();
                document.querySelector('.vip-price-display').textContent = vipPrice.toLocaleString();
                
                // Reset quantity inputs
                document.getElementById('standardQty').value = 0;
                document.getElementById('vipQty').value = 0;
                
                // Update price summary
                updatePriceSummary();
                
                // Show modal
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                
                // Reset to booking step
                showBookingStep();
            });
        });
        
        // Close modal handlers
        closeModal.addEventListener('click', closeModalFn);
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModalFn();
            }
        });
        
        // Back button handler
        backToBooking.addEventListener('click', function() {
            showBookingStep();
        });
        
        // Close success handler
        closeSuccess.addEventListener('click', closeModalFn);
        
        // Form submission handler
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect form data
            currentBooking.fullName = document.getElementById('fullName').value;
            currentBooking.email = document.getElementById('email').value;
            currentBooking.phone = document.getElementById('phone').value;
            currentBooking.standardQty = parseInt(document.getElementById('standardQty').value) || 0;
            currentBooking.vipQty = parseInt(document.getElementById('vipQty').value) || 0;
            currentBooking.idNumber = document.getElementById('idNumber').value;
            
            // Validate at least one ticket
            if (currentBooking.standardQty === 0 && currentBooking.vipQty === 0) {
                alert('Please select at least one ticket');
                return;
            }
            
            // Calculate total price
            currentBooking.totalPrice = (currentBooking.standardQty * currentBooking.price) + (currentBooking.vipQty * currentBooking.vipPrice);
            
            // Determine ticket type for display
            if (currentBooking.standardQty > 0 && currentBooking.vipQty > 0) {
                currentBooking.ticketType = 'mixed';
                currentBooking.quantity = currentBooking.standardQty + currentBooking.vipQty;
            } else if (currentBooking.vipQty > 0) {
                currentBooking.ticketType = 'vip';
                currentBooking.quantity = currentBooking.vipQty;
            } else {
                currentBooking.ticketType = 'standard';
                currentBooking.quantity = currentBooking.standardQty;
            }
            
            // Show payment step
            showPaymentStep();
        });
        
        // Quantity and ticket type change handlers
        document.querySelectorAll('.qty-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const type = this.getAttribute('data-type');
                const input = document.querySelector(`.ticket-qty[data-type="${type}"]`);
                let value = parseInt(input.value) || 0;
                
                if (this.classList.contains('qty-plus')) {
                    value++;
                } else if (this.classList.contains('qty-minus') && value > 0) {
                    value--;
                }
                
                input.value = value;
                updatePriceSummary();
            });
        });
        
        document.querySelectorAll('.ticket-qty').forEach(input => {
            input.addEventListener('input', updatePriceSummary);
            input.addEventListener('change', updatePriceSummary);
        });
        
        // Payment method selection
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                const paymentType = this.getAttribute('data-method');
                
                // Update active state
                paymentMethods.forEach(m => m.classList.remove('active'));
                this.classList.add('active');
                
                // Show appropriate form
                if (paymentType === 'mpesa') {
                    mpesaForm.style.display = 'block';
                    cardForm.style.display = 'none';
                } else {
                    mpesaForm.style.display = 'none';
                    cardForm.style.display = 'block';
                }
            });
        });
        
        // M-Pesa payment handler
        document.getElementById('payMpesa').addEventListener('click', function() {
            const mpesaPhone = document.getElementById('mpesaPhone').value;
            
            if (!mpesaPhone || mpesaPhone.length < 10) {
                alert('Please enter a valid M-Pesa phone number');
                return;
            }
            
            // Simulate payment processing
            processPayment('M-Pesa');
        });
        
        // Card payment handler
        document.getElementById('payCard').addEventListener('click', function() {
            const cardNumber = document.getElementById('cardNumber').value;
            const cardExpiry = document.getElementById('cardExpiry').value;
            const cardCvv = document.getElementById('cardCvv').value;
            
            if (!cardNumber || !cardExpiry || !cardCvv) {
                alert('Please fill in all card details');
                return;
            }
            
            // Simulate payment processing
            processPayment('Card');
        });
        
        // Download receipt handler
        downloadReceipt.addEventListener('click', downloadReceiptFn);
        
        // Email receipt handler
        emailReceipt.addEventListener('click', function() {
            alert('Receipt has been sent to ' + currentBooking.email);
        });
    }
    
    // Fetch events from API
    function fetchEvents() {
        // API URL - change localhost to your server IP if needed
        const apiUrl = 'http://localhost:8000/api_get_events.py';
        
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.data.length > 0) {
                    generateEventCards(data.data);
                } else {
                    // Show fallback static events if API fails or no events
                    console.log('No events from API, using static events');
                }
            })
            .catch(error => {
                console.log('API not available, using static events:', error);
            });
    }
    
    // Generate event cards dynamically
    function generateEventCards(events) {
        const eventsGrid = document.querySelector('.events-grid');
        if (!eventsGrid) return;
        
        // Clear existing static events
        eventsGrid.innerHTML = '';
        
        // Category icons mapping
        const categoryIcons = {
            'music': 'fa-guitar',
            'sports': 'fa-running',
            'arts': 'fa-mask',
            'business': 'fa-briefcase',
            'food': 'fa-utensils',
            'tech': 'fa-microchip'
        };
        
        // Generate cards for each event
        events.forEach((event, index) => {
            const card = document.createElement('div');
            card.className = 'event-card';
            card.style.animationDelay = (index * 0.1) + 's';
            
            const categoryIcon = categoryIcons[event.category] || 'fa-calendar-alt';
            const imageUrl = event.image_url || 'images/event-default.jpg';
            const formattedDate = event.event_date_formatted || new Date(event.event_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            
            card.innerHTML = `
                <div class="event-image">
                    <img src="${imageUrl}" alt="${event.title}">
                    <span class="event-badge">${index < 3 ? 'Trending' : 'Popular'}</span>
                    <span class="event-date">${formattedDate}</span>
                </div>
                <div class="event-details">
                    <span class="event-category"><i class="fas ${categoryIcon}"></i> ${event.category.charAt(0).toUpperCase() + event.category.slice(1)}</span>
                    <h3>${event.title}</h3>
                    <p class="event-venue"><i class="fas fa-map-marker-alt"></i> ${event.venue_name || event.venue_name}</p>
                    <p class="event-description">${event.description.substring(0, 100)}...</p>
                    <div class="event-footer">
                        <div class="event-price">
                            <span class="price-from">From</span>
                            <span class="price-amount">KSh ${parseInt(event.standard_price).toLocaleString()}</span>
                        </div>
                        <button class="btn btn-primary btn-sm get-tickets" 
                            data-id="${event.id}" 
                            data-event="${event.title}" 
                            data-price="${event.standard_price}"
                            data-vip-price="${event.vip_price}">
                            Get Tickets
                        </button>
                    </div>
                </div>
            `;
            
            eventsGrid.appendChild(card);
        });
        
        // Re-attach click handlers to new buttons
        document.querySelectorAll('.get-tickets').forEach(button => {
            button.addEventListener('click', function() {
                const eventId = this.getAttribute('data-id');
                const eventName = this.getAttribute('data-event');
                const price = parseInt(this.getAttribute('data-price'));
                const vipPrice = parseInt(this.getAttribute('data-vip-price'));
                
                currentBooking.eventName = eventName;
                currentBooking.eventId = eventId;
                currentBooking.price = price;
                currentBooking.vipPrice = vipPrice;
                currentBooking.totalPrice = price;
                
                // Update modal content
                document.getElementById('modalEventName').textContent = eventName;
                document.querySelector('.price-display').textContent = price.toLocaleString();
                document.querySelector('.vip-price-display').textContent = vipPrice.toLocaleString();
                
                // Reset quantity inputs
                document.getElementById('standardQty').value = 0;
                document.getElementById('vipQty').value = 0;
                
                // Update price summary
                updatePriceSummary();
                
                // Show modal
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
                
                // Reset to booking step
                showBookingStep();
            });
        });
    }
    
    function updatePriceSummary() {
        const standardQty = parseInt(document.getElementById('standardQty').value) || 0;
        const vipQty = parseInt(document.getElementById('vipQty').value) || 0;
        
        const standardTotal = standardQty * currentBooking.price;
        const vipTotal = vipQty * currentBooking.vipPrice;
        const total = standardTotal + vipTotal;
        
        document.getElementById('standardSummary').textContent = standardQty + ' x KSh ' + currentBooking.price.toLocaleString();
        document.getElementById('vipSummary').textContent = vipQty + ' x KSh ' + currentBooking.vipPrice.toLocaleString();
        document.getElementById('totalPrice').textContent = 'KSh ' + total.toLocaleString();
    }
    
    function showBookingStep() {
        bookingStep.style.display = 'block';
        paymentStep.style.display = 'none';
        successStep.style.display = 'none';
    }
    
    function showPaymentStep() {
        bookingStep.style.display = 'none';
        paymentStep.style.display = 'block';
        successStep.style.display = 'none';
        
        document.getElementById('paymentAmount').textContent = 'KSh ' + currentBooking.totalPrice.toLocaleString();
    }
    
    function showSuccessStep(paymentMethod) {
        bookingStep.style.display = 'none';
        paymentStep.style.display = 'none';
        successStep.style.display = 'block';
        
        // Generate booking reference
        const bookingRef = 'ITECH-' + Date.now().toString().slice(-6);
        
        // Get current date
        const today = new Date();
        const dateStr = today.toLocaleDateString('en-KE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        // Build ticket type string
        let ticketTypeStr = '';
        if (currentBooking.standardQty > 0 && currentBooking.vipQty > 0) {
            ticketTypeStr = currentBooking.standardQty + ' Standard + ' + currentBooking.vipQty + ' VIP';
        } else if (currentBooking.vipQty > 0) {
            ticketTypeStr = currentBooking.vipQty + ' VIP';
        } else {
            ticketTypeStr = currentBooking.standardQty + ' Standard';
        }
        
        // Populate receipt
        document.getElementById('bookingRef').textContent = bookingRef;
        document.getElementById('receiptEvent').textContent = currentBooking.eventName;
        document.getElementById('receiptDate').textContent = dateStr;
        document.getElementById('receiptName').textContent = currentBooking.fullName;
        document.getElementById('receiptEmail').textContent = currentBooking.email;
        document.getElementById('receiptPhone').textContent = currentBooking.phone;
        document.getElementById('receiptId').textContent = currentBooking.idNumber;
        document.getElementById('receiptQuantity').textContent = ticketTypeStr;
        document.getElementById('receiptType').textContent = currentBooking.ticketType === 'mixed' ? 'Mixed' : (currentBooking.ticketType === 'vip' ? 'VIP' : 'Standard');
        document.getElementById('receiptAmount').textContent = 'KSh ' + currentBooking.totalPrice.toLocaleString();
        document.getElementById('receiptMethod').textContent = paymentMethod;
    }
    
    function processPayment(method) {
        // Show loading state
        const payButton = method === 'M-Pesa' ? 
            document.getElementById('payMpesa') : 
            document.getElementById('payCard');
        
        const originalText = payButton.textContent;
        payButton.textContent = 'Processing...';
        payButton.disabled = true;
        
        // Simulate payment processing delay
        setTimeout(function() {
            payButton.textContent = originalText;
            payButton.disabled = false;
            
            // Show success
            showSuccessStep(method);
        }, 2000);
    }
    
    function closeModalFn() {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Reset form
        bookingForm.reset();
        updatePriceSummary();
    }
    
    function downloadReceiptFn() {
        // Create receipt content
        const receiptContent = `
========================================
         iTECH EVENTS - TICKET RECEIPT
========================================

Booking Reference: ${document.getElementById('bookingRef').textContent}
Date: ${document.getElementById('receiptDate').textContent}

----------------------------------------
EVENT DETAILS
----------------------------------------
Event: ${document.getElementById('receiptEvent').textContent}

----------------------------------------
CUSTOMER DETAILS
----------------------------------------
Name: ${document.getElementById('receiptName').textContent}
Email: ${document.getElementById('receiptEmail').textContent}
Phone: ${document.getElementById('receiptPhone').textContent}
ID Number: ${document.getElementById('receiptId').textContent}

----------------------------------------
TICKET INFORMATION
----------------------------------------
Tickets: ${document.getElementById('receiptQuantity').textContent}
Type: ${document.getElementById('receiptType').textContent}

----------------------------------------
PAYMENT
----------------------------------------
Total Paid: ${document.getElementById('receiptAmount').textContent}
Payment Method: ${document.getElementById('receiptMethod').textContent}

========================================
Thank you for booking with iTech Events!

Please present this receipt at the venue entry.
========================================
        `.trim();
        
        // Create blob and download
        const blob = new Blob([receiptContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'iTech_Events_Receipt_' + document.getElementById('bookingRef').textContent + '.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
    
    // =========================================
    // MERCHANT REGISTRATION MODAL FUNCTIONALITY
    // =========================================
    
    // DOM Elements
    const postEventBtn = document.getElementById('postEventBtn');
    const signInBtn = document.getElementById('signInBtn');
    const merchantModal = document.getElementById('merchantModal');
    const closeMerchantModal = document.getElementById('closeMerchantModal');
    const merchantChoiceStep = document.getElementById('merchantChoiceStep');
    const merchantLoginStep = document.getElementById('merchantLoginStep');
    const merchantRegisterStep = document.getElementById('merchantRegisterStep');
    const merchantSuccessStep = document.getElementById('merchantSuccessStep');
    const postEventStep = document.getElementById('postEventStep');
    
    // Buttons
    const showLoginBtn = document.getElementById('showLoginBtn');
    const showRegisterBtn = document.getElementById('showRegisterBtn');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    const backToChoice = document.getElementById('backToChoice');
    const backToChoiceFromRegister = document.getElementById('backToChoiceFromRegister');
    const proceedToPostEvent = document.getElementById('proceedToPostEvent');
    const closeMerchantSuccess = document.getElementById('closeMerchantSuccess');
    const logoutFromPost = document.getElementById('logoutFromPost');
    
    // Forms
    const merchantLoginForm = document.getElementById('merchantLoginForm');
    const merchantRegisterForm = document.getElementById('merchantRegisterForm');
    const postEventForm = document.getElementById('postEventForm');
    
    // Simulated logged in state
    let isMerchantLoggedIn = false;
    let currentMerchant = null;
    
    // Open merchant modal when clicking "Post Event"
    if (postEventBtn) {
        postEventBtn.addEventListener('click', function() {
            if (isMerchantLoggedIn) {
                // Show post event form directly
                showPostEventStep();
            } else {
                // Show login/register choice
                showMerchantStep('choice');
            }
            merchantModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    }
    
    // Open merchant modal when clicking "Sign In" - show login directly
    if (signInBtn) {
        signInBtn.addEventListener('click', function() {
            if (isMerchantLoggedIn) {
                // User is already logged in, show logout option
                alert('You are logged in as ' + (currentMerchant?.name || currentMerchant?.companyName));
            } else {
                // Show login form directly
                showMerchantStep('login');
                merchantModal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    }
    
    // Close merchant modal
    if (closeMerchantModal) {
        closeMerchantModal.addEventListener('click', closeMerchantModalFn);
    }
    
    merchantModal.addEventListener('click', function(e) {
        if (e.target === merchantModal) {
            closeMerchantModalFn();
        }
    });
    
    function closeMerchantModalFn() {
        merchantModal.style.display = 'none';
        document.body.style.overflow = 'auto';
        // Reset to choice step
        showMerchantStep('choice');
    }
    
    // Show specific step
    function showMerchantStep(step) {
        merchantChoiceStep.style.display = 'none';
        merchantLoginStep.style.display = 'none';
        merchantRegisterStep.style.display = 'none';
        merchantSuccessStep.style.display = 'none';
        postEventStep.style.display = 'none';
        
        switch(step) {
            case 'choice':
                merchantChoiceStep.style.display = 'block';
                break;
            case 'login':
                merchantLoginStep.style.display = 'block';
                break;
            case 'register':
                merchantRegisterStep.style.display = 'block';
                break;
            case 'success':
                merchantSuccessStep.style.display = 'block';
                break;
            case 'postEvent':
                postEventStep.style.display = 'block';
                break;
        }
    }
    
    function showPostEventStep() {
        showMerchantStep('postEvent');
    }
    
    // Show login step
    if (showLoginBtn) {
        showLoginBtn.addEventListener('click', function() {
            showMerchantStep('login');
        });
    }
    
    // Show register step
    if (showRegisterBtn) {
        showRegisterBtn.addEventListener('click', function() {
            showMerchantStep('register');
        });
    }
    
    // Switch between login and register
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function(e) {
            e.preventDefault();
            showMerchantStep('register');
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            showMerchantStep('login');
        });
    }
    
    // Back buttons
    if (backToChoice) {
        backToChoice.addEventListener('click', function() {
            showMerchantStep('choice');
        });
    }
    
    if (backToChoiceFromRegister) {
        backToChoiceFromRegister.addEventListener('click', function() {
            showMerchantStep('choice');
        });
    }
    
    // Proceed to post event after registration success
    if (proceedToPostEvent) {
        proceedToPostEvent.addEventListener('click', function() {
            showPostEventStep();
        });
    }
    
    // Close after success
    if (closeMerchantSuccess) {
        closeMerchantSuccess.addEventListener('click', closeMerchantModalFn);
    }
    
    // Logout
    if (logoutFromPost) {
        logoutFromPost.addEventListener('click', function() {
            isMerchantLoggedIn = false;
            currentMerchant = null;
            closeMerchantModalFn();
        });
    }
    
    // Merchant login form submission
    if (merchantLoginForm) {
        merchantLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            // Simulate login (in real app, this would be an API call)
            if (email && password) {
                isMerchantLoggedIn = true;
                currentMerchant = { 
                    id: 1, // In real app, this would come from the API
                    email: email, 
                    name: email.split('@')[0] 
                };
                
                // Show success message
                alert('Login successful! Welcome back, ' + currentMerchant.name);
                
                // Show post event form
                showPostEventStep();
                
                // Reset form
                merchantLoginForm.reset();
            }
        });
    }
    
    // Merchant registration form submission
    if (merchantRegisterForm) {
        merchantRegisterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // Validate password match
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            // Collect form data
            const companyName = document.getElementById('companyName').value;
            const contactName = document.getElementById('contactName').value;
            const email = document.getElementById('regEmail').value;
            const phone = document.getElementById('regPhone').value;
            const businessType = document.getElementById('businessType').value;
            const idNumber = document.getElementById('idNumber').value;
            
            // Prepare form data for API
            const formData = new URLSearchParams();
            formData.append('fullName', contactName);
            formData.append('email', email);
            formData.append('phone', phone);
            formData.append('idNumber', idNumber);
            formData.append('password', password);
            formData.append('companyName', companyName);
            formData.append('businessType', businessType);
            
            // Show loading
            const submitBtn = merchantRegisterForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating Account...';
            submitBtn.disabled = true;
            
            // For now, simulate registration and auto-login
            isMerchantLoggedIn = true;
            currentMerchant = {
                id: 1, // In real app, this would come from the API response
                companyName: companyName,
                contactName: contactName,
                email: email,
                phone: phone,
                businessType: businessType
            };
            
            // Show success step
            showMerchantStep('success');
            
            // Reset form
            merchantRegisterForm.reset();
            
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
    
    // Post event form submission
    if (postEventForm) {
        postEventForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const eventTitle = document.getElementById('eventTitle').value;
            const eventCategory = document.getElementById('eventCategory').value;
            const eventDate = document.getElementById('eventDate').value;
            const eventVenue = document.getElementById('eventVenue').value;
            const eventDescription = document.getElementById('eventDescription').value;
            const standardPrice = document.getElementById('standardPrice').value;
            const vipPrice = document.getElementById('vipPrice').value;
            const eventImage = document.getElementById('eventImage').value;
            
            // Validate required fields
            if (!currentMerchant || !currentMerchant.id) {
                alert('Please log in as a merchant first.');
                return;
            }
            
            // Prepare form data
            const formData = new URLSearchParams();
            formData.append('organizerId', currentMerchant.id);
            formData.append('venueId', 1); // Default venue, you may want to create venues dynamically
            formData.append('title', eventTitle);
            formData.append('description', eventDescription);
            formData.append('category', eventCategory);
            formData.append('eventDate', eventDate + ' 00:00:00');
            formData.append('standardPrice', standardPrice);
            formData.append('vipPrice', vipPrice);
            formData.append('imageUrl', eventImage);
            
            // Show loading
            const submitBtn = postEventForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Publishing...';
            submitBtn.disabled = true;
            
            // Call API
            fetch('http://localhost:8000/api_create_event.py', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData.toString()
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Event "' + eventTitle + '" has been published successfully!\n\nIt will appear in the featured events section.');
                    
                    // Refresh events list
                    fetchEvents();
                    
                    // Close modal
                    closeMerchantModalFn();
                    
                    // Reset form
                    postEventForm.reset();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to publish event. Please try again.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // =========================================
    // END MERCHANT REGISTRATION MODAL
    // =========================================
});
