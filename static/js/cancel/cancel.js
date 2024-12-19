document.addEventListener("DOMContentLoaded", () => {
    const shatteredContainer = document.querySelector(".shattered-container");
    for (let i = 0; i < 40; i++) {
        const shard = document.createElement("div");
        shard.classList.add("shard");
        shard.style.left = `${Math.random() * 100}vw`;
        shard.style.animationDelay = `${Math.random() * 2}s`;
        shard.style.transform = `rotate(${Math.random() * 180}deg)`;
        shard.style.width = `${Math.random() * 5 + 5}px`;
        shard.style.height = `${Math.random() * 10 + 10}px`;
        shatteredContainer.appendChild(shard);
    }
});
