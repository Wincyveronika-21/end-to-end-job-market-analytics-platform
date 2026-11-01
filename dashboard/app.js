// Job Market Analytics Platform - Main JS Engine

let chartSkills = null;
let chartSalary = null;
let chartWorkmode = null;
let chartCities = null;

document.addEventListener("DOMContentLoaded", () => {
    initDashboard();
    setupEventListeners();
});

async function initDashboard() {
    await fetchOverviewMetrics();
    await fetchDemandedSkillsChart();
    await fetchSalaryTrendsChart();
    await fetchWorkModeChart();
    await fetchCityHiringChart();
    await fetchLiveJobs();
}

function setupEventListeners() {
    document.getElementById("btn-refresh").addEventListener("click", async () => {
        const btn = document.getElementById("btn-refresh");
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Ingesting...';
        try {
            await fetch("/api/ingest/trigger", { method: "POST" });
            await initDashboard();
        } catch (e) {
            console.error("Ingestion trigger error:", e);
        } finally {
            btn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Trigger Ingest';
        }
    });

    document.getElementById("btn-export").addEventListener("click", () => {
        window.location.href = "/api/export/csv";
    });

    document.getElementById("filter-category").addEventListener("change", fetchDemandedSkillsChart);
    document.getElementById("filter-workmode").addEventListener("change", fetchLiveJobs);
    
    let searchTimeout = null;
    document.getElementById("search-input").addEventListener("input", () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(fetchLiveJobs, 400);
    });

    // Chatbot drawer toggles
    const chatBtn = document.getElementById("btn-chat-toggle");
    const chatDrawer = document.getElementById("chat-drawer");
    const chatClose = document.getElementById("btn-close-chat");

    chatBtn.addEventListener("click", () => chatDrawer.classList.toggle("active"));
    chatClose.addEventListener("click", () => chatDrawer.classList.remove("active"));

    // Resume match button
    document.getElementById("btn-match-skills").addEventListener("click", handleResumeMatch);

    document.getElementById("btn-build-career-plan").addEventListener("click", handleBuildCareerPlan);
    document.getElementById("career-resume-file").addEventListener("change", handleResumeFile);
    document.getElementById("job-stream-container").addEventListener("click", event => {
        const button = event.target.closest(".btn-career-plan");
        if (!button) return;

        document.getElementById("career-job-select").value = button.dataset.jobId;
        document.getElementById("career-portal").scrollIntoView({ behavior: "smooth" });
        document.getElementById("career-resume-text").focus({ preventScroll: true });
    });
}

// 1. Overview KPIs
async function fetchOverviewMetrics() {
    try {
        const res = await fetch("/api/analytics/overview");
        const data = await res.json();

        document.getElementById("kpi-total-jobs").innerText = (data.total_jobs || 0).toLocaleString();
        document.getElementById("kpi-avg-salary").innerText = "$" + (data.avg_salary || 0).toLocaleString();
        document.getElementById("kpi-remote-pct").innerText = (data.remote_pct || 0) + "%";
        document.getElementById("kpi-top-skill").innerText = data.top_skill || "N/A";
        document.getElementById("kpi-top-city").innerText = data.top_city || "N/A";
    } catch (e) {
        console.error("Error fetching overview metrics:", e);
    }
}

// 2. Demanded Skills Bar Chart
async function fetchDemandedSkillsChart() {
    try {
        const category = document.getElementById("filter-category").value;
        const res = await fetch(`/api/analytics/demanded-skills?limit=10&category=${category}`);
        const data = await res.json();

        const labels = data.map(d => d.skill);
        const counts = data.map(d => d.demand_count);
        const avgSalaries = data.map(d => d.avg_salary);

        const ctx = document.getElementById("chart-skills").getContext("2d");
        if (chartSkills) chartSkills.destroy();

        chartSkills = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Job Postings Mentioning Skill",
                    data: counts,
                    backgroundColor: "rgba(236, 72, 153, 0.75)",
                    borderColor: "#EC4899",
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const idx = context.dataIndex;
                                return "Avg Salary: $" + (avgSalaries[idx] || 0).toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: "#9CA3AF" }, grid: { color: "rgba(255,255,255,0.05)" } },
                    y: { ticks: { color: "#F3F4F6", font: { weight: "600" } }, grid: { display: false } }
                }
            }
        });
    } catch (e) {
        console.error("Error fetching skills chart:", e);
    }
}

// 3. Salary Trends Multi-Bar Chart
async function fetchSalaryTrendsChart() {
    try {
        const res = await fetch("/api/analytics/salary-trends");
        const data = await res.json();
        const skillsData = data.salary_by_skill || [];

        const labels = skillsData.map(s => s.skill);
        const minSal = skillsData.map(s => s.min_salary);
        const avgSal = skillsData.map(s => s.avg_salary);
        const maxSal = skillsData.map(s => s.max_salary);

        const ctx = document.getElementById("chart-salary").getContext("2d");
        if (chartSalary) chartSalary.destroy();

        chartSalary = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    { label: "Min Salary", data: minSal, backgroundColor: "rgba(59, 130, 246, 0.4)" },
                    { label: "Avg Salary", data: avgSal, backgroundColor: "rgba(16, 185, 129, 0.85)" },
                    { label: "Max Salary", data: maxSal, backgroundColor: "rgba(139, 92, 246, 0.4)" }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#9CA3AF" } }
                },
                scales: {
                    x: { ticks: { color: "#9CA3AF" }, grid: { display: false } },
                    y: { 
                        ticks: { 
                            color: "#9CA3AF",
                            callback: value => "$" + (value/1000) + "k"
                        }, 
                        grid: { color: "rgba(255,255,255,0.05)" } 
                    }
                }
            }
        });
    } catch (e) {
        console.error("Error fetching salary trends chart:", e);
    }
}

// 4. Remote vs Onsite Doughnut Chart
async function fetchWorkModeChart() {
    try {
        const res = await fetch("/api/analytics/work-mode");
        const data = await res.json();

        const labels = data.map(d => d.work_mode);
        const values = data.map(d => d.total_jobs);

        const ctx = document.getElementById("chart-workmode").getContext("2d");
        if (chartWorkmode) chartWorkmode.destroy();

        chartWorkmode = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ["#10B981", "#3B82F6", "#F59E0B"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { color: "#F3F4F6", font: { size: 13 } } }
                },
                cutout: "68%"
            }
        });
    } catch (e) {
        console.error("Error fetching workmode chart:", e);
    }
}

// 5. Top Cities Bar Chart
async function fetchCityHiringChart() {
    try {
        const res = await fetch("/api/analytics/city-hiring?limit=8");
        const data = await res.json();

        const labels = data.map(d => d.city);
        const counts = data.map(d => d.total_postings);

        const ctx = document.getElementById("chart-cities").getContext("2d");
        if (chartCities) chartCities.destroy();

        chartCities = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Open Job Positions",
                    data: counts,
                    backgroundColor: "rgba(245, 158, 11, 0.8)",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: "#9CA3AF" }, grid: { display: false } },
                    y: { ticks: { color: "#9CA3AF" }, grid: { color: "rgba(255,255,255,0.05)" } }
                }
            }
        });
    } catch (e) {
        console.error("Error fetching city hiring chart:", e);
    }
}

// 6. Live Job Stream List
async function fetchLiveJobs() {
    try {
        const workMode = document.getElementById("filter-workmode").value;
        const search = document.getElementById("search-input").value;

        let url = `/api/jobs?limit=100&work_mode=${workMode}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;

        const res = await fetch(url);
        const data = await res.json();
        const container = document.getElementById("job-stream-container");
        populateCareerJobOptions(data.jobs || []);

        if (!data.jobs || data.jobs.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No postings matched your criteria.</p>';
            return;
        }

        container.innerHTML = data.jobs.slice(0, 15).map(j => `
            <div class="job-item">
                <div>
                    <div class="job-title-text">${escapeHtml(j.title)}</div>
                    <div class="job-subtext">
                        <span><i class="fa-regular fa-building"></i> ${escapeHtml(j.company)}</span> &bull; 
                        <span><i class="fa-solid fa-location-dot"></i> ${escapeHtml(j.city)}</span>
                    </div>
                    <div class="job-tags">
                        <span class="tag ${j.work_mode === 'Remote' ? 'tag-remote' : 'tag-onsite'}">${escapeHtml(j.work_mode)}</span>
                        <span class="tag">${escapeHtml(j.experience_level || 'Mid')}</span>
                        <span class="tag">${escapeHtml(j.source)}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="job-salary">$${(j.salary_avg || 0).toLocaleString()}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(j.date_posted)}</div>
                    <button class="btn btn-outline btn-career-plan" type="button" data-job-id="${escapeHtml(String(j.id))}">
                        <i class="fa-solid fa-graduation-cap"></i> Prepare for role
                    </button>
                </div>
            </div>
        `).join("");

    } catch (e) {
        console.error("Error fetching live jobs stream:", e);
    }
}

function populateCareerJobOptions(jobs) {
    const select = document.getElementById("career-job-select");
    jobs.forEach(job => {
        const id = String(job.id);
        if (Array.from(select.options).some(option => option.value === id)) return;
        const label = [job.title, job.company].filter(Boolean).join(" at ");
        select.add(new Option(label || "Job posting", id));
    });
}

async function handleResumeFile(event) {
    const file = event.target.files[0];
    if (!file) return;

    const error = document.getElementById("career-plan-error");
    error.style.display = "none";
    if (!/\.pdf$/i.test(file.name)) {
        error.textContent = "Please choose a PDF resume.";
        error.style.display = "block";
        event.target.value = "";
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        error.textContent = "PDF resumes must be 5 MB or smaller.";
        error.style.display = "block";
        event.target.value = "";
        return;
    }
}

async function handleBuildCareerPlan() {
    const jobId = document.getElementById("career-job-select").value;
    const resumeText = document.getElementById("career-resume-text").value.trim();
    const resumeFile = document.getElementById("career-resume-file").files[0];
    const error = document.getElementById("career-plan-error");
    const button = document.getElementById("btn-build-career-plan");
    const results = document.getElementById("career-plan-results");
    error.style.display = "none";

    if (!jobId || (!resumeFile && !resumeText)) {
        error.textContent = "Select a job and upload a PDF or paste resume text to build your plan.";
        error.style.display = "block";
        return;
    }
    if (resumeFile && resumeFile.size > 5 * 1024 * 1024) {
        error.textContent = "PDF resumes must be 5 MB or smaller.";
        error.style.display = "block";
        return;
    }

    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Building your plan...';
    try {
        let response;
        if (resumeFile) {
            const formData = new FormData();
            formData.append("job_id", jobId);
            formData.append("resume_file", resumeFile);
            response = await fetch("/api/career/job-plan-pdf", {
                method: "POST",
                body: formData
            });
        } else {
            response = await fetch("/api/career/job-plan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ job_id: jobId, resume_text: resumeText })
            });
        }
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Could not build the career plan.");
        }
        renderCareerPlan(data);
        results.style.display = "block";
    } catch (e) {
        console.error("Error building job career plan:", e);
        error.textContent = e.message || "Could not build the career plan. Please try again.";
        error.style.display = "block";
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="fa-solid fa-route"></i> Analyze Resume &amp; Build Learning Plan';
    }
}

function renderCareerPlan(data) {
    const results = document.getElementById("career-plan-results");
    const job = data.job || {};
    const matchLabel = data.match_score === null ? "No skills listed" : `${data.match_score}% role match`;
    const matched = data.matched_skills.length
        ? data.matched_skills.map(escapeHtml).join(", ")
        : "No listed requirements matched yet";
    const missing = data.missing_skills.length
        ? data.missing_skills.map(escapeHtml).join(", ")
        : "None";
    const applicationUrl = safeExternalUrl(job.url);
    const learningCards = data.learning_path.length
        ? data.learning_path.map(item => {
            const resourceUrl = safeExternalUrl(item.resource_url);
            return `
                <article class="learning-card">
                    <span class="learning-skill">${escapeHtml(item.skill)}</span>
                    <h4>${escapeHtml(item.project_title)}</h4>
                    <p><strong>Learning goal:</strong> ${escapeHtml(item.focus)}</p>
                    <p><strong>Portfolio project:</strong> ${escapeHtml(item.project_brief)}</p>
                    ${resourceUrl ? `<a href="${escapeHtml(resourceUrl)}" target="_blank" rel="noopener noreferrer">Open learning resource <i class="fa-solid fa-arrow-up-right-from-square"></i></a>` : ""}
                </article>
            `;
        }).join("")
        : '<p class="learning-empty">Your resume covers the skills listed for this role. Review the project requirements and use your existing experience to prepare your application.</p>';

    results.innerHTML = `
        <div class="career-result-heading">
            <div>
                <p class="career-eyebrow">YOUR ROLE PLAN</p>
                <h3>${escapeHtml(job.title)}${job.company ? ` at ${escapeHtml(job.company)}` : ""}</h3>
                <p>${escapeHtml([job.city, job.work_mode].filter(Boolean).join(" · "))}</p>
            </div>
            <div class="career-score">${escapeHtml(matchLabel)}</div>
        </div>
        <div class="career-skills-summary">
            <p><strong>Skills found in resume:</strong> ${matched}</p>
            <p><strong>Skills to develop:</strong> ${missing}</p>
        </div>
        <div class="learning-path">
            <h4><i class="fa-solid fa-list-check"></i> Learning goals &amp; project briefs</h4>
            ${learningCards}
        </div>
        <div class="career-apply">
            ${applicationUrl
                ? `<a class="btn btn-primary" href="${escapeHtml(applicationUrl)}" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-arrow-up-right-from-square"></i> Continue to application</a><span>Applications are submitted on the employer's website.</span>`
                : '<span>No application link is available for this posting.</span>'}
        </div>
    `;
}

function safeExternalUrl(value) {
    if (!value) return null;
    try {
        const url = new URL(value);
        return url.protocol === "https:" || url.protocol === "http:" ? url.href : null;
    } catch (e) {
        return null;
    }
}

// 7. Resume Skill Matcher
async function handleResumeMatch() {
    const input = document.getElementById("user-skills-input").value;
    if (!input.trim()) return;

    const skills = input.split(",").map(s => s.trim());
    try {
        const res = await fetch("/api/career/match-resume", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ skills: skills })
        });
        const data = await res.json();

        const box = document.getElementById("match-result-box");
        box.style.display = "block";
        document.getElementById("match-score").innerText = data.match_score + "% Market Alignment";
        
        const matchedNames = data.matched_skills.map(s => s.skill).join(", ") || "None";
        const missingNames = data.missing_high_demand_skills.map(s => s.skill).join(", ") || "None";

        document.getElementById("match-summary").innerHTML = `
            <p style="margin-bottom: 6px;"><strong>Matched Market Skills:</strong> <span style="color: var(--accent-emerald);">${matchedNames}</span></p>
            <p><strong>High-Demand Skills to Add:</strong> <span style="color: var(--accent-pink);">${missingNames}</span></p>
        `;
    } catch (e) {
        console.error("Error running resume match:", e);
    }
}

// 8. AI Chatbot Interface
async function handleSendChat() {
    const input = document.getElementById("chat-input");
    const question = input.value.trim();
    if (!question) return;

    input.value = "";
    appendChatMessage(question, "user");

    try {
        const res = await fetch("/api/chatbot/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });
        const data = await res.json();
        appendChatMessage(data.answer, "bot");
    } catch (e) {
        appendChatMessage("Sorry, I encountered an issue processing your query.", "bot");
    }
}

function sendQuickPrompt(promptText) {
    document.getElementById("chat-input").value = promptText;
    handleSendChat();
}

function appendChatMessage(text, sender) {
    const messagesContainer = document.getElementById("chat-messages");
    const div = document.createElement("div");
    div.className = `msg msg-${sender}`;
    
    // Simple markdown parsing for formatting
    let formatted = escapeHtml(text)
        .replace(/### (.*?)\n/g, '<strong style="font-size: 1rem; color: #FFF;">$1</strong><br>')
        .replace(/#### (.*?)\n/g, '<strong style="font-size: 0.9rem; color: #FFF;">$1</strong><br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');

    div.innerHTML = formatted;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
