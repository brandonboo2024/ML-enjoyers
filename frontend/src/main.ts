import "./styles.css";

type AlertItem = {
  id: string;
  receivedAt: string;
  deviceId: string;
  eventType: string;
  confidence: number;
  location: string;
  notes: string;
  transport: string;
  acknowledgedAt?: string;
  acknowledgedBy?: string;
};

const alertsContainer = document.querySelector<HTMLDivElement>("#alerts");
const refreshButton = document.querySelector<HTMLButtonElement>("#refresh");
const statusEl = document.querySelector<HTMLSpanElement>("#status");
const filterButtons = document.querySelectorAll<HTMLButtonElement>(".filter-button");
const summaryEl = document.querySelector<HTMLDivElement>("#summary");

const apiBase = "http://localhost:4100";
let currentFilter: "all" | "unacknowledged" = "all";

function setStatus(message: string) {
  if (statusEl) {
    statusEl.textContent = message;
  }
}

function formatTime(value?: string) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function updateSummary(total: number, unacknowledged: number) {
  if (!summaryEl) return;
  summaryEl.innerHTML = `
    <span class="summary-label">Total</span>
    <span class="summary-value">${total}</span>
    <span class="summary-label">Unacknowledged</span>
    <span class="summary-value">${unacknowledged}</span>
  `;
}

function updateFilterButtons() {
  filterButtons.forEach((button) => {
    const filter = button.dataset.filter;
    if (!filter) return;
    button.classList.toggle("is-active", filter === currentFilter);
  });
}

function renderAlerts(items: AlertItem[]) {
  if (!alertsContainer) return;
  const unacknowledged = items.filter((item) => !item.acknowledgedAt).length;
  updateSummary(items.length, unacknowledged);
  const visibleItems =
    currentFilter === "unacknowledged"
      ? items.filter((item) => !item.acknowledgedAt)
      : items;

  if (!visibleItems.length) {
    alertsContainer.innerHTML =
      currentFilter === "unacknowledged"
        ? "<p>No unacknowledged alerts right now.</p>"
        : "<p>No alerts yet.</p>";
    return;
  }

  alertsContainer.innerHTML = visibleItems
    .map((item) => {
      const acknowledged = Boolean(item.acknowledgedAt);
      const ackMeta = item.acknowledgedAt
        ? `Acknowledged ${formatTime(item.acknowledgedAt)} by ${item.acknowledgedBy}`
        : "Not acknowledged";
      const confidence = (item.confidence * 100).toFixed(1);

      return `
        <article class="alert-card ${acknowledged ? "is-ack" : "is-pending"}">
          <div class="alert-header">
            <div>
              <h3>Fall Alert</h3>
              <div class="alert-sub">${item.deviceId} · ${formatTime(item.receivedAt)}</div>
            </div>
            <div class="alert-tags">
              <span class="badge">${item.eventType}</span>
              <span class="status-pill ${acknowledged ? "ack" : "pending"}">
                ${acknowledged ? "Acknowledged" : "Unacknowledged"}
              </span>
            </div>
          </div>
          <div class="alert-body">
            <div class="alert-meta">
              <div>
                <span class="meta-label">Location</span>
                <span class="meta-value">${item.location}</span>
              </div>
              <div>
                <span class="meta-label">Transport</span>
                <span class="meta-value">${item.transport}</span>
              </div>
              <div>
                <span class="meta-label">Status</span>
                <span class="meta-value">${ackMeta}</span>
              </div>
            </div>
            <div class="alert-notes">
              <h4>Notes</h4>
              <p>${item.notes || "No notes"}</p>
            </div>
          </div>
          <div class="alert-actions">
            <div class="confidence">
              <span class="meta-label">Confidence</span>
              <div class="confidence-bar" style="--confidence:${confidence}%">
                <span></span>
              </div>
              <strong>${confidence}%</strong>
            </div>
            ${acknowledged ? "" : `<button data-ack="${item.id}">Acknowledge</button>`}
          </div>
        </article>
      `;
    })
    .join("");

  const ackButtons = alertsContainer.querySelectorAll<HTMLButtonElement>("button[data-ack]");
  ackButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const id = button.dataset.ack;
      if (!id) return;
      await fetch(`${apiBase}/api/ack/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ by: "caregiver" })
      });
      await loadAlerts();
    });
  });
}

async function loadAlerts() {
  try {
    setStatus("Loading...");
    const response = await fetch(`${apiBase}/api/alerts`);
    const data = await response.json();
    renderAlerts(data.items || []);
    setStatus("Updated");
  } catch (err) {
    console.error(err);
    setStatus("Failed to load alerts");
  }
}

refreshButton?.addEventListener("click", () => {
  void loadAlerts();
});

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    if (!filter) return;
    currentFilter = filter as "all" | "unacknowledged";
    updateFilterButtons();
    void loadAlerts();
  });
});

updateFilterButtons();
void loadAlerts();
