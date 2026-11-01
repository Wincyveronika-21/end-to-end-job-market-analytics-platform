Extras.bind("salary-form", async form => {
    const result = await Extras.request("/extras/salary/predict", {
        method: "POST",
        body: JSON.stringify({
            title: form.get("title"),
            city: form.get("city"),
            experience_level: form.get("experience_level"),
            work_mode: form.get("work_mode"),
            skills: form.get("skills").split(",").map(skill => skill.trim()).filter(Boolean)
        })
    });
    const container = document.getElementById("result");
    container.replaceChildren();

    const card = document.createElement("section");
    card.className = "result-card";
    const heading = document.createElement("h3");
    heading.textContent = "Estimated annual salary";
    const amount = document.createElement("div");
    amount.className = "metric";
    amount.textContent = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: result.currency,
        maximumFractionDigits: 0
    }).format(result.predicted_salary);
    card.append(heading, amount);
    container.append(card);
}, "message");
