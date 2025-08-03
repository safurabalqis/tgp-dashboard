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

// (A) Transform API rows into Plotly sankey input
function buildSankeyData(rows, topN = 6) {
    // sum total per cause
    const totals = rows.reduce((acc, r) => {
        acc[r.cause] = (acc[r.cause] || 0) + r.count;
        return acc;
    }, {});

    // pick topN causes
    const topCauses = Object.entries(totals)
        .sort((a, b) => b[1] - a[1])
        .slice(0, topN)
        .map((e) => e[0]);

    // replace others with “Other”
    const pruned = rows.map((r) => ({
        cause: topCauses.includes(r.cause) ? r.cause : "Other",
        severity: r.severity,
        count: r.count,
    }));

    // build nodes & links as before
    const causes = [...new Set(pruned.map((r) => r.cause))];
    const severities = [...new Set(pruned.map((r) => r.severity))];
    const nodes = causes.concat(severities);
    const idx = (lbl) => nodes.indexOf(lbl);
    const links = pruned.map((r) => ({
        source: idx(r.cause),
        target: idx(r.severity),
        value: r.count,
    }));

    return { nodes, links };
}

// (B) Fetch & render Sankey for a given beat
function fetchAndDrawSankey(beat, singleCause = null) {
    fetch(`/offense/api/cause-severity?beat=${beat}`)
        .then((r) => r.json())
        .then((rows) => {
            // if drilling down to one cause, filter now:
            const filtered = singleCause
                ? rows.filter((r) => r.cause === singleCause)
                : rows;

            // pass 6 to show top 6 + “Other”
            const { nodes, links } = buildSankeyData(filtered, 6);

            Plotly.react(
                "sankey-chart",
                [
                    {
                        type: "sankey",
                        orientation: "h",
                        node: {
                            label: nodes,
                            pad: 25, // more padding
                            thickness: 20,
                            line: { color: "black", width: 0.5 },
                        },
                        link: {
                            source: links.map((l) => l.source),
                            target: links.map((l) => l.target),
                            value: links.map((l) => l.value),
                        },
                    },
                ],
                {
                    title: "Primary Cause → Crash Severity",
                    height: 600, // taller canvas
                    margin: { t: 50, l: 20, r: 20, b: 20 },
                },
            );
        });
}

document.addEventListener("DOMContentLoaded", () => {
    beatSelect = document.getElementById("region-select");
    ctx = document.getElementById("cause-chart").getContext("2d");

    initChart();
    initMap();

    // initial load
    fetchAndDraw();

    // initial sankey (all causes)
    fetchAndDrawSankey("all");

    // when the beat changes, redraw both
    beatSelect.addEventListener("change", () => {
        const b = beatSelect.value;
        fetchAndDraw(); // chart + map
        fetchAndDrawSankey(b); // sankey default
    });

    // drill-down on bar click
    causeChart.options.onClick = (evt, elements) => {
        if (!elements.length) return;
        const idx = elements[0].index;
        const cause = causeChart.data.labels[idx];
        fetchAndDrawSankey(beatSelect.value, cause);
    };
});
