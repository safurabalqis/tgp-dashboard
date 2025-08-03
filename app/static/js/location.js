// === Map Setup ===
let locationMap = L.map("map").setView([41.8781, -87.6298], 11);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; OpenStreetMap contributors',
}).addTo(locationMap);

let searchMarker = null;

// === Search & Filter Logic ===
function performSearch() {
    const query = document.getElementById("search").value.trim();
    const metric = document.getElementById("metric-select").value;
    const container = document.getElementById("region-info");

    if (!query) {
        container.innerHTML = "";
        return;
    }

    fetch(`/location/api/streets?q=${encodeURIComponent(query)}&metric=${metric}`)
        .then(res => res.json())
        .then(results => {
            // Sort descending and take top 5
            results.sort((a, b) => b.crash_count - a.crash_count);
            results = results.slice(0, 5);

            if (results.length === 0) {
                container.innerHTML = `<em>No streets found.</em>`;
                return;
            }

            const labelMap = {
                crashes: "Crashes",
                injuries: "Injuries",
                vehicles: "Vehicles"
            };

            const label = labelMap[metric] || "Crashes";

            container.innerHTML = results.map(street => `
                <div class="search-result-item clickable" data-lat="${street.coords[0]}" data-lng="${street.coords[1]}" data-name="${street.name}">
                    <strong>${street.name}</strong> – ${street.crash_count} ${label}
                </div>
            `).join("");

            document.querySelectorAll(".search-result-item").forEach(item => {
                item.addEventListener("click", () => {
                    const lat = parseFloat(item.getAttribute("data-lat"));
                    const lng = parseFloat(item.getAttribute("data-lng"));
                    const name = item.getAttribute("data-name");

                    locationMap.setView([lat, lng], 15);

                    if (searchMarker) locationMap.removeLayer(searchMarker);

                    searchMarker = L.marker([lat, lng])
                        .addTo(locationMap)
                        .bindPopup(`<strong>${name}</strong>`)
                        .openPopup();
                });

                item.addEventListener("mouseover", () => {
                    item.style.backgroundColor = "#f0f8ff";
                    item.style.cursor = "pointer";
                });
                item.addEventListener("mouseout", () => {
                    item.style.backgroundColor = "";
                    item.style.cursor = "default";
                });
            });
        });
}

// === Listeners ===
document.getElementById("search").addEventListener("input", performSearch);
document.getElementById("metric-select").addEventListener("change", performSearch);

// === Reset View ===
document.getElementById("reset-btn").addEventListener("click", () => {
    locationMap.setView([41.8781, -87.6298], 11);
    document.getElementById("search").value = "";

    if (searchMarker) {
        locationMap.removeLayer(searchMarker);
        searchMarker = null;
    }

    const container = document.getElementById("region-info");
    if (container) container.innerHTML = "";
});
