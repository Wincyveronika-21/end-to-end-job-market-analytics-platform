document.getElementById("load-trends").addEventListener("click", async event => {
    const button = event.currentTarget;
    const message = document.getElementById("message");
    const charts = document.getElementById("charts");
    button.disabled = true;
    message.textContent = "";
    charts.replaceChildren();
    try {
        const result = await Extras.request("/extras/trends?horizon_months=3&top_n=10");
        if (!result.available) {
            message.textContent = result.message;
            return;
        }
        for (const forecast of result.forecasts) {
            const panel = document.createElement("section");
            panel.className = "panel";
            const heading = document.createElement("h2");
            heading.textContent = forecast.skill;
            const canvas = document.createElement("canvas");
            canvas.className = "chart";
            panel.append(heading, canvas);
            charts.append(panel);
            const history = forecast.history;
            const future = forecast.forecast;
            new Chart(canvas, {
                type: "line",
                data: {
                    labels: [...history.map(item => item.month), ...future.map(item => item.month)],
                    datasets: [
                        {
                            label: "Actual postings",
                            data: [...history.map(item => item.count), ...future.map(() => null)],
                            borderColor: "#2457c5",
                            spanGaps: false
                        },
                        {
                            label: "Forecast",
                            data: [...history.map(() => null), ...future.map(item => item.count)],
                            borderColor: "#d16d21",
                            borderDash: [6, 4],
                            spanGaps: false
                        }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    } catch (error) {
        message.textContent = error.message;
    } finally {
        button.disabled = false;
    }
});
