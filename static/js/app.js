document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initAccountSetup();
    initScrape();
    initDMs();
    initHistory();
    
    // Poll status initially
    fetchStatus();
    setInterval(fetchStatus, 5000);
});

// --- Tab Navigation ---
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            // Remove active from all
            navItems.forEach(n => n.classList.remove("active"));
            tabContents.forEach(t => t.classList.remove("active"));
            
            // Add active to clicked
            item.classList.add("active");
            const targetId = item.getAttribute("data-target");
            document.getElementById(targetId).classList.add("active");
            
            if (targetId === 'tab-history') {
                fetchHistory();
            } else if (targetId === 'tab-dms') {
                fetchPendingDMs();
            }
        });
    });
}

// --- Global Status Polling ---
async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();
        
        // Instagram Status Update
        const igStatusEl = document.getElementById("ig-status");
        const igLaunchBtn = document.getElementById("btn-ig-launch");
        const igDisconnectBtn = document.getElementById("btn-ig-disconnect");
        
        if (data.ig_connected) {
            igStatusEl.innerHTML = `Status: <span class="status-connected">🟢 Session Saved (${data.ig_username})</span>`;
            igLaunchBtn.classList.add("hidden");
            igDisconnectBtn.classList.remove("hidden");
            document.getElementById("ig-error").classList.add("hidden");
        } else {
            igStatusEl.innerHTML = `Status: <span class="status-disconnected">🔴 No Session Found</span>`;
            igLaunchBtn.classList.remove("hidden");
            igDisconnectBtn.classList.add("hidden");
            
            if (data.ig_login_error && !data.ig_login_in_progress) {
                document.getElementById("ig-error").innerText = data.ig_login_error;
                document.getElementById("ig-error").classList.remove("hidden");
            } else {
                document.getElementById("ig-error").classList.add("hidden");
            }
            
            igLaunchBtn.disabled = data.ig_login_in_progress;
            igLaunchBtn.innerText = data.ig_login_in_progress
                ? "⏳ Waiting for Login..."
                : "🌐 Launch IG Login Window";
        }
        
        // Facebook Status Update
        const fbStatusEl = document.getElementById("fb-status");
        const fbDisconnectBtn = document.getElementById("btn-fb-disconnect");
        if (data.fb_connected) {
            fbStatusEl.innerHTML = `Status: <span class="status-connected">🟢 Session Saved</span>`;
            fbDisconnectBtn.classList.remove("hidden");
        } else {
            fbStatusEl.innerHTML = `Status: <span class="status-disconnected">🔴 No Session Found</span>`;
            fbDisconnectBtn.classList.add("hidden");
        }
        
    } catch (e) {
        console.error("Failed to fetch status", e);
    }
}

// --- Account Setup Logic ---
function initAccountSetup() {
    // Instagram — Launch browser window (same as Facebook)
    document.getElementById("btn-ig-launch").addEventListener("click", async () => {
        const btn = document.getElementById("btn-ig-launch");
        btn.disabled = true;
        btn.innerText = "⏳ Waiting for Login...";
        
        const res = await fetch("/api/ig/launch_login", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            alert("Instagram session saved!");
        } else {
            alert("Instagram login failed: " + data.error);
        }
        
        btn.disabled = false;
        btn.innerText = "🌐 Launch IG Login Window";
        fetchStatus();
    });
    
    // Instagram Disconnect
    document.getElementById("btn-ig-disconnect").addEventListener("click", async () => {
        await fetch("/api/ig/disconnect", { method: "POST" });
        fetchStatus();
    });
    
    // Facebook Logic
    document.getElementById("btn-fb-launch").addEventListener("click", async () => {
        const btn = document.getElementById("btn-fb-launch");
        btn.disabled = true;
        btn.innerText = "⏳ Waiting for Login...";
        
        const res = await fetch("/api/fb/launch", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            alert("Facebook session saved!");
        } else {
            alert("Facebook login failed: " + data.error);
        }
        
        btn.disabled = false;
        btn.innerText = "🌐 Launch FB Login Window";
        fetchStatus();
    });
    
    document.getElementById("btn-fb-test").addEventListener("click", async () => {
        const res = await fetch("/api/fb/test", { method: "POST" });
        const data = await res.json();
        alert(data.message || data.error);
        fetchStatus();
    });
    
    document.getElementById("btn-fb-disconnect").addEventListener("click", async () => {
        await fetch("/api/fb/disconnect", { method: "POST" });
        fetchStatus();
    });
}

// --- Scrape Logic ---
let scrapePollInterval = null;

function initScrape() {
    document.getElementById("btn-start-scrape").addEventListener("click", async () => {
        const domain = document.getElementById("scrape-domain").value;
        const platform = document.querySelector('input[name="scrape-platform"]:checked').value;
        const posts_count = parseInt(document.getElementById("scrape-posts").value);
        const max_comments = parseInt(document.getElementById("scrape-comments").value);
        const targets = document.getElementById("scrape-targets").value;
        
        if (!targets.trim()) return alert("Please enter target accounts.");
        
        document.getElementById("btn-start-scrape").disabled = true;
        document.getElementById("scrape-results-container").classList.add("hidden");
        
        const res = await fetch("/api/scrape/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ domain, platform, posts_count, max_comments, targets })
        });
        const data = await res.json();
        
        if (!data.success) {
            alert(data.error);
            document.getElementById("btn-start-scrape").disabled = false;
            return;
        }
        
        // Start polling logs
        if (scrapePollInterval) clearInterval(scrapePollInterval);
        scrapePollInterval = setInterval(pollScrapeLogs, 2000);
    });
    
    document.getElementById("btn-clear-scrape-logs").addEventListener("click", () => {
        document.getElementById("scrape-console").innerText = "";
    });
    
    document.getElementById("btn-save-scraped").addEventListener("click", async () => {
        const domain = document.getElementById("scrape-domain").value;
        const res = await fetch("/api/scrape/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ domain })
        });
        const data = await res.json();
        if (data.success) {
            alert(`Saved ${data.saved_count} leads to database!`);
        }
    });
    
    document.getElementById("btn-export-scraped").addEventListener("click", async () => {
        const domain = document.getElementById("scrape-domain").value;
        const res = await fetch("/api/scrape/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ domain })
        });
        const data = await res.json();
        if (data.success) {
            alert(`Exported to: ${data.filepath}`);
        }
    });
}

async function pollScrapeLogs() {
    const res = await fetch("/api/scrape/logs");
    const data = await res.json();
    
    const consoleEl = document.getElementById("scrape-console");
    consoleEl.innerText = data.logs.join("\n");
    consoleEl.scrollTop = consoleEl.scrollHeight;
    
    if (!data.running) {
        clearInterval(scrapePollInterval);
        document.getElementById("btn-start-scrape").disabled = false;
        
        if (data.results && data.results.length > 0) {
            renderScrapeResults(data.results);
        }
    }
}

function getScoreClass(score) {
    if (score >= 80) return "score-high";
    if (score >= 50) return "score-medium";
    if (score >= 5) return "score-low";
    return "";
}

function renderScrapeResults(results) {
    document.getElementById("scrape-count").innerText = results.length;
    const tbody = document.querySelector("#scrape-table tbody");
    tbody.innerHTML = "";
    
    results.forEach(row => {
        const tr = document.createElement("tr");
        tr.className = getScoreClass(row.Score);
        tr.innerHTML = `
            <td><a href="${row['Profile URL']}" target="_blank" style="color:inherit">${row.Username}</a></td>
            <td>${row.Platform}</td>
            <td>${row['Source Account']}</td>
            <td>${row.Comment}</td>
            <td>${row.Score}</td>
        `;
        tbody.appendChild(tr);
    });
    
    document.getElementById("scrape-results-container").classList.remove("hidden");
}

// --- DM Logic ---
let dmPollInterval = null;

function initDMs() {
    document.getElementById("dm-select-all").addEventListener("change", (e) => {
        const checked = e.target.checked;
        document.querySelectorAll(".dm-checkbox").forEach(cb => cb.checked = checked);
    });
    
    document.getElementById("btn-start-dms").addEventListener("click", async () => {
        const message = document.getElementById("dm-message").value;
        if (!message) return alert("Please compose a message first.");
        
        const target_ids = [];
        document.querySelectorAll(".dm-checkbox:checked").forEach(cb => {
            target_ids.push(parseInt(cb.value));
        });
        
        if (target_ids.length === 0) return alert("Select at least one prospect.");
        
        document.getElementById("btn-start-dms").disabled = true;
        
        const res = await fetch("/api/dms/send", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, target_ids })
        });
        const data = await res.json();
        
        if (!data.success) {
            alert(data.error);
            document.getElementById("btn-start-dms").disabled = false;
            return;
        }
        
        if (dmPollInterval) clearInterval(dmPollInterval);
        dmPollInterval = setInterval(pollDMLogs, 2000);
    });
    
    document.getElementById("btn-clear-dm-logs").addEventListener("click", () => {
        document.getElementById("dm-console").innerText = "";
    });
}

async function fetchPendingDMs() {
    const res = await fetch("/api/dms/pending");
    const data = await res.json();
    const tbody = document.querySelector("#pending-dms-table tbody");
    tbody.innerHTML = "";
    
    if (data.leads.length === 0) {
        tbody.innerHTML = "<tr><td colspan='6' style='text-align:center'>No pending leads found.</td></tr>";
        return;
    }
    
    data.leads.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="checkbox" class="dm-checkbox" value="${row.id}" checked></td>
            <td>${row.id}</td>
            <td><a href="${row.commenter_profile_url}" target="_blank" style="color:inherit">${row.commenter_username}</a></td>
            <td>${row.platform}</td>
            <td>${row.domain}</td>
            <td>${row.interest_score}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function pollDMLogs() {
    const res = await fetch("/api/dms/logs");
    const data = await res.json();
    
    const consoleEl = document.getElementById("dm-console");
    consoleEl.innerText = data.logs.join("\n");
    consoleEl.scrollTop = consoleEl.scrollHeight;
    
    if (!data.running) {
        clearInterval(dmPollInterval);
        document.getElementById("btn-start-dms").disabled = false;
        fetchPendingDMs(); // refresh list
    }
}

// --- Lead History Logic ---
let currentHistoryLeads = [];

function initHistory() {
    const filters = ["hist-filter-domain", "hist-filter-platform", "hist-filter-dm"];
    filters.forEach(id => {
        document.getElementById(id).addEventListener("change", fetchHistory);
    });
    
    document.getElementById("btn-export-history").addEventListener("click", async () => {
        const domain = document.getElementById("hist-filter-domain").value;
        const res = await fetch("/api/history/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ leads: currentHistoryLeads, domain })
        });
        const data = await res.json();
        if (data.success) {
            alert(`History exported to: ${data.filepath}`);
        }
    });
    
    document.getElementById("btn-clear-history").addEventListener("click", async () => {
        if (!confirm("Are you sure you want to permanently delete all real leads?")) return;
        const res = await fetch("/api/history/clear", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            fetchHistory();
        }
    });
}

async function fetchHistory() {
    const domain = document.getElementById("hist-filter-domain").value;
    const platform = document.getElementById("hist-filter-platform").value;
    const dm_sent = document.getElementById("hist-filter-dm").value;
    
    const qs = `?domain=${encodeURIComponent(domain)}&platform=${encodeURIComponent(platform)}&dm_sent=${encodeURIComponent(dm_sent)}`;
    const res = await fetch("/api/history" + qs);
    const data = await res.json();
    
    currentHistoryLeads = data.leads;
    
    const tbody = document.querySelector("#history-table tbody");
    tbody.innerHTML = "";
    
    if (data.leads.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7' style='text-align:center'>No history found.</td></tr>";
        return;
    }
    
    data.leads.forEach(row => {
        const tr = document.createElement("tr");
        tr.className = getScoreClass(row.interest_score);
        tr.innerHTML = `
            <td>${row.id}</td>
            <td><a href="${row.commenter_profile_url}" target="_blank" style="color:inherit">${row.commenter_username}</a></td>
            <td>${row.platform}</td>
            <td>${row.domain}</td>
            <td>${row.interest_score}</td>
            <td>${row.dm_sent === 1 ? '✅ Yes' : '❌ No'}</td>
            <td>${row.scraped_at}</td>
        `;
        tbody.appendChild(tr);
    });
}
