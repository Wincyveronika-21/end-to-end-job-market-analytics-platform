Extras.bind("skill-gap-form", async form => {
    const skills = form.get("user_skills").split(",").map(skill => skill.trim()).filter(Boolean);
    const result = await Extras.request("/extras/skill-gap", {
        method: "POST",
        body: JSON.stringify({
            target_role: form.get("target_role"),
            user_skills: skills,
            resume_text: form.get("resume_text")
        })
    });
    const container = document.getElementById("result");
    container.replaceChildren();

    const summary = document.createElement("div");
    summary.className = "result-grid";
    for (const [label, value] of [
        ["Role match", `${result.match_score}%`],
        ["Role postings analyzed", result.posting_count],
        ["Skills already matched", result.matched_skills.length]
    ]) {
        const card = document.createElement("section");
        card.className = "result-card";
        const heading = document.createElement("h3");
        heading.textContent = label;
        const metric = document.createElement("div");
        metric.className = "metric";
        metric.textContent = value;
        card.append(heading, metric);
        summary.append(card);
    }

    const gaps = document.createElement("section");
    gaps.className = "result-card";
    const heading = document.createElement("h3");
    heading.textContent = "Top skills to learn next";
    gaps.append(heading);
    if (result.top_skills_to_learn.length) {
        for (const item of result.top_skills_to_learn) {
            const chip = document.createElement("span");
            chip.className = "skill-chip";
            chip.textContent = `${item.skill} · ${item.demand_count} postings`;
            gaps.append(chip);
        }
    } else {
        const message = document.createElement("p");
        message.textContent = "No missing skills were found for this role.";
        gaps.append(message);
    }
    summary.append(gaps);
    container.append(summary);

    const details = document.createElement("details");
    details.className = "panel";
    const toggle = document.createElement("summary");
    toggle.textContent = "View all matching and missing skills";
    const pre = document.createElement("pre");
    pre.className = "result";
    pre.textContent = JSON.stringify({
        matched_skills: result.matched_skills,
        missing_skills: result.missing_skills
    }, null, 2);
    details.append(toggle, pre);
    container.append(details);
}, "message");
