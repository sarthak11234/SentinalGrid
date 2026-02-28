const API_BASE = "http://localhost:8000";

// ── DOM Elements ──
const themeToggle = document.getElementById("theme-toggle");
const themeIcon = document.getElementById("theme-icon");
const themeText = document.getElementById("theme-text");
const navItems = document.querySelectorAll(".nav-item");
const pages = document.querySelectorAll(".page");
const apiStatusText = document.getElementById("api-status-text");
const apiStatusDot = document.querySelector(".status-dot");

// Form Elements
const campaignForm = document.getElementById("campaign-form");
const dataFileInput = document.getElementById("data-file");
const fileDropArea = document.getElementById("file-drop-area");
const btnCreate = document.getElementById("btn-create-campaign");
const createOrAlert = document.getElementById("create-notification");

// Dashboard Elements
const dashCampaignSelect = document.getElementById("campaign-selector");
const reviewCampaignSelect = document.getElementById("review-campaign-selector");
const btnRefreshDash = document.getElementById("btn-refresh-dash");
const btnLaunchCampaign = document.getElementById("btn-launch-campaign");
const dashEmptyState = document.getElementById("dashboard-empty-state");
const dashContent = document.getElementById("dashboard-content");

// ── Initialization ──
document.addEventListener("DOMContentLoaded", () => {
    checkBackendHealth();
    loadCampaigns();
    
    // Theme toggle from localStorage
    const savedTheme = localStorage.getItem("sg_theme") || "light";
    setTheme(savedTheme);
});

// ── Navigation ──
navItems.forEach(item => {
    item.addEventListener("click", () => {
        // Update active nav
        navItems.forEach(nav => nav.classList.remove("active"));
        item.classList.add("active");

        // Update active page
        const targetId = item.getAttribute("data-target");
        pages.forEach(page => page.classList.remove("active"));
        document.getElementById(targetId).classList.add("active");

        // Refresh data on page change
        if (targetId === "page-dashboard" || targetId === "page-review") {
            loadCampaigns();
        }
    });
});

// ── Theme Toggle ──
function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('sg_theme', theme);
    if (theme === 'dark') {
        themeIcon.textContent = 'light_mode';
        themeText.textContent = 'Light Mode';
    } else {
        themeIcon.textContent = 'dark_mode';
        themeText.textContent = 'Dark Mode';
    }
}

themeToggle.addEventListener("click", () => {
    const currentTheme = document.body.getAttribute('data-theme') || 'light';
    setTheme(currentTheme === 'light' ? 'dark' : 'light');
});


// ── Backend Health ──
async function checkBackendHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            apiStatusDot.className = "status-dot online";
            apiStatusText.textContent = "Backend Connected";
        } else {
            apiStatusDot.className = "status-dot offline";
            apiStatusText.textContent = "Backend Error";
        }
    } catch (e) {
        apiStatusDot.className = "status-dot offline";
        apiStatusText.textContent = "Backend Offline";
    }
}


// ── File Upload UX ──
fileDropArea.addEventListener("click", () => dataFileInput.click());
dataFileInput.addEventListener("change", (e) => updateFileDisplay(e.target.files[0]));

fileDropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    fileDropArea.classList.add("dragover");
});
fileDropArea.addEventListener("dragleave", () => fileDropArea.classList.remove("dragover"));
fileDropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    fileDropArea.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        dataFileInput.files = e.dataTransfer.files;
        updateFileDisplay(e.dataTransfer.files[0]);
    }
});

function updateFileDisplay(file) {
    const msg = fileDropArea.querySelector(".file-message");
    if (file) {
        msg.innerHTML = `<strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
        fileDropArea.style.borderColor = "var(--success)";
    } else {
        msg.innerHTML = `Drag & drop your file here or click to browse`;
        fileDropArea.style.borderColor = "var(--border)";
    }
}


// ── Create Campaign ──
campaignForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("campaign-name").value;
    const prompt = document.getElementById("master-prompt").value;
    const file = dataFileInput.files[0];

    if (!file) return;

    // Simulate UX
    btnCreate.disabled = true;
    btnCreate.innerHTML = `<span class="material-symbols-rounded" style="animation: spin 1s linear infinite;">progress_activity</span> Creating...`;
    
    const formData = new FormData();
    formData.append("name", name);
    formData.append("master_prompt", prompt);
    formData.append("user_email", "admin@sentinalgrid.com"); // Hardcoded for this demo
    formData.append("file", file);

    try {
        const res = await fetch(`${API_BASE}/campaigns`, { method: "POST", body: formData });
        const data = await res.json();

        if (res.ok) {
            showNotification(`Campaign "${data.name}" successfully created!`, "success");
            campaignForm.reset();
            updateFileDisplay(null);
            loadCampaigns(); // refresh dropdowns
        } else {
            showNotification(data.detail || "Failed to create campaign.", "error");
        }
    } catch (err) {
        showNotification("Connection error. Ensure backend is running.", "error");
    } finally {
        btnCreate.disabled = false;
        btnCreate.innerHTML = `<span class="material-symbols-rounded">rocket_launch</span> Create Campaign`;
    }
});

function showNotification(msg, type) {
    createOrAlert.textContent = msg;
    createOrAlert.className = `notification ${type}`;
    createOrAlert.classList.remove("hidden");
    setTimeout(() => createOrAlert.classList.add("hidden"), 5000);
}


// ── Load Campaigns Dropdown ──
async function loadCampaigns() {
    try {
        const res = await fetch(`${API_BASE}/campaigns`);
        if (!res.ok) return;
        const data = await res.json();
        const campaigns = data.campaigns || [];
        
        const optionsHtml = campaigns.length 
            ? campaigns.map(c => `<option value="${c.id}">${c.name} (ID: ${c.id})</option>`).join("")
            : `<option value="" disabled selected>No campaigns available</option>`;

        dashCampaignSelect.innerHTML = `<option value="" disabled selected>Select a campaign...</option>` + optionsHtml;
        reviewCampaignSelect.innerHTML = `<option value="" disabled selected>Select a campaign...</option>` + optionsHtml;

    } catch (e) {
        console.error("Failed to load campaigns", e);
    }
}


// ── Dashboard Interaction ──
dashCampaignSelect.addEventListener("change", fetchDashboardData);
btnRefreshDash.addEventListener("click", fetchDashboardData);

async function fetchDashboardData() {
    const cid = dashCampaignSelect.value;
    if (!cid) return;

    btnRefreshDash.innerHTML = `<span class="material-symbols-rounded" style="animation: spin 1s linear infinite;">sync</span>`;

    try {
        const res = await fetch(`${API_BASE}/campaigns/${cid}`);
        const data = await res.json();

        dashEmptyState.classList.add("hidden");
        dashContent.classList.remove("hidden");

        // Update Stats
        const stats = data.stats;
        document.getElementById("stat-total").textContent = stats.total || 0;
        document.getElementById("stat-pending").textContent = stats.pending || 0;
        document.getElementById("stat-sent").textContent = stats.sent || 0;
        document.getElementById("stat-replied").textContent = stats.replied || 0;
        document.getElementById("stat-review").textContent = stats.review || 0;

        // Button States
        const status = data.campaign.status;
        if (status === "draft" || status === "completed") {
            btnLaunchCampaign.disabled = false;
            btnLaunchCampaign.textContent = "Launch Campaign";
            btnLaunchCampaign.onclick = () => launchCampaign(cid);
        } else {
            btnLaunchCampaign.disabled = true;
            btnLaunchCampaign.textContent = "Running...";
        }

        // Render Table
        const tbody = document.querySelector("#data-rows-table tbody");
        tbody.innerHTML = (data.rows || []).map(r => `
            <tr>
                <td>${r.row_index}</td>
                <td>${r.channel === 'whatsapp' ? '📱 WhatsApp' : '📧 Email'}</td>
                <td>${r.contact_phone || r.contact_email || '—'}</td>
                <td><span class="status-badge status-${r.message_status}">${r.message_status}</span></td>
                <td style="color: var(--text-soft); font-size: 0.85rem;">
                    ${r.outbound_message ? r.outbound_message.substring(0, 50) + '...' : '—'}
                </td>
            </tr>
        `).join("");

    } catch (e) {
        console.error(e);
    } finally {
        btnRefreshDash.innerHTML = `<span class="material-symbols-rounded">refresh</span> Refresh`;
    }
}

async function launchCampaign(cid) {
    btnLaunchCampaign.disabled = true;
    btnLaunchCampaign.textContent = "Launching...";
    try {
        await fetch(`${API_BASE}/campaigns/${cid}/launch`, { method: "POST" });
        setTimeout(fetchDashboardData, 1000); // refresh after a sec
    } catch (e) {
        console.error(e);
    }
}
