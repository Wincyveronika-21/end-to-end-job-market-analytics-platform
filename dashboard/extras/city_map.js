const remoteToggle = document.getElementById("remote-only");

async function loadCities() {
    const message = document.getElementById("message");
    message.textContent = "";
    try {
        const data = await Extras.request(`/extras/cities?remote_only=${remoteToggle.checked}`);
        const cities = data.cities;
        const mappable = cities.filter(city => city.latitude !== null && city.longitude !== null);
        await Plotly.newPlot("map", [{
            type: "scattergeo",
            mode: "markers",
            lat: mappable.map(city => city.latitude),
            lon: mappable.map(city => city.longitude),
            text: mappable.map(city => `${city.city}, ${city.country} (${city.tier})`),
            customdata: mappable.map(city => [city.job_count, city.average_salary]),
            marker: {
                size: mappable.map(city => Math.max(8, Math.min(34, 7 + Math.sqrt(city.job_count) * 2))),
                color: mappable.map(city => city.average_salary || 0),
                colorscale: "Viridis",
                showscale: true,
                colorbar: { title: "Average salary" }
            },
            hovertemplate: "%{text}<br>Jobs: %{customdata[0]}<br>Average salary: %{customdata[1]}<extra></extra>"
        }], {
            paper_bgcolor: "#111827",
            plot_bgcolor: "#111827",
            font: { color: "#d3d9e7" },
            geo: { bgcolor: "#111827", showland: true, landcolor: "#edf1f7", showcountries: true },
            margin: { t: 10, b: 10, l: 10, r: 10 }
        }, { responsive: true });

        document.getElementById("remote-summary").textContent =
            `Remote postings: ${data.remote_job_count}; average listed salary: ${
                data.remote_average_salary === null
                    ? "not available"
                    : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })
                        .format(data.remote_average_salary)
            }.`;
        const table = document.createElement("table");
        const header = document.createElement("tr");
        for (const column of ["City", "Country", "Jobs", "Remote", "Onsite", "Average salary", "Tier"]) {
            const cell = document.createElement("th");
            cell.textContent = column;
            header.append(cell);
        }
        table.append(header);
        for (const city of cities) {
            const row = document.createElement("tr");
            for (const value of [
                city.city, city.country, city.job_count, city.remote_jobs, city.onsite_jobs,
                city.average_salary === null
                    ? "—"
                    : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })
                        .format(city.average_salary),
                city.tier
            ]) {
                const cell = document.createElement("td");
                cell.textContent = String(value);
                row.append(cell);
            }
            table.append(row);
        }
        document.getElementById("table-wrap").replaceChildren(table);
    } catch (error) {
        message.textContent = error.message;
    }
}

remoteToggle.addEventListener("change", loadCities);
loadCities();
