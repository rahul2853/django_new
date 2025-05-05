document.addEventListener('DOMContentLoaded', function() {
    // AJAX for cart forms
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    const updateQuantityForms = document.querySelectorAll('.update-quantity-form');
    
    // Add to cart functionality with AJAX
    if (addToCartForms) {
        addToCartForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const url = this.getAttribute('action');
                
                fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Update cart counter
                        const cartCounter = document.querySelector('.fa-shopping-cart + .badge');
                        if (cartCounter) {
                            cartCounter.textContent = data.cart_total;
                        }
                        
                        // Show success message
                        const toastHTML = `
                            <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
                                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                                    <div class="toast-header bg-success text-white">
                                        <strong class="me-auto">Item Added</strong>
                                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                                    </div>
                                    <div class="toast-body">
                                        ${data.message}
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Append toast to body
                        const toastContainer = document.createElement('div');
                        toastContainer.innerHTML = toastHTML;
                        document.body.appendChild(toastContainer);
                        
                        // Automatically remove the toast after 3 seconds
                        setTimeout(() => {
                            toastContainer.remove();
                        }, 3000);
                        
                        // Reset quantity input to 1
                        const quantityInput = this.querySelector('input[name="quantity"]');
                        if (quantityInput) {
                            quantityInput.value = 1;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    }
    
    // Update cart quantity functionality with AJAX
    if (updateQuantityForms) {
        updateQuantityForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const url = this.getAttribute('action');
                const row = this.closest('tr');
                
                fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Update item total
                        if (row) {
                            const itemTotal = row.querySelector('.item-total');
                            if (itemTotal) {
                                itemTotal.textContent = '$' + data.item_total;
                            }
                        }
                        
                        // Update cart total
                        const cartTotal = document.querySelector('.cart-total');
                        if (cartTotal) {
                            cartTotal.textContent = '$' + data.cart_total;
                        }
                        
                        // Update cart counter
                        const cartCounter = document.querySelector('.fa-shopping-cart + .badge');
                        if (cartCounter) {
                            cartCounter.textContent = data.item_count;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    }
});
