// Register datalabels plugin
Chart.register(ChartDataLabels);

const charts = {}; // Store chart instances dynamically

// === Load Filters ===
async function loadFilters() {
    try {
        const res = await fetch('/environment/api/filters');
        const data = await res.json();

        document.getElementById('weather-filter').innerHTML =
            `<option value="All">All</option>` + data.weather.map(w => `<option value="${w}">${w}</option>`).join('');
        document.getElementById('speed-filter').innerHTML =
            `<option value="All">All</option>` + data.speed.map(s => `<option value="${s}">${s}</option>`).join('');
        document.getElementById('lighting-filter').innerHTML =
            `<option value="All">All</option>` + data.lighting.map(l => `<option value="${l}">${l}</option>`).join('');
    } catch (err) {
        console.error("Failed to load filters:", err);
    }
}

// === Load Metrics & Charts ===
async function loadData() {
    const month = document.getElementById('month-filter').value;
    const weather = document.getElementById('weather-filter').value;
    const speed = document.getElementById('speed-filter').value;
    const lighting = document.getElementById('lighting-filter').value;

    try {
        const res = await fetch(`/environment/api/data?month=${month}&weather=${weather}&speed=${speed}&lighting=${lighting}`);
        const data = await res.json();

        // Update metrics
        document.getElementById("metric-total").textContent = data.metrics.total;
        document.getElementById("metric-street").textContent = data.metrics.common_street;
        document.getElementById("metric-street-count").textContent = `${data.metrics.common_street_count} crashes`;
        document.getElementById("metric-severe").textContent = data.metrics.severe;

        // Update charts
        updateChart("chart-speed", data.charts.speed, "blue", "Crashes by Speed Limit", 'bar');
        updateChart("chart-weather", data.charts.weather, "green", "Crashes by Weather", 'bar');
        updateChart("chart-lighting", data.charts.lighting, "orange", "Crashes by Lighting", 'doughnut');

        // Load heatmap
        loadHeatmap();
    } catch (err) {
        console.error("Failed to load data:", err);
    }
}

// === Update Chart Function ===
function updateChart(canvasId, data, color, label, type = 'bar') {
    const ctx = document.getElementById(canvasId).getContext('2d');

    const chartColors = {
        "chart-speed": ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE'],   // blue shades
        'chart-weather': ['#16a34a', '#22c55e', '#4ade80', '#86efac', '#bbf7d0'], // green shades
        "chart-lighting": ['#F59E0B', '#FBBF24', '#FCD34D', '#FDE68A'] // amber shades
    };

    // Sort by crash count (descending)
    const sortedData = [...data].sort((a, b) => b.count - a.count);

    const labels = sortedData.map(d => d.label || "Unknown");
    const values = sortedData.map(d => d.count || 0);

    if (charts[canvasId]) charts[canvasId].destroy();

    if (labels.length === 0 || values.length === 0) {
        ctx.font = "16px Arial";
        ctx.fillText("No data available", 30, 50);
        return;
    }

    const palette = chartColors[canvasId] || [color];

    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: type === 'doughnut'
                    ? palette.slice(0, values.length)
                    : palette[0]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: (canvasId === "chart-weather") ? 'y' : 'x',
            cutout: type === 'doughnut' ? '65%' : undefined,
            plugins: {
                legend: {
                    display: type === 'doughnut',
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        font: { size: 11 }
                    }
                },
                datalabels: { display: false }
            },
            elements: {
                bar: { borderRadius: 4 }
            },
            // Hide scales entirely for doughnut chart
            scales: type === 'doughnut'
                ? {} // no axes or grid
                : {
                    x: { grid: { color: 'rgba(0,0,0,0.04)' } },
                    y: { grid: { color: 'rgba(0,0,0,0.04)' } }
                }
        }
    });
}

// === Load Heatmap ===
async function loadHeatmap() {
    const month = document.getElementById('month-filter').value;
    const weather = document.getElementById('weather-filter').value;
    const speed = document.getElementById('speed-filter').value;
    const lighting = document.getElementById('lighting-filter').value;

    try {
        const res = await fetch(`/environment/heatmap?month=${month}&weather=${weather}&speed=${speed}&lighting=${lighting}`);
        const data = await res.json();

        const iframe = document.getElementById("heatmap-frame");
        if (data.map_path) {
            iframe.src = data.map_path;
        } else {
            iframe.srcdoc = "<p style='color:red;'>No data available for selected filters</p>";
        }
    } catch (err) {
        console.error("Failed to load heatmap:", err);
    }
}

// === Init ===
window.addEventListener('DOMContentLoaded', async () => {
    await loadFilters();
    await loadData();

    // Add event listeners for all dropdowns including month
    document.querySelectorAll("select").forEach(sel => {
        sel.addEventListener("change", loadData);
    });
});
