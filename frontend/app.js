const API_BASE = "http://127.0.0.1:8000/api";

const els = {
    caseList: document.getElementById('case-list'),
    emptyState: document.getElementById('empty-state'),
    caseDetail: document.getElementById('case-detail'),
    caseTitle: document.getElementById('case-title'),
    handoffContent: document.getElementById('handoff-content'),
    clipContent: document.getElementById('clip-content'),
    screenshotImg: document.getElementById('screenshot-img'),

    btnCopyHandoff: document.getElementById('btn-copy-handoff'),
    btnOpenFolder: document.getElementById('btn-open-folder'),
    btnDeleteCase: document.getElementById('btn-delete-case'),

    // Help
    btnHelp: document.getElementById('btn-help'),
    btnCloseHelp: document.getElementById('btn-close-help'),
    helpModal: document.getElementById('help-modal'),

    // Manual Trigger
    btnManualCapture: document.getElementById('btn-manual-capture')
};

// Help Modal Logic
els.btnHelp.onclick = () => els.helpModal.classList.remove('hidden');
els.btnCloseHelp.onclick = () => els.helpModal.classList.add('hidden');
// Close on click outside
els.helpModal.onclick = (e) => {
    if (e.target === els.helpModal) els.helpModal.classList.add('hidden');
    if (e.target === els.helpModal) els.helpModal.classList.add('hidden');
}

// Manual Capture Logic
if (els.btnManualCapture) {
    els.btnManualCapture.onclick = async () => {
        try {
            const originalText = "📷 Capture";
            // Countdown
            for (let i = 3; i > 0; i--) {
                els.btnManualCapture.textContent = `Wait ${i}s...`;
                await new Promise(r => setTimeout(r, 1000));
            }

            els.btnManualCapture.textContent = "Capturing...";
            await fetch(`${API_BASE}/debug/trigger`);

            // Wait a sec for FS
            setTimeout(() => {
                fetchCases();
                els.btnManualCapture.textContent = originalText;
            }, 1000);
        } catch (e) {
            console.error("Manual capture failed", e);
            alert("Capture failed");
            els.btnManualCapture.textContent = "Error";
        }
    };
}

let currentCase = null;

// Event Listeners
els.btnCopyHandoff.onclick = async () => {
    try {
        const originalText = els.btnCopyHandoff.textContent;
        els.btnCopyHandoff.textContent = "Generating...";

        // 1. Force Generate (and server-side copy)
        await fetch(`${API_BASE}/debug/handoff`);

        // 2. Refresh UI to get new content
        if (currentCase) {
            const res = await fetch(`${API_BASE}/case/${currentCase.name}/assets`);
            const assets = await res.json();
            els.handoffContent.value = assets.handoff_content || '';
        }

        // 3. Client-side copy (redundant but safe)
        if (els.handoffContent.value) {
            await navigator.clipboard.writeText(els.handoffContent.value);
            els.btnCopyHandoff.textContent = "Copied!";
        } else {
            els.btnCopyHandoff.textContent = "Empty!";
        }

        setTimeout(() => els.btnCopyHandoff.textContent = originalText, 2000);
    } catch (err) {
        console.error('Failed to copy!', err);
        els.btnCopyHandoff.textContent = "Error";
    }
};

els.btnOpenFolder.onclick = () => {
    // There is no standard web API to open a local folder from browser for security.
    // However, since this is a local app, we can make an API call to the backend to open it.
    if (currentCase) {
        // User requested to open 'input' folder specifically
        const targetPath = currentCase.path + "\\input";
        fetch(`${API_BASE}/open_folder?path=${encodeURIComponent(targetPath)}`);
    }
};

els.btnDeleteCase.onclick = async () => {
    if (!currentCase) return;
    if (!confirm(`案件 "${currentCase.name}" を削除しますか？\nこの操作は元に戻せません。`)) return;

    try {
        const res = await fetch(`${API_BASE}/cases/${currentCase.name}`, { method: 'DELETE' });
        if (res.ok) {
            currentCase = null;
            els.caseDetail.classList.add('hidden');
            els.emptyState.classList.remove('hidden');
            fetchCases(); // Refresh list
        } else {
            alert("削除に失敗しました");
        }
    } catch (e) {
        console.error("Delete failed", e);
        alert("エラーが発生しました");
    }
};

async function fetchCases() {
    try {
        const res = await fetch(`${API_BASE}/cases`);
        const cases = await res.json();
        renderCaseList(cases);
    } catch (e) {
        console.error("Failed to fetch cases", e);
    }
}

function renderCaseList(cases) {
    els.caseList.innerHTML = '';
    cases.forEach(c => {
        const div = document.createElement('div');
        div.className = `case-item ${currentCase && currentCase.name === c.name ? 'active' : ''}`;
        div.onclick = () => selectCase(c);

        const time = c.created_at.replace(/^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})$/, "$2/$3 $4:$5");
        div.innerHTML = `
            <span class="timestamp">${time}</span>
            <span class="name">${c.name}</span>
        `;
        els.caseList.appendChild(div);
    });
}


async function selectCase(c) {
    currentCase = c;
    els.emptyState.classList.add('hidden');
    els.caseDetail.classList.remove('hidden');
    els.caseTitle.textContent = c.name;

    // Highlight in list
    Array.from(els.caseList.children).forEach(child => {
        child.classList.toggle('active', child.querySelector('.name').textContent === c.name);
    });

    // Fetch Assets
    try {
        const res = await fetch(`${API_BASE}/case/${c.name}/assets`);
        const assets = await res.json();

        els.screenshotImg.src = assets.screenshot_url || '';
        els.handoffContent.value = assets.handoff_content || '';
        els.clipContent.textContent = assets.clip_content || '(No clipboard content)';

    } catch (e) {
        console.error("Failed to load assets", e);
    }
}


// Polling for new cases
setInterval(fetchCases, 5000);
fetchCases();
