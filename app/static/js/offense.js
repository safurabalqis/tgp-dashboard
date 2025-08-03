// static/js/offense.js

// grab DOM nodes & globals
let beatSelect, ctx, causeChart, map, markerCluster, resetBtn;

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
            maintainAspectRatio: false,
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

function fetchAndDraw(overrideBeat = null) {
    const beat = encodeURIComponent(overrideBeat ?? beatSelect.value);

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

function fetchAndDrawSankey(beat, singleCause = null) {
    fetch(`/offense/api/cause-severity?beat=${encodeURIComponent(beat)}`)
        .then((r) => r.json())
        .then((rows) => {
            // 1) optionally drill down to a single cause
            const filtered = singleCause
                ? rows.filter((r) => r.cause === singleCause)
                : rows;

            // 2) build top-6+Other nodes & links
            const { nodes, links } = buildSankeyData(filtered, 6);

            // 3) prepare Plotly sankey trace
            const data = [
                {
                    type: "sankey",
                    orientation: "h",
                    node: {
                        label: nodes,
                        pad: 25,
                        thickness: 20,
                        line: { color: "black", width: 0.5 },
                    },
                    link: {
                        source: links.map((l) => l.source),
                        target: links.map((l) => l.target),
                        value: links.map((l) => l.value),
                    },
                },
            ];

            // 4) autosize layout (no fixed width/height)
            const layout = {
                autosize: true,
                margin: { t: 50, l: 20, r: 20, b: 20 },
            };

            // 5) tell Plotly to watch for container resizes
            const config = { responsive: true };

            // 6) draw & then force an immediate resize pass
            Plotly.react("sankey-chart", data, layout, config).then(() => {
                Plotly.Plots.resize(document.getElementById("sankey-chart"));
            });
        })
        .catch((err) => console.error("Sankey load error:", err));
}

function fetchSummary(beat = "all") {
    fetch(`/offense/api/primary-cause?beat=${encodeURIComponent(beat)}`)
        .then((r) => r.json())
        .then((data) => {
            const top = data[0] || { cause: "—", count: 0 };
            document.getElementById("summary-top-cause").innerText = `${
                top.cause
            } (${top.count.toLocaleString()})`;
        })
        .catch(console.error);

    fetch(`/offense/api/most-hit-and-run-beat`)
        .then((r) => r.json())
        .then(({ beat, count }) => {
            document.getElementById(
                "summary-top-hitrun",
            ).innerText = `${beat} (${count.toLocaleString()})`;
        })
        .catch(console.error);
}

document.addEventListener("DOMContentLoaded", () => {
    beatSelect = document.getElementById("region-select");
    ctx = document.getElementById("cause-chart").getContext("2d");
    resetBtn = document.getElementById("reset-filters");

    initChart();
    initMap();

    // initial load
    fetchAndDraw();
    fetchSummary();
    fetchAndDrawSankey("all");

    // 2) Wire up Choices.js on the beat dropdown
    const beatChoices = new Choices("#region-select", {
        searchEnabled: true,
        shouldSort: false,
        placeholder: true,
        placeholderValue: "All Beats",
        itemSelectText: "", // removes the “Press to select” text
        position: "bottom", // dropdown opens below
        removeItemButton: true, // not strictly needed for single-select
    });

    // when the beat changes, redraw both
    beatSelect.addEventListener("change", () => {
        const b = beatSelect.value;
        fetchSummary(b);
        fetchAndDraw(); // chart + map
        fetchAndDrawSankey(b); // sankey default
    });

    resetBtn.addEventListener("click", () => {
        beatSelect.value = "all";
        beatChoices.setChoiceByValue("all");

        fetchAndDraw("all");
        fetchAndDrawSankey("all");
        fetchSummary("all");
    });

    // drill-down on bar click
    causeChart.options.onClick = (evt, elements) => {
        if (!elements.length) return;
        const idx = elements[0].index;
        const cause = causeChart.data.labels[idx];
        fetchAndDrawSankey(beatSelect.value, cause);
    };
});
