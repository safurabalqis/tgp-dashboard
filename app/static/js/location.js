// static/js/location.js

document.addEventListener("DOMContentLoaded", () => {
    const map = L.map("map").setView([41.8781, -87.6298], 11);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    fetch("/location/api/heatmap")
        .then((res) => res.json())
        .then((data) => {
            L.heatLayer(data, {
                radius: 15,
                blur: 25,
                maxZoom: 17,
            }).addTo(map);
        });
});
