document.addEventListener("DOMContentLoaded", () => {
    let currentCategory = "all";
    let currentMaxPrice = "";
    let currentQuery = "";

    // DOM Elements
    const productGrid = document.getElementById("product-grid");
    const searchInput = document.getElementById("search-input");
    const searchBtn = document.getElementById("search-btn");
    const clearBtn = document.getElementById("clear-btn");
    const categoryPills = document.getElementById("category-pills");
    const priceLimitSelect = document.getElementById("price-limit");
    const resultsHeading = document.getElementById("results-heading");
    const resultsCount = document.getElementById("results-count");

    // Modal Elements
    const recModal = document.getElementById("rec-modal");
    const closeModal = document.getElementById("close-modal");
    const modalSubtitle = document.getElementById("modal-subtitle");
    const modalRecommendations = document.getElementById("modal-recommendations");

    // Chatbot Elements
    const chatToggleBtn = document.getElementById("chat-toggle-btn");
    const chatWindow = document.getElementById("chat-window");
    const chatCloseBtn = document.getElementById("chat-close-btn");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const promptChips = document.querySelectorAll(".prompt-chip");

    // 1. Initial Load: Fetch and render all products
    fetchProducts();

    // 2. Search & Filter Handlers
    searchBtn.addEventListener("click", () => {
        currentQuery = searchInput.value.trim();
        fetchProducts();
    });

    searchInput.addEventListener("keyup", (e) => {
        if (e.key === "Enter") {
            currentQuery = searchInput.value.trim();
            fetchProducts();
        }
        if (searchInput.value.length > 0) {
            clearBtn.style.display = "block";
        } else {
            clearBtn.style.display = "none";
        }
    });

    clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        currentQuery = "";
        clearBtn.style.display = "none";
        fetchProducts();
    });

    categoryPills.addEventListener("click", (e) => {
        if (e.target.classList.contains("pill")) {
            document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
            e.target.classList.add("active");
            currentCategory = e.target.dataset.category;
            fetchProducts();
        }
    });

    priceLimitSelect.addEventListener("change", (e) => {
        currentMaxPrice = e.target.value;
        fetchProducts();
    });

    // 3. API Fetch Function
    async function fetchProducts() {
        productGrid.innerHTML = `<div class="loading-spinner">Searching with AI vector models...</div>`;
        try {
            let url = `/api/search?q=${encodeURIComponent(currentQuery)}&category=${encodeURIComponent(currentCategory)}`;
            if (currentMaxPrice) {
                url += `&max_price=${currentMaxPrice}`;
            }

            const res = await fetch(url);
            const data = await res.json();

            renderProducts(data.results);
            updateHeaders(data.total_matches);
        } catch (err) {
            productGrid.innerHTML = `<div class="error-msg">Failed to load catalog: ${err.message}</div>`;
        }
    }

    function updateHeaders(total) {
        if (currentQuery) {
            resultsHeading.innerText = `Search: "${currentQuery}"`;
            resultsCount.innerText = `Found ${total} semantic match(es)`;
        } else if (currentCategory !== "all") {
            resultsHeading.innerText = currentCategory;
            resultsCount.innerText = `Showing ${total} items`;
        } else {
            resultsHeading.innerText = "Featured Products";
            resultsCount.innerText = `Showing all ${total} items`;
        }
    }

    function renderProducts(products) {
        if (!products || products.length === 0) {
            productGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <h3>No products found</h3>
                    <p style="color: #64748b; margin-top: 0.5rem;">Try relaxing your budget filter or searching for another term like 'laptop' or 'headphones'.</p>
                </div>
            `;
            return;
        }

        productGrid.innerHTML = products.map(p => `
            <div class="product-card">
                <div class="card-top">
                    <div>
                        <span class="category-tag">${p.category}</span>
                        ${p.relevance_score ? `<span class="relevance-badge">${p.relevance_score}% Match</span>` : ''}
                    </div>
                    <h4 class="product-title">${p.title}</h4>
                    <p class="product-desc">${p.description}</p>
                    <div class="product-tags">
                        ${p.tags.map(t => `<span class="tag-badge">#${t}</span>`).join('')}
                    </div>
                </div>
                <div class="card-bottom">
                    <div class="price-rating-row">
                        <span class="product-price">$${p.price.toFixed(2)}</span>
                        <span class="product-rating">⭐ ${p.rating} / 5</span>
                    </div>
                    <button class="recommend-btn" onclick="openRecommendations(${p.id}, '${p.title.replace(/'/g, "\\'")}')">
                        ✨ Find Similar (AI Recommender)
                    </button>
                </div>
            </div>
        `).join('');
    }

    // 4. Recommendations Modal Logic
    window.openRecommendations = async function(productId, title) {
        modalSubtitle.innerText = `Smart AI recommendations for: ${title}`;
        modalRecommendations.innerHTML = `<div class="loading-spinner">Calculating vector similarity...</div>`;
        recModal.style.display = "flex";

        try {
            const res = await fetch(`/api/recommend/${productId}`);
            const data = await res.json();
            const recs = data.recommendations;

            if (recs.length === 0) {
                modalRecommendations.innerHTML = `<p>No similar items found.</p>`;
                return;
            }

            modalRecommendations.innerHTML = recs.map(r => `
                <div class="rec-item">
                    <div>
                        <div class="rec-item-title">${r.title}</div>
                        <div class="rec-item-reason">${r.recommendation_reason}</div>
                    </div>
                    <div>
                        <div class="rec-item-price">$${r.price.toFixed(2)}</div>
                        <div class="rec-match-score">${r.similarity_percent}% Similarity</div>
                    </div>
                </div>
            `).join('');
        } catch (err) {
            modalRecommendations.innerHTML = `<p class="error-msg">Error: ${err.message}</p>`;
        }
    };

    closeModal.addEventListener("click", () => {
        recModal.style.display = "none";
    });

    window.addEventListener("click", (e) => {
        if (e.target === recModal) {
            recModal.style.display = "none";
        }
    });

    // 5. Chatbot Widget Logic
    const mongoModal = document.getElementById("mongo-modal");
    const closeMongoModal = document.getElementById("close-mongo-modal");
    const mongoLogsContent = document.getElementById("mongo-logs-content");
    const viewMongoLogsBtn = document.getElementById("view-mongo-logs-btn");

    if (viewMongoLogsBtn) {
        viewMongoLogsBtn.addEventListener("click", async () => {
            mongoModal.style.display = "flex";
            mongoLogsContent.innerHTML = `<div class="loading-spinner">Fetching live documents from MongoDB...</div>`;
            try {
                const res = await fetch("/api/chat/history?limit=15");
                const data = await res.json();
                if (!data.history || data.history.length === 0) {
                    mongoLogsContent.innerHTML = `<p style="padding: 1.5rem; text-align: center; color: #64748b;">No conversations recorded yet. Send a message in the chat to see documents appear here!</p>`;
                    return;
                }
                mongoLogsContent.innerHTML = data.history.map((log, idx) => `
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem; margin-bottom: 0.75rem; font-family: monospace; font-size: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem; color: #059669; font-weight: bold;">
                            <span>Document #${data.history.length - idx} (Storage: ${log.storage || 'MongoDB'})</span>
                            <span>${log.timestamp ? log.timestamp.split('T')[1].slice(0, 8) + ' UTC' : ''}</span>
                        </div>
                        <div style="margin-bottom: 0.3rem;"><strong>User:</strong> "${log.user_message}"</div>
                        <div style="color: #334155;"><strong>Bot:</strong> ${log.bot_reply.slice(0, 150)}...</div>
                    </div>
                `).join('');
            } catch (err) {
                mongoLogsContent.innerHTML = `<p style="color: #ef4444;">Failed to fetch MongoDB logs: ${err.message}</p>`;
            }
        });
    }

    if (closeMongoModal) {
        closeMongoModal.addEventListener("click", () => {
            mongoModal.style.display = "none";
        });
    }

    window.addEventListener("click", (e) => {
        if (e.target === mongoModal) {
            mongoModal.style.display = "none";
        }
    });

    chatToggleBtn.addEventListener("click", () => {
        if (chatWindow.style.display === "none") {
            chatWindow.style.display = "flex";
            chatInput.focus();
        } else {
            chatWindow.style.display = "none";
        }
    });

    chatCloseBtn.addEventListener("click", () => {
        chatWindow.style.display = "none";
    });

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;

        appendMessage("user", msg);
        chatInput.value = "";
        sendChatMessage(msg);
    });

    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.dataset.query;
            appendMessage("user", query);
            sendChatMessage(query);
        });
    });

    async function sendChatMessage(msg) {
        const loadingId = "bot-loading-" + Date.now();
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "message bot-message";
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = `<div class="message-bubble">Thinking... 🤖</div>`;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });
            const data = await res.json();

            const target = document.getElementById(loadingId);
            if (target) target.remove();

            appendMessage("bot", data.reply, data.products);
        } catch (err) {
            const target = document.getElementById(loadingId);
            if (target) target.remove();
            appendMessage("bot", `Sorry, I ran into an error: ${err.message}`);
        }
    }

    function appendMessage(sender, text, products = []) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender}-message`;
        let contentHtml = `<div class="message-bubble">${formatMarkdown(text)}`;
        
        if (products && products.length > 0) {
            contentHtml += `<div class="chat-product-list">`;
            products.forEach(p => {
                contentHtml += `
                    <div class="chat-product-item">
                        <div class="chat-prod-info">
                            <span class="chat-prod-title">${p.title}</span>
                            <span class="chat-prod-meta">$${p.price.toFixed(2)} • ⭐ ${p.rating}</span>
                        </div>
                        <button class="chat-view-btn" onclick="openRecommendations(${p.id}, '${p.title.replace(/'/g, "\\'")}')">Find Similar</button>
                    </div>
                `;
            });
            contentHtml += `</div>`;
        }
        
        contentHtml += `</div>`;
        msgDiv.innerHTML = contentHtml;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function formatMarkdown(text) {
        // Simple markdown parsing for bold and bullet points
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/•\s*(.*?)\n/g, '<li>$1</li>');
        return formatted;
    }
});
