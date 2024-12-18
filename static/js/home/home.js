document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.querySelector("#sidebar");
    const hide_sidebar = document.querySelector(".hide-sidebar");
    const new_chat_button = document.querySelector(".new-chat");

    hide_sidebar.addEventListener( "click", function() {
        sidebar.classList.toggle( "hidden" );
    } );

    const user_menu = document.querySelector(".user-menu ul");
    const show_user_menu = document.querySelector(".user-menu button");

    show_user_menu.addEventListener( "click", function() {
        if( user_menu.classList.contains("show") ) {
            user_menu.classList.toggle( "show" );
            setTimeout( function() {
                user_menu.classList.toggle( "show-animate" );
            }, 200 );
        } else {
            user_menu.classList.toggle( "show-animate" );
            setTimeout( function() {
                user_menu.classList.toggle( "show" );
            }, 50 );
        }
    } );

    const models = document.querySelectorAll(".model-selector button");

    for( const model of models ) {
        model.addEventListener("click", function() {
            document.querySelector(".model-selector button.selected")?.classList.remove("selected");
            model.classList.add("selected");
        });
    }

    const message_box = document.querySelector("#message");

    message_box.addEventListener("keyup", function() {
        message_box.style.height = "auto";
        let height = message_box.scrollHeight + 2;
        if( height > 200 ) {
            height = 200;
        }
        message_box.style.height = height + "px";
    });

    function show_view( view_selector ) {
        document.querySelectorAll(".view").forEach(view => {
            view.style.display = "none";
        });

        document.querySelector(view_selector).style.display = "flex";
    }

    new_chat_button.addEventListener("click", function() {
        show_view( ".new-chat-view" );
    });

    document.querySelectorAll(".conversation-button").forEach(button => {
        button.addEventListener("click", function() {
            show_view( ".conversation-view" );
        })
    });

    ////////////////////// Toastofy ////////////////////////////////////////////

    function showToast(message, type = 'success') {
        Toastify({
            text: message,
            duration: 3000,
            close: true, 
            gravity: "top",
            position: "right",
            backgroundColor: type === 'error' ? "#FF5F6D" : "#00b09b",
            stopOnFocus: true,
        }).showToast();
    }

    ////////////////////// Customize Model /////////////////////////////////////

    const settingsBtn = document.getElementById("settings-btn");
    const modal = document.getElementById("settings-modal");
    const closeModal = document.querySelector(".close-btn");
    const sidebarItems = document.querySelectorAll(".settings-item");
    const contentSections = document.querySelectorAll(".content-section");
    const planDropdown = document.getElementById('plan-dropdown');
    const langDropdown = document.getElementById('lang');
    
    const deleteChatsButton = document.getElementById('delete-chats-button');
    const deleteAccountButton = document.querySelector('.delete-acc');
    const confirmationModal = document.getElementById('confirmation-modal');
    const modalContent = document.querySelector('.confirm-modal-content h4');
    const modalDescription = document.querySelector('.confirm-modal-content p');
    const cancelButton = document.getElementById('cancel-delete');
    const proceedButton = document.getElementById('confirm-delete');
    
    async function fetchUserCredentials() {
        try {
            const response = await fetch('/user_plan');
            const data = await response.json();
            if (data.subscription) {
                if (data.subscription === "Plus") {
                    planDropdown.value = "Plus";
                    langDropdown.value = "Auto-detect" 
                } else {
                    planDropdown.value = "Free"; 
                    langDropdown.value = "English"
                }
            } else {
                showToast('Error: Subscription data not found', 'error');
            }
        } catch (error) {
            showToast("Error fetching user credentials: " + error.message, 'error');
        }
    }

    fetchUserCredentials();

    settingsBtn.addEventListener("click", () => {
        modal.style.display = "block";
    });

    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    sidebarItems.forEach(item => {
        item.addEventListener("click", () => {
            sidebarItems.forEach(i => i.classList.remove("active"));
            contentSections.forEach(section => section.classList.remove("active"));
            item.classList.add("active");
            const targetId = item.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");
        });
    });

    sidebarItems[0].classList.add("active");
    contentSections[0].classList.add("active");    

    deleteChatsButton.addEventListener('click', function () {
        modalContent.textContent = "Are you sure you want to delete all chats?";
        modalDescription.textContent = "This action cannot be undone.";
        proceedButton.dataset.action = "deleteChats";
        confirmationModal.style.display = 'block';
    });

    deleteAccountButton.addEventListener('click', function () {
        modalContent.textContent = "Are you sure you want to delete your account?";
        modalDescription.textContent = "This action will permanently delete your account.";
        proceedButton.dataset.action = "deleteAccount";
        confirmationModal.style.display = 'block';
    });

    cancelButton.addEventListener('click', function () {
        confirmationModal.style.display = 'none';
    });

    proceedButton.addEventListener('click', async function () {
        confirmationModal.style.display = 'none';
        const action = proceedButton.dataset.action;

        try {
            let response;
            if (action === "deleteChats") {
                response = await fetch('/delete_chats', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                });
            } else if (action === "deleteAccount") {
                response = await fetch('/delete-account', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                });
            }

            const result = await response.json();
            if (response.ok) {
                showToast(
                    action === "deleteChats" 
                    ? 'All chats deleted successfully!' 
                    : 'Account deleted successfully!', 
                    'success'
                );
    
                if (action === "deleteAccount") {
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                }
            } else {
                showToast(result.error || 'Action failed. Please try again.', 'error');
            }
        } catch (error) {
            showToast('An error occurred. Please try again.', 'error');
        }
    });

    ///////////////////// Upload Files Upload //////////////////////////////////

    const uploadContainer = document.querySelector('.drag-drop-container');
    const fileInput = document.getElementById('file-upload');

    uploadContainer.addEventListener('click', () => fileInput.click());

    uploadContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadContainer.classList.add('drag-over');
    });

    uploadContainer.addEventListener('dragleave', () => {
        uploadContainer.classList.remove('drag-over');
    });

    uploadContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadContainer.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(fileInput.files);
    });

    ////////////////////////////// API validate_files to validate and show the model //////////////////////////////////

    function hideLoader() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.remove();
            document.removeEventListener('keydown', handleLoaderKeydown);
        }
    }

    function handleLoaderKeydown(event) {
        if (event.key === 'Escape') {
            hideLoader();
        }
    }

    function showLoader() {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.style.display = 'flex';
            document.addEventListener('keydown', handleLoaderKeydown);
        } else {
            console.error('Loader element not found in the DOM.');
        }
    }

    function handleFiles(files) {
        const formData = new FormData();
        [...files].forEach(file => {
            formData.append('files[]', file);
            console.log(`File uploaded: ${file.name}`);
        });

        showLoader();

        fetch('/validate_files', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            hideLoader();
            if (Array.isArray(data.results)) {
                const successCount = data.results.filter(result => result.status === "✅ Text extracted successfully").length;
                sessionStorage.setItem('successCount', successCount);
                console.log(`Number of files with successful text extraction: ${successCount}`);
                showModal(data.results);
            } else if (data.error) {
                showToast(`${data.error}`, 'error');
            } else {
                showToast("Error: Unexpected response from the server", 'error');
            }
        })
        .catch(error => {
            hideLoader();
            console.error('Error validating files:', error);
            showToast('An error occurred while validating files. Please try again.', 'error');
        });
    }
    

    ////////////////////////////////////// showing Model ////////////////////////////////////////////////

    function showModal(results = []) {
        const modal = document.createElement('div');
        modal.id = 'file-validation-modal';
        
        const backdrop = document.createElement('div');
        backdrop.classList.add('modal-backdrop');
    
        modal.innerHTML = `
            <div class="modal-content">
                <h2>File Validation Results</h2>
                <div class="file-list">
                    ${results.length
                        ? results.map(result =>
                            `<div class="file-item">
                                ${result.filename} - ${result.status}
                            </div>`
                        ).join('')
                        : '<p>No files uploaded</p>'
                    }
                </div>
                <div class="modal-actions">
                    <button id="process-btn">Process</button>
                    <button id="cancel-btn">Cancel</button>
                </div>
            </div>
        `;
    
        document.body.appendChild(backdrop);
        document.body.appendChild(modal);
        document.body.classList.add('modal-open'); 
    
        function removeModal() {
            modal.remove();
            backdrop.remove();
            document.body.classList.remove('modal-open');
            document.removeEventListener('keydown', handleKeydown);
        }
    
        function handleKeydown(event) {
            if (event.key === 'Escape') {
                removeModal();
            }
        }
    
        document.getElementById('process-btn').addEventListener('click', () => {
            removeModal();
            const fileInput = document.getElementById('file-upload');
            const files = fileInput.files;

            if (!files.length) {
                showToast("Please upload at least one file.", "error");
                return;
            }        

            const successCount = parseInt(sessionStorage.getItem('successCount'), 10) || 0;
                if (successCount > 0) {
                    const formData = new FormData();
                    [...files].forEach(file => {
                        formData.append('files[]', file);
                        console.log(`File uploaded: ${file.name}`);
                    });

                    startProcessing(formData);
                } else {
                    showToast("There is no text generated from any of the files uploaded.", "error");
                }
            });

        function showLoader_2() {
            if (!document.getElementById('loader')) {
                const loader = document.createElement('div');
                loader.id = 'loader';
                loader.innerHTML = '<div class="spinner"></div><p>Processing...</p>';
                document.body.appendChild(loader);
                document.addEventListener('keydown', handleLoaderKeydown);
            }
        } 

        async function startProcessing(formData) {
            showLoader_2();
            try {
                const response = await fetch('/process_files', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json();
                if (data.session_url) {
                    window.location.href = data.session_url;
                } else if (data.error) {
                    showToast(data.error, 'error');
                } else {
                    showToast('Error processing files.', 'error');
                }
            } catch (error) {
                showToast('An error occurred while processing.', 'error');
            } finally {
                hideLoader();
            }
        }        

        document.getElementById('cancel-btn').addEventListener('click', () => {
            removeModal();
        });
    
        document.addEventListener('keydown', handleKeydown);
    }       

    ///////////////////////////////////////////// Make a Stripe Payment //////////////////////////////////////////////////
    const username = document.getElementById("userMenu").getAttribute("data-username");

    document.getElementById('plan-dropdown').addEventListener('change', function () {
        const selectedPlan = this.value;
        if (selectedPlan === "Plus") {
            showLoader();
            redirectToStripe();
        }
    });
    
    async function redirectToStripe() {
        try {
            const response = await fetch('/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan: 'Plus',
                    username: username
                }),
            });
    
            if (!response.ok) {
                throw new Error('Failed to create Stripe session');
            }
    
            const { sessionId, status } = await response.json();
            console.log("Session ID:", sessionId, "Status:", status);
            if (status === 'success') {
                const stripe = Stripe('pk_test_51QMqgQGAuM9oavUCVFhplM1y5cIz1LPNGS5ZWNDD8iBZCXNjjC54AdAfNvV6qLa6PzmSlTkMfDUNVqHOllrHYV2000YFtB5c0b');
                await stripe.redirectToCheckout({ sessionId });
            } else {
                showToast('Payment failed, please try again.', 'error');
            }
        } catch (error) {
            console.error('Error redirecting to Stripe:', error.message);
            showToast('Error redirecting to payment page: ' + error.message, 'error');
        } finally {
            hideLoader()
        }
    }

});