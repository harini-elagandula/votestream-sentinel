```javascript
const API = "http://127.0.0.1:8000";
const WS = "ws://127.0.0.1:8000/ws/votes";

const electionSelect = document.getElementById("electionSelect");
const candidateSelect = document.getElementById("candidateSelect");
const resultsDiv = document.getElementById("results");
const activityLog = document.getElementById("activityLog");
const voteMessage = document.getElementById("voteMessage");

let elections = [];
let candidates = [];
let socket;

function logActivity(message) {
    const time = new Date().toLocaleTimeString();
    activityLog.textContent =
        `[${time}] ${message}\n` + activityLog.textContent;
}

async function requestJSON(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || `Request failed: ${response.status}`
        );
    }

    return data;
}

// Load all elections
async function loadElections() {
    try {
        elections = await requestJSON(
            `${API}/api/v1/elections`
        );

        electionSelect.replaceChildren();

        if (!Array.isArray(elections) || elections.length === 0) {
            electionSelect.add(
                new Option("No elections found", "")
            );
            candidateSelect.replaceChildren(
                new Option("No candidates available", "")
            );
            resultsDiv.textContent = "Create an election to get started.";
            return;
        }

        elections.forEach(election => {
            electionSelect.add(
                new Option(
                    `${election.title} (#${election.id})`,
                    election.id
                )
            );
        });

        electionSelect.value = String(elections[0].id);

        await loadResults();
        logActivity("Elections loaded successfully.");
    } catch (error) {
        electionSelect.replaceChildren(
            new Option("Could not load elections", "")
        );
        logActivity(`Election loading error: ${error.message}`);
    }
}

// Load election results
async function loadResults() {
    const electionId = electionSelect.value;

    if (!electionId) return;

    try {
        const election = elections.find(
            item => String(item.id) === String(electionId)
        );

        document.getElementById("electionStatus").textContent =
            election?.status || "—";

        document.getElementById("electionInfo").textContent =
            election?.title || `Election #${electionId}`;

        // FIX: Support both a list and an object containing results.
        const response = await requestJSON(
            `${API}/api/v1/results/${electionId}`
        );

        const results = Array.isArray(response)
            ? response
            : Array.isArray(response.results)
                ? response.results
                : [];

        renderResults(results);
        await loadCandidates(electionId);

    } catch (error) {
        logActivity(`Results error: ${error.message}`);
    }
}

// Display results and vote totals
function renderResults(results) {
    resultsDiv.replaceChildren();

    // Protect against an unexpected API response.
    if (!Array.isArray(results)) {
        results = [];
    }

    const totalVotes = results.reduce(
        (sum, item) => sum + Number(item.votes || 0),
        0
    );

    document.getElementById("totalVotes").textContent =
        totalVotes;

    document.getElementById("candidateCount").textContent =
        results.length;

    if (results.length === 0) {
        resultsDiv.textContent =
            "No results yet. Add candidates to this election.";
        return;
    }

    results.forEach(item => {
        const card = document.createElement("article");
        card.className = "candidate-card";

        const name = document.createElement("h4");
        name.textContent =
            item.candidate || item.name || "Unknown candidate";

        const count = document.createElement("p");
        count.className = "vote-number";
        count.textContent = `${Number(item.votes || 0)} votes`;

        const track = document.createElement("div");
        track.className = "bar-track";

        const fill = document.createElement("div");
        fill.className = "bar-fill";

        fill.style.width = totalVotes > 0
            ? `${(Number(item.votes || 0) / totalVotes) * 100}%`
            : "0%";

        track.appendChild(fill);
        card.append(name, count, track);
        resultsDiv.appendChild(card);
    });
}

// Load candidates for the selected election
async function loadCandidates(electionId) {
    try {
        candidates = await requestJSON(
            `${API}/api/v1/elections/${electionId}/candidates`
        );

        if (!Array.isArray(candidates)) {
            candidates = [];
        }

        candidateSelect.replaceChildren(
            new Option(
                candidates.length
                    ? "Select a candidate"
                    : "No candidates — add candidates first",
                ""
            )
        );

        candidates.forEach(candidate => {
            candidateSelect.add(
                new Option(candidate.name, candidate.id)
            );
        });

        logActivity(
            `Loaded ${candidates.length} candidate(s).`
        );

    } catch (error) {
        candidates = [];

        candidateSelect.replaceChildren(
            new Option("Could not load candidates", "")
        );

        logActivity(
            `Candidate loading error: ${error.message}`
        );
    }
}

// Connect to live WebSocket updates
function connectWebSocket() {
    socket = new WebSocket(WS);

    socket.onopen = () => {
        document.getElementById("connectionStatus").textContent =
            "Live connection";

        document.getElementById("connectionDot").className =
            "dot connected";

        logActivity("WebSocket connected.");
    };

    socket.onmessage = event => {
        try {
            const data = JSON.parse(event.data);

            if (data.type === "vote_update") {
                logActivity("Live vote update received.");

                if (
                    String(data.election_id) ===
                    String(electionSelect.value)
                ) {
                    const results = Array.isArray(data.results)
                        ? data.results
                        : [];

                    renderResults(results);
                }
            }
        } catch (error) {
            logActivity(
                `WebSocket message error: ${error.message}`
            );
        }
    };

    socket.onclose = () => {
        document.getElementById("connectionStatus").textContent =
            "Disconnected — refresh page to reconnect";

        document.getElementById("connectionDot").className =
            "dot disconnected";

        logActivity("WebSocket disconnected.");
    };

    socket.onerror = () => {
        document.getElementById("connectionStatus").textContent =
            "Connection error";

        logActivity("WebSocket connection error.");
    };
}

// Load results button
document.getElementById("loadButton").addEventListener(
    "click",
    loadResults
);

// Refresh button
document.getElementById("refreshButton").addEventListener(
    "click",
    loadResults
);

// Change election
electionSelect.addEventListener(
    "change",
    loadResults
);

// Submit a demo vote
document.getElementById("voteForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        const electionId = electionSelect.value;
        const candidateId = candidateSelect.value;

        const voterId = document
            .getElementById("voterId")
            .value
            .trim();

        if (!electionId || !candidateId || !voterId) {
            voteMessage.textContent =
                "Please select an election, select a candidate, and enter a demo voter ID.";
            return;
        }

        try {
            const result = await