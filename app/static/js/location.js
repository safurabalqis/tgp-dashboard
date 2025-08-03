// static/js/location.js

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const resultBox = document.getElementById("search-results");

    input.addEventListener("input", () => {
        const query = input.value.trim();

        if (query.length < 2) {
            resultBox.innerHTML = "";
            return;
        }

        fetch(`/location/api/search?q=${encodeURIComponent(query)}`)
            .then((res) => res.json())
            .then((data) => {
                resultBox.innerHTML = "";

                if (data.length === 0) {
                    resultBox.innerHTML = `<div class="list-group-item">No crashes found in this location</div>`;
                    return;
                }

                data.forEach((crash) => {
                    const item = document.createElement("div");
                    item.className = "list-group-item";

                    item.innerHTML = `
                        <strong>Crash ID:</strong> ${crash.id}<br>
                        <strong>Date:</strong> ${formatDate(crash.date)}<br>
                        <strong>Reason:</strong> ${crash.reason}<br>
                        <strong>Injuries:</strong> ${crash.injuries || 0}<br>
                        <strong>Vehicles Involved:</strong> ${crash.vehicles}
                    `;

                    resultBox.appendChild(item);
                });
            });
    });
});

function formatDate(rawDate) {
    const [y, m, d] = rawDate.split("-");
    return `${d}/${m}/${y}`;
}
