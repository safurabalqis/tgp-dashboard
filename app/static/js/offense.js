// fire on Apply or on page load
document
    .getElementById("apply-filters")
    .addEventListener("click", fetchAndDraw);

function fetchAndDraw() {
    const params = new URLSearchParams({
        start_date: document.getElementById("start-date").value,
        end_date: document.getElementById("end-date").value,
        region: document.getElementById("region-select").value,
    });

    fetch(`/offense/api/cause-distribution?${params}`)
        .then((res) => res.json())
        .then((data) => {
            const labels = data.map((d) => d.cause || "Unknown");
            const counts = data.map((d) => d.count);

            // Destroy existing chart if needed
            if (window.causeChart) window.causeChart.destroy();

            // Render horizontal bar chart
            const ctx = document.getElementById("cause-chart").getContext("2d");
            window.causeChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [{ label: "Crash Count", data: counts }],
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: "Count" } },
                    },
                },
            });

            // Populate table
            const tbody = document.querySelector("#cause-table tbody");
            tbody.innerHTML = data
                .map(
                    (d) =>
                        `<tr><td>${d.cause || "Unknown"}</td><td>${
                            d.count
                        }</td></tr>`,
                )
                .join("");
        });
}

// Initial draw with defaults (optional):
document.addEventListener("DOMContentLoaded", fetchAndDraw);
