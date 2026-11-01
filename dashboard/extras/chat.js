Extras.bind("chat-form", async form => {
    const missingSkills = form.get("missing_skills").split(",").map(skill => skill.trim()).filter(Boolean);
    const result = await Extras.request("/extras/chat", {
        method: "POST",
        body: JSON.stringify({
            question: form.get("question"),
            target_role: form.get("target_role") || null,
            missing_skills: missingSkills.length ? missingSkills : null
        })
    });
    Extras.showJson("result", result);
}, "message");
