document.addEventListener("DOMContentLoaded", () => {
    const emojiContainer = document.querySelector(".emoji-container");
    for (let i = 0; i < 40; i++) {
        const emoji = document.createElement("div");
        emoji.classList.add("emoji");
        emoji.textContent = "🎉";
        emoji.style.left = `${Math.random() * 100}vw`;
        emoji.style.animationDelay = `${Math.random() * 2}s`;
        emoji.style.fontSize = `${Math.random() * 1.5 + 1}rem`;
        emojiContainer.appendChild(emoji);
    }

    document.getElementById('return-dashboard').addEventListener('click', async () => {
        const data = {
            username: localStorage.getItem('username'),
            plan: "Plus",
            plan_update_date: new Date().toISOString(),
            plan_expiry_date: new Date(new Date().getTime() + 30 * 24 * 60 * 60 * 1000).toISOString()
        };
    
        try {
            const response = await fetch('/update-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
    
            if (response.ok) {
                window.location.href = "/home";
            } else {
                console.error('Failed to update plan:', await response.text());
            }
        } catch (error) {
            console.error('Error updating plan:', error);
        }
    });
    
});
