// static/js/offense.js

// grab DOM nodes & globals
let beatSelect, ctx, causeChart, map, markerCluster;

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

function initMap() {
    // Base layers
    const defaultOSM = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        { attribution: "© OpenStreetMap contributors" },
    );
    const light = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        { attribution: "©CartoDB" },
    );
    const dark = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        { attribution: "©CartoDB" },
    );

    map = L.map("map", {
        center: [41.8781, -87.6298], // Chicago
        zoom: 11,
        layers: [defaultOSM],
    });

    L.control
        .layers({
            Default: defaultOSM,
            Light: light,
            Dark: dark,
        })
        .addTo(map);

    // Initialize marker cluster group instead of plain layerGroup
    markerCluster = L.markerClusterGroup();
    map.addLayer(markerCluster);
}

function fetchAndDraw() {
    const beat = encodeURIComponent(beatSelect.value);

    // 1) Update chart
    fetch(`/offense/api/primary-cause?beat=${beat}`)
        .then((r) => r.json())
        .then((data) => {
            const labels = data.map((d) => d.cause || "Unknown");
            const counts = data.map((d) => d.count);

            causeChart.data.labels = labels;
            causeChart.data.datasets[0].data = counts;
            causeChart.update();
        });

    // 2) Update clustered hit-and-run points
    fetch(`/offense/api/hit-and-run?beat=${beat}`)
        .then((r) => r.json())
        .then((geojson) => {
            // clear old clusters
            markerCluster.clearLayers();

            // create a GeoJSON layer and add into cluster group
            const geoLayer = L.geoJSON(geojson, {
                pointToLayer: (feature, latlng) =>
                    L.circleMarker(latlng, {
                        radius: 6,
                        fillColor: "orange",
                        color: "#333",
                        weight: 1,
                        fillOpacity: 0.8,
                    }),
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(
                        `<strong>${feature.properties.cause}</strong><br>${feature.properties.date}`,
                    );
                },
            });

            markerCluster.addLayer(geoLayer);
        });
}

document.addEventListener("DOMContentLoaded", () => {
    beatSelect = document.getElementById("region-select");
    ctx = document.getElementById("cause-chart").getContext("2d");

    initChart();
    initMap();

    // initial load
    fetchAndDraw();

    beatSelect.addEventListener("change", () => {
        fetchAndDraw();
    });
});
