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
                showModal(data.results);
            } else {
                alert("Error: Unexpected response from the server.");
            }
        })
        .catch(error => {
            hideLoader();
            console.error('Error validating files:', error);
            alert('An error occurred while validating files. Please try again.');
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

            const formData = new FormData();
            [...files].forEach(file => {
                formData.append('files[]', file);
                console.log(`File uploaded: ${file.name}`);
            });

            startProcessing(formData);

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
                } else {
                    alert('Error processing files.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while processing.');
            } finally {
                hideLoader();
            }
        }
    
        document.getElementById('cancel-btn').addEventListener('click', () => {
            removeModal();
        });
    
        document.addEventListener('keydown', handleKeydown);
    }       

});