// OmniPost Studio - Frontend App Logic
let currentQueue = [];
let activeDays = ["Mon", "Wed", "Fri"];
let currentFreq = 3;
let currentEditingId = null;
let currentAIResults = null;
let uploadPollInterval = null;

const DAY_PRESETS = {
  1: ["Sun"],
  2: ["Tue", "Fri"],
  3: ["Mon", "Wed", "Fri"],
  4: ["Mon", "Wed", "Fri", "Sun"],
  5: ["Mon", "Tue", "Wed", "Thu", "Fri"],
  6: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  7: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  // Set default start date to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const dateInput = document.getElementById("cadence-start-date");
  if (dateInput) {
    dateInput.value = tomorrow.toISOString().split("T")[0];
  }

  loadQueue();
  loadLicenseStatus();
  setupDropZone();
  setupGlobalPlatformFilters();
});

// Load Queue
async function loadQueue() {
  try {
    const res = await fetch("/api/queue");
    const data = await res.json();
    currentQueue = data.queue || [];
    renderQueue();
    updateStats();
  } catch (err) {
    console.error("Failed to load queue:", err);
  }
}

// Update Top Bar Stats
function updateStats() {
  document.getElementById("stat-queue-count").textContent = currentQueue.length;
  const scheduledCount = currentQueue.filter(x => x.status === "scheduled" || x.scheduled_time_iso).length;
  document.getElementById("stat-scheduled-count").textContent = scheduledCount;
  document.getElementById("queue-badge-count").textContent = `${currentQueue.length} video${currentQueue.length === 1 ? '' : 's'}`;
}

// Render Queue List
function renderQueue() {
  const container = document.getElementById("queue-list");
  if (!container) return;

  if (currentQueue.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; color: var(--text-dim);">
        <p style="font-size: 15px; margin-bottom: 8px;">📭 No videos in queue yet.</p>
        <p style="font-size: 12.5px;">Drop your rendered video files above or click "➕ Add Video" to get started.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = currentQueue.map(item => {
    const thumbHtml = item.thumbnail_path
      ? `<img src="/api/browse/image_preview?path=${encodeURIComponent(item.thumbnail_path)}" onerror="this.parentElement.innerHTML='🎬'">`
      : `🎬`;

    const platformPills = `
      <span class="platform-pill selected">🔴 YouTube</span>
      <span class="platform-pill selected">⚡ Shorts Enabled</span>
      <span class="platform-pill ${item.thumbnail_path ? 'selected' : ''}">${item.thumbnail_path ? '🖼️ Custom Thumbnail' : '📷 Auto Frame'}</span>
    `;

    return `
      <div class="queue-card" id="card-${item.id}">
        <!-- Thumbnail -->
        <div class="video-thumb">
          ${thumbHtml}
          <span class="badge-res">HD</span>
        </div>

        <!-- Details -->
        <div class="card-details">
          <div class="card-title">
            <span>${item.title}</span>
            <button class="btn btn-secondary btn-sm" onclick="openAIModalForVideo('${item.id}', '${escapeAttr(item.title)}')">
              <span>✨ AI SEO</span>
            </button>
          </div>
          <div class="card-meta">
            <span>📁 ${item.file_name}</span>
            <span>💾 ${item.file_size_mb} MB</span>
          </div>
          <div class="platform-pills">
            ${platformPills}
          </div>
        </div>

        <!-- Schedule -->
        <div class="card-schedule">
          <span class="schedule-pill">${item.scheduled_time_human || 'Not scheduled'}</span>
          <span class="status-badge ${item.status || 'queued'}">${(item.status || 'queued').toUpperCase()}</span>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <button class="btn btn-secondary btn-sm" onclick="openEditModal('${item.id}')">✏️ Edit</button>
          <button class="btn btn-secondary btn-sm" style="color: var(--accent-danger);" onclick="deleteVideo('${item.id}')">🗑️</button>
        </div>

        <!-- Progress Bar (Active when uploading) -->
        ${item.status === 'uploading' ? `
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${item.upload_progress || 0}%"></div>
          </div>
        ` : ''}
      </div>
    `;
  }).join("");
}

function escapeAttr(str) {
  return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// Frequency and Day Selectors
function setFrequency(freq) {
  currentFreq = freq;
  document.querySelectorAll(".freq-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.freq == freq);
  });

  if (freq !== "custom" && DAY_PRESETS[freq]) {
    activeDays = [...DAY_PRESETS[freq]];
    updateDayChipsUI();
  }
}

function toggleDay(day) {
  if (activeDays.includes(day)) {
    if (activeDays.length > 1) {
      activeDays = activeDays.filter(d => d !== day);
    }
  } else {
    activeDays.push(day);
  }
  updateDayChipsUI();
  // Mark as custom frequency
  currentFreq = "custom";
  document.querySelectorAll(".freq-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.freq === "custom");
  });
}

function updateDayChipsUI() {
  document.querySelectorAll(".day-chip").forEach(chip => {
    const day = chip.dataset.day;
    chip.classList.toggle("active", activeDays.includes(day));
  });
}

function setTimePreset(time) {
  document.getElementById("cadence-time").value = time;
}

function updateJitter(val) {
  document.getElementById("jitter-val").textContent = `± ${val} mins`;
}

// Apply Cadence Engine to Queue
async function applyCadenceToQueue() {
  if (currentQueue.length === 0) {
    alert("Please add at least 1 video to the queue first.");
    return;
  }

  const preferredTime = document.getElementById("cadence-time").value || "18:30";
  const startDate = document.getElementById("cadence-start-date").value || null;
  const jitter = parseInt(document.getElementById("jitter-slider").value, 10) || 0;

  try {
    const res = await fetch("/api/cadence/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        frequency_per_week: typeof currentFreq === "number" ? currentFreq : activeDays.length,
        active_days: activeDays,
        preferred_time: preferredTime,
        start_date: startDate,
        jitter_minutes: jitter
      })
    });
    const data = await res.json();
    if (data.success) {
      currentQueue = data.queue;
      renderQueue();
      updateStats();
      alert(`Success! Scheduled ${data.slots.length} video(s) smoothly across your upcoming dates.`);
    }
  } catch (err) {
    console.error("Error applying cadence:", err);
  }
}

// Browse & Add Video
async function browseAndAddVideo() {
  try {
    const res = await fetch("/api/browse/video");
    const data = await res.json();
    if (data.file_path) {
      await addVideoToQueue(data.file_path);
    }
  } catch (err) {
    console.error("Browse failed:", err);
  }
}

async function addVideoToQueue(filePath) {
  try {
    const res = await fetch("/api/queue/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: filePath })
    });
    const data = await res.json();
    if (data.success) {
      currentQueue.push(data.item);
      renderQueue();
      updateStats();
    }
  } catch (err) {
    console.error("Failed to add video:", err);
  }
}

// Drag & Drop Setup
function setupDropZone() {
  const zone = document.getElementById("drop-zone");
  if (!zone) return;

  ["dragenter", "dragover"].forEach(name => {
    zone.addEventListener(name, (e) => {
      e.preventDefault();
      zone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    zone.addEventListener(name, (e) => {
      e.preventDefault();
      zone.classList.remove("dragover");
    });
  });

  zone.addEventListener("drop", async (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      for (let i = 0; i < files.length; i++) {
        // In webview or browser with local access
        const file = files[i];
        if (file.path) {
          await addVideoToQueue(file.path);
        } else {
          // If in standalone browser without absolute path, trigger native browse
          browseAndAddVideo();
          break;
        }
      }
    }
  });
}

// Toggle Target Platform for an item
async function toggleItemPlatform(itemId, platformId) {
  const item = currentQueue.find(x => x.id === itemId);
  if (!item) return;

  let targets = item.target_platforms || [];
  if (targets.includes(platformId)) {
    targets = targets.filter(p => p !== platformId);
  } else {
    targets.push(platformId);
  }

  item.target_platforms = targets;
  renderQueue();

  await fetch("/api/queue/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: itemId, target_platforms: targets })
  });
}

// Global Platform Pills
function setupGlobalPlatformFilters() {
  document.querySelectorAll("#global-platforms .platform-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      pill.classList.toggle("selected");
    });
  });
}

// Delete video from queue
async function deleteVideo(itemId) {
  if (!confirm("Remove this video from the schedule queue?")) return;
  try {
    const res = await fetch("/api/queue/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: itemId })
    });
    const data = await res.json();
    if (data.success) {
      currentQueue = currentQueue.filter(x => x.id !== itemId);
      renderQueue();
      updateStats();
    }
  } catch (err) {
    console.error("Delete failed:", err);
  }
}

// Clear Queue
async function clearEntireQueue() {
  if (currentQueue.length === 0) return;
  if (!confirm("Clear all videos from the queue?")) return;
  await fetch("/api/queue/clear", { method: "POST" });
  currentQueue = [];
  renderQueue();
  updateStats();
}

// Edit Modal
function openEditModal(itemId) {
  const item = currentQueue.find(x => x.id === itemId);
  if (!item) return;

  currentEditingId = itemId;
  document.getElementById("edit-modal-title").textContent = `Edit: ${item.file_name}`;
  document.getElementById("edit-title").value = item.title || "";
  document.getElementById("edit-description").value = item.description || "";
  document.getElementById("edit-tags").value = (item.tags || []).join(", ");
  document.getElementById("edit-thumbnail").value = item.thumbnail_path || "";

  document.getElementById("edit-modal").style.display = "flex";
}

function closeEditModal() {
  document.getElementById("edit-modal").style.display = "none";
  currentEditingId = null;
}

async function browseThumbnailForEdit() {
  try {
    const res = await fetch("/api/browse/thumbnail");
    const data = await res.json();
    if (data.file_path) {
      document.getElementById("edit-thumbnail").value = data.file_path;
    }
  } catch (err) {
    console.error("Browse thumbnail failed:", err);
  }
}

async function saveEditModal() {
  if (!currentEditingId) return;

  const title = document.getElementById("edit-title").value;
  const description = document.getElementById("edit-description").value;
  const tagsStr = document.getElementById("edit-tags").value;
  const thumbnail_path = document.getElementById("edit-thumbnail").value;

  const tags = tagsStr.split(",").map(t => t.trim()).filter(Boolean);

  try {
    const res = await fetch("/api/queue/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: currentEditingId,
        title,
        description,
        tags,
        thumbnail_path
      })
    });
    const data = await res.json();
    if (data.success) {
      const idx = currentQueue.findIndex(x => x.id === currentEditingId);
      if (idx !== -1) {
        currentQueue[idx] = data.item;
        renderQueue();
      }
      closeEditModal();
    }
  } catch (err) {
    console.error("Save edit failed:", err);
  }
}

// AI Modal
function openAIModalForVideo(itemId, initialTitle) {
  currentEditingId = itemId;
  document.getElementById("ai-topic").value = initialTitle;
  document.getElementById("ai-results").style.display = "none";
  document.getElementById("ai-modal").style.display = "flex";
}

function closeAIModal() {
  document.getElementById("ai-modal").style.display = "none";
}

async function generateAIMetadata() {
  const topic = document.getElementById("ai-topic").value;
  const language = document.getElementById("ai-language").value;

  if (!topic) {
    alert("Please enter a topic or title.");
    return;
  }

  try {
    const res = await fetch("/api/ai/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, language })
    });
    const data = await res.json();
    currentAIResults = data.metadata;

    document.getElementById("ai-yt-title").textContent = currentAIResults.youtube.title;
    document.getElementById("ai-yt-desc").textContent = currentAIResults.youtube.description;
    document.getElementById("ai-ig-caption").textContent = currentAIResults.instagram.caption;

    document.getElementById("ai-results").style.display = "flex";
  } catch (err) {
    console.error("AI Generation error:", err);
  }
}

async function applyAIToCurrentVideo() {
  if (!currentEditingId || !currentAIResults) return;

  const updates = {
    id: currentEditingId,
    title: currentAIResults.youtube.title,
    description: currentAIResults.youtube.description,
    tags: currentAIResults.suggested_tags
  };

  await fetch("/api/queue/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates)
  });

  const idx = currentQueue.findIndex(x => x.id === currentEditingId);
  if (idx !== -1) {
    Object.assign(currentQueue[idx], updates);
    renderQueue();
  }

  closeAIModal();
  alert("✨ AI Title, Description, and Tags applied to this video!");
}

// Accounts Modal
async function openAccountsModal() {
  const list = document.getElementById("platform-settings-list");
  list.innerHTML = `<p style="color: var(--text-muted);">Loading platform statuses...</p>`;
  document.getElementById("accounts-modal").style.display = "flex";

  try {
    const res = await fetch("/api/platforms");
    const data = await res.json();
    const platforms = data.platforms || [];

    list.innerHTML = platforms.map(p => {
      const isOk = p.is_configured;
      const btnText = isOk ? '✓ Connected (Change)' : (p.id === 'youtube' ? '🔴 Sign in with Google' : 'Connect Channel');
      const btnClass = isOk ? 'btn-secondary' : (p.id === 'youtube' ? 'btn-primary' : 'btn-secondary');
      const statusText = isOk 
        ? (p.status?.channel_title ? `● Connected as: ${p.status.channel_title}` : '● Connected & Ready') 
        : '○ Ready to connect (or runs in Preview mode)';

      return `
        <div class="panel-card" style="padding: 14px; background: var(--bg-card); display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-weight: 600; font-size: 14px;">${p.name}</div>
            <div style="font-size: 11.5px; color: ${isOk ? 'var(--accent-success)' : 'var(--text-dim)'}; margin-top: 2px;">
              ${statusText}
            </div>
          </div>
          <button class="btn ${btnClass} btn-sm" onclick="configurePlatformPrompt('${p.id}', '${p.name}')">
            ${btnText}
          </button>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Failed to load platforms:", err);
  }
}

function closeAccountsModal() {
  document.getElementById("accounts-modal").style.display = "none";
}

async function configurePlatformPrompt(platformId, platformName) {
  if (platformId === "youtube") {
    try {
      const res = await fetch("/api/youtube/login", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        alert("🎉 YouTube channel connected successfully!");
        openAccountsModal();
        loadQueue();
      } else {
        alert(`Google Sign-In note: ${data.message}`);
      }
    } catch (err) {
      alert("Error starting Google Login: " + err);
    }
    return;
  }
}

let currentPlanStatus = { is_pro: false, remaining_free: 5, plan_name: "Free Starter" };

async function loadLicenseStatus() {
  try {
    const res = await fetch("/api/license/status");
    const data = await res.json();
    currentPlanStatus = data;
    
    const planPill = document.getElementById("stat-plan-pill");
    const planName = document.getElementById("stat-plan-name");
    const upgradeBtn = document.getElementById("btn-upgrade-pro");

    if (data.is_pro) {
      if (planName) {
        planName.innerHTML = `👑 Pro Lifetime`;
        planName.style.color = "#10b981";
      }
      if (planPill) {
        planPill.style.background = "rgba(16, 185, 129, 0.12)";
        planPill.style.borderColor = "rgba(16, 185, 129, 0.35)";
      }
      if (upgradeBtn) upgradeBtn.style.display = "none";
    } else {
      if (planName) {
        planName.textContent = `Free (${data.remaining_free}/5 left)`;
        planName.style.color = "#fbbf24";
      }
      if (planPill) {
        planPill.style.background = "rgba(234, 179, 8, 0.12)";
        planPill.style.borderColor = "rgba(234, 179, 8, 0.35)";
      }
      if (upgradeBtn) upgradeBtn.style.display = "inline-flex";
    }
  } catch (err) {
    console.error("Failed to load license status:", err);
  }
}

function openLicenseModal() {
  const modal = document.getElementById("license-modal");
  if (modal) modal.classList.add("active");
  const msg = document.getElementById("license-activate-msg");
  if (msg) msg.style.display = "none";
}

function closeLicenseModal() {
  const modal = document.getElementById("license-modal");
  if (modal) modal.classList.remove("active");
}

async function activateLicenseKey() {
  const input = document.getElementById("license-key-input");
  const msg = document.getElementById("license-activate-msg");
  const key = input.value.trim().toUpperCase();

  if (!key) {
    msg.style.display = "block";
    msg.style.color = "#ef4444";
    msg.textContent = "Please enter your license key.";
    return;
  }

  try {
    const res = await fetch("/api/license/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key })
    });
    const data = await res.json();
    msg.style.display = "block";
    if (data.success) {
      msg.style.color = "#10b981";
      msg.textContent = "🎉 " + data.message;
      loadLicenseStatus();
      setTimeout(() => {
        closeLicenseModal();
      }, 1600);
    } else {
      msg.style.color = "#ef4444";
      msg.textContent = "❌ " + data.message;
    }
  } catch (err) {
    msg.style.display = "block";
    msg.style.color = "#ef4444";
    msg.textContent = "Error activating key. Try again.";
  }
}

// Bulk Upload Trigger & Live Status Polling
async function startBulkUpload() {
  if (currentQueue.length === 0) {
    alert("Your queue is empty. Add videos first!");
    return;
  }

  const btn = document.getElementById("btn-start-bulk");
  btn.disabled = true;
  btn.textContent = "⏳ Uploading Queue...";

  try {
    const res = await fetch("/api/upload/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (data.success) {
      startUploadPolling();
    } else {
      btn.disabled = false;
      btn.textContent = "🚀 Publish / Schedule All";
      if (data.requires_pro) {
        openLicenseModal();
        alert(data.message);
      } else {
        alert(data.message);
      }
    }
  } catch (err) {
    console.error("Upload start failed:", err);
    btn.disabled = false;
    btn.textContent = "🚀 Publish / Schedule All";
  }
}

function startUploadPolling() {
  if (uploadPollInterval) clearInterval(uploadPollInterval);

  uploadPollInterval = setInterval(async () => {
    try {
      const res = await fetch("/api/upload/status");
      const status = await res.json();

      if (status.is_uploading) {
        document.getElementById("btn-start-bulk").textContent = `⏳ ${status.status_message} (${status.progress}%)`;
        loadQueue(); // Refresh card badges
      } else {
        clearInterval(uploadPollInterval);
        document.getElementById("btn-start-bulk").disabled = false;
        document.getElementById("btn-start-bulk").textContent = "🚀 Publish / Schedule All";
        loadQueue();
        loadLicenseStatus();
        alert(`🎉 Bulk publish / scheduling finished! Processed ${status.completed_count} videos.`);
      }
    } catch (err) {
      console.error("Polling error:", err);
    }
  }, 1000);
}
