// static/js/offense.js
// console.log(123);
// grab DOM nodes
let beatSelect, ctx, causeChart;

// initialize chart with the data passed from Flask
function initChart() {
    causeChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: window.initialLabels,
            datasets: [
                {
                    label: "Crash Count",
                    data: window.initialValues,
                    backgroundColor: "rgba(52, 152, 219, 0.7)",
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            scales: {
                x: { title: { display: true, text: "Count" } },
                y: { title: { display: true, text: "Cause" } },
            },
        },
    });
}

// fetch fresh data from your API and redraw chart
function fetchAndDraw() {
    const beat = encodeURIComponent(beatSelect.value);
    fetch(`/offense/api/primary-cause?beat=${beat}`)
        .then((r) => r.json())
        .then((data) => {
            const labels = data.map((d) => d.cause || "Unknown");
            const counts = data.map((d) => d.count);

            // update existing chart
            causeChart.data.labels = labels;
            causeChart.data.datasets[0].data = counts;
            causeChart.update();
        });
}

// wire up events
document.addEventListener("DOMContentLoaded", () => {
    beatSelect = document.getElementById("region-select");
    ctx = document.getElementById("cause-chart").getContext("2d");

    initChart();

    beatSelect.addEventListener("change", (event) => {
        console.log("Beat changed to:", event.target.value);
        // or alert('Beat changed to: ' + event.target.value);
        fetchAndDraw();
    });
});
