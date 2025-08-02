// Bar chart for crash types
const ctx1 = document.getElementById('impactChart').getContext('2d');
const impactChart = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Number of Crashes',
            data: values,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Crash Count'
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Crash Severity Type'
                }
            }
        }
    }
});

// Line chart for crash frequency by hour
const ctx2 = document.getElementById('hourChart').getContext('2d');
const hourChart = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: hour_labels,
        datasets: [{
            label: 'Number of Crashes by Hour',
            data: hour_counts,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            fill: true,
            tension: 0.3,
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Hour of Day (0–23)'
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Number of Crashes'
                }
            }
        }
    }
});

// Pie Chart: Most Severe Injury
const ctxInjury = document.getElementById('injuryChart');
new Chart(ctxInjury, {
    type: 'pie',
    data: {
        labels: injury_labels,
        datasets: [{
            label: 'Most Severe Injury',
            data: injury_values,
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#8E44AD', '#2ECC71', '#95A5A6'
            ],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            },
            title: {
                display: true,
                text: 'Most Severe Injury per Crash'
            }
        }
    }
});