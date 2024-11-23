document.addEventListener("DOMContentLoaded", async () => {
    const messageBox = document.querySelector("#message");
    const sendButton = document.querySelector(".send-button");
    const conversationView = document.querySelector(".conversation-view");
    const sidebar = document.querySelector("#sidebar");
    const hide_sidebar = document.querySelector(".hide-sidebar");
    const newChatButton = document.querySelector(".new-chat");
    const username = document.getElementById("userMenu").getAttribute("data-username");

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

    messageBox.addEventListener("keyup", function () {
        messageBox.style.height = "auto";
        let height = messageBox.scrollHeight + 2;
        if (height > 200) {
            height = 200;
        }
        messageBox.style.height = height + "px";
    });

    function showView(viewSelector) {
        document.querySelectorAll(".view").forEach((view) => {
            view.style.display = "none";
        });
        document.querySelector(viewSelector).style.display = "flex";
    }

    newChatButton?.addEventListener("click", function () {
        window.location.href = "/home";
    });

    document.querySelectorAll(".conversation-button").forEach((button) => {
        button.addEventListener("click", function () {
            showView(".conversation-view");
        });
    });

   /////////////////////////////////////////////////// Clear the conversation ////////////////////////////////////////////////

    function clearConversationView() {
        const conversationView = document.querySelector(".conversation-view");
        if (conversationView) {
            conversationView.innerHTML = "";
        }
    }

    /////////////////////////////////////////////////// Load the messages & sidebar /////////////////////////////////////////////

    window.onload = function() {
        const sessionTitlesJSON = document.getElementById("session-titles").getAttribute("data-titles");
        const messagesJSON = document.getElementById("session-titles").getAttribute("data-messages");
    
        console.log("Raw data in data-titles:", sessionTitlesJSON);
        console.log("Raw data in data-messages:", messagesJSON);
    
        try {
            if (sessionTitlesJSON.trim().startsWith('[') && sessionTitlesJSON.trim().endsWith(']')) {
                const sessionTitles = JSON.parse(sessionTitlesJSON);
    
                if (sessionTitles.length === 0) {
                    console.log("No sessions available for this user.");
                    return;
                }
                
                sessionTitles.forEach(session => {
                    addConversationToSidebar(session.title, session.session_id, session.date);
                });
            } else {
                console.error("Invalid JSON format in data-titles:", sessionTitlesJSON);
            }
            
            const sessionTitles_message = JSON.parse(sessionTitlesJSON);
            const sessionIds = sessionTitles_message.map(session => session.session_id);
            if (messagesJSON.trim().startsWith('[') && messagesJSON.trim().endsWith(']')) {
                const messages = JSON.parse(messagesJSON);
                messages.forEach(message => {
                    if (sessionIds.includes(message.session_id)) {
                        displayMessage(message.content, message.role);
                    } else {
                        console.warn("Message session_id does not match any session:", message.session_id);
                    }
                });
            } else {
                console.error("Invalid JSON format in data-messages:", messagesJSON);
            }
        } catch (error) {
            console.error("Error parsing session titles or messages JSON:", error);
        }
    };
    
    ///////////////////////////////////////////////////////// Function to add display chat message role & content ////////////////////////////////////

    function displayMessage(content, sender, isTyping = false) {
        if (!conversationView) {
            console.error("Conversation view element not found.");
            return;
        }

        const messageContainer = document.createElement("div");
        messageContainer.classList.add(sender, "message");

        const identity = document.createElement("div");
        identity.classList.add("identity");

        const icon = document.createElement("i");
        icon.classList.add(sender === "user" ? "user-icon" : "gpt", "user-icon");
        icon.textContent = sender === "user" ? username[0].toUpperCase() : "H";
        identity.appendChild(icon);

        const contentDiv = document.createElement("div");
        contentDiv.classList.add("content");
        if (isTyping) {
            contentDiv.innerHTML = `<p><span class="typing-text">Typing</span><span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></p>`;
        } else {
            contentDiv.innerHTML = `<p>${content}</p>`;
        }

        messageContainer.appendChild(identity);
        messageContainer.appendChild(contentDiv);
        conversationView.appendChild(messageContainer);
        conversationView.scrollTop = conversationView.scrollHeight;
   
        return contentDiv;
    }

    /////////////////////////////////////////////////////////// Function to add Sidebar titles ////////////////////////////////////////////

    function addConversationToSidebar(title, sessionId, date) {
        const conversationsList = document.querySelector(".conversations");
    
        const today = new Date().toISOString().split("T")[0];
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const isToday = date === today;
        const isYesterday = date === yesterday;
    
        let todayGrouping = conversationsList.querySelector(".grouping-today");
        if (!todayGrouping) {
            todayGrouping = document.createElement("li");
            todayGrouping.classList.add("grouping", "grouping-today");
            todayGrouping.textContent = "Today";
            conversationsList.insertBefore(todayGrouping, conversationsList.firstChild);
        }
    
        let yesterdayGrouping = conversationsList.querySelector(".grouping-yesterday");
        if (!yesterdayGrouping) {
            yesterdayGrouping = document.createElement("li");
            yesterdayGrouping.classList.add("grouping", "grouping-yesterday");
            yesterdayGrouping.textContent = "Yesterday";
            conversationsList.insertBefore(yesterdayGrouping, todayGrouping.nextSibling);
        }
    
        let otherGrouping = conversationsList.querySelector(`.grouping-${date}`);
        if (!isToday && !isYesterday && !otherGrouping) {
            otherGrouping = document.createElement("li");
            otherGrouping.classList.add("grouping", `grouping-${date}`);
            otherGrouping.textContent = date;
    
            const allGroupings = Array.from(conversationsList.querySelectorAll(".grouping"));
            const insertAfter = allGroupings.reverse().find(grouping => grouping.textContent < date);
            if (insertAfter) {
                conversationsList.insertBefore(otherGrouping, insertAfter.nextSibling);
            } else {
                conversationsList.appendChild(otherGrouping);
            }
        }
    
        const existingConversation = Array.from(conversationsList.children).find(conversationItem => {
            const conversationButton = conversationItem.querySelector(".conversation-button");
            return conversationButton && conversationButton.innerHTML.includes(title);
        });
    
        if (existingConversation) {
            return;
        }
    
        const conversationItem = document.createElement("li");
        conversationItem.classList.add("active");
    
        const conversationButton = document.createElement("button");
        conversationButton.classList.add("conversation-button");
        conversationButton.innerHTML = `<i class="fa fa-message fa-regular"></i> ${title}`;
    
        conversationButton.addEventListener("click", async function () {
            history.pushState({}, "", `/c/${sessionId}`);
            clearConversationView();
            showView(".conversation-view");
    
            const response = await fetch(`/get-chat/${sessionId}`);
            const data = await response.json();
    
            if (data.messages) {
                data.messages.forEach(message => {
                    displayMessage(message.content, message.role);
                });
            } else {
                console.error("Error loading messages:", data.error);
            }
        });
    
        const fadeDiv = document.createElement("div");
        fadeDiv.classList.add("fade");
    
        const editButtons = document.createElement("div");
        editButtons.classList.add("edit-buttons");
    
        const editButton = document.createElement("button");
        editButton.innerHTML = '<i class="fa fa-edit"></i>';
    
        const deleteButton = document.createElement("button");
        deleteButton.innerHTML = '<i class="fa fa-trash"></i>';
    
        editButtons.appendChild(editButton);
        editButtons.appendChild(deleteButton);
    
        conversationItem.appendChild(conversationButton);
        conversationItem.appendChild(fadeDiv);
        conversationItem.appendChild(editButtons);
    
        if (isToday) {
            conversationsList.insertBefore(conversationItem, todayGrouping.nextSibling);
        } else if (isYesterday) {
            conversationsList.insertBefore(conversationItem, yesterdayGrouping.nextSibling);
        } else {
            conversationsList.insertBefore(conversationItem, otherGrouping.nextSibling);
        }
    
        conversationItem.offsetHeight;
    }
        
    
    //////////////////////////////////////////////////////////////// Function to handleSendMessage ///////////////////////////////////////

    async function handleSendMessage() {
        const userMessage = messageBox.value.trim();
        if (!userMessage) {
            console.warn("Message is empty.");
            return;
        }

        showView(".conversation-view");

        displayMessage(userMessage, "user");
        messageBox.value = "";

        const typingIndicatorContent = displayMessage("", "assistant", true);

        try {
            const sessionId = window.location.pathname.split("/")[2];
            const response = await fetch("/query-bot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username, question: userMessage , session_id: sessionId}),
            });

            const data = await response.json();

            if (data.response) {
                typingIndicatorContent.innerHTML = `<p>${data.response}</p>`;
                if (data.title) {
                    addConversationToSidebar(data.title, sessionId, new Date().toISOString().split("T")[0]);
                }
            } else {
                console.error("API Error:", data.error);
                typingIndicatorContent.innerHTML = `<p>Something went wrong. Please try again.</p>`;
            }
        } catch (error) {
            console.error("Error during API call:", error);
            typingIndicatorContent.innerHTML = `<p>Failed to connect to the server. Please try later.</p>`;
        } 
    }

    sendButton.addEventListener("click", handleSendMessage);

    messageBox.addEventListener("keypress", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    });
});
