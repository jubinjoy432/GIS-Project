document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Map
    const map = L.map('heatmap-map').setView([10.0229, 76.3095], 15);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    let heatLayer = null;

    // 2. Initialize Chart
    const ctx = document.getElementById('trendChart').getContext('2d');
    let trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Avg. Vehicle Flow',
                data: [],
                borderColor: '#4bc0c0',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#ccc' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#333' },
                    ticks: { color: '#aaa' }
                },
                x: {
                    grid: { color: '#333' },
                    ticks: { color: '#aaa' }
                }
            }
        }
    });

    // 3. Fetch Data Logic
    const timeSlotSelector = document.getElementById('time-slot');

    async function fetchData(slot) {
        try {
            const response = await fetch(`/api/history?slot=${slot}`);
            const data = await response.json();
            updateDashboard(data);
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }

    function updateDashboard(data) {
        // Update Chart Title
        // document.getElementById('chart-title').textContent = `${data.period_label} Trend`;

        // Update Heatmap
        if (heatLayer) {
            map.removeLayer(heatLayer);
        }

        // Prepare heat points: [lat, lng, intensity]
        // Intensity from backend is 0.0-1.0. Leaflet heat expects intensity.
        const heatPoints = data.heatmap.map(p => [p.lat, p.lng, p.intensity * 20]); // Scale up for visibility

        heatLayer = L.heatLayer(heatPoints, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            gradient: {
                0.2: 'blue',
                0.4: 'lime',
                0.6: 'yellow',
                1.0: 'red'
            }
        }).addTo(map);

        // Update Chart
        const labels = data.trend.map(d => d.time);
        const counts = data.trend.map(d => d.count);

        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = counts;

        // Adjust color based on intensity (optional nice touch)
        // Night = Blueish, Peak = Reddish
        if (data.period_label.includes('Night')) {
            trendChart.data.datasets[0].borderColor = '#36a2eb';
            trendChart.data.datasets[0].backgroundColor = 'rgba(54, 162, 235, 0.2)';
        } else if (data.period_label.includes('Peak')) {
            trendChart.data.datasets[0].borderColor = '#ff6384';
            trendChart.data.datasets[0].backgroundColor = 'rgba(255, 99, 132, 0.2)';
        } else {
            trendChart.data.datasets[0].borderColor = '#4bc0c0';
            trendChart.data.datasets[0].backgroundColor = 'rgba(75, 192, 192, 0.2)';
        }

        trendChart.update();
    }

    // 4. Listeners
    timeSlotSelector.addEventListener('change', (e) => {
        fetchData(e.target.value);
    });

    // Initial Load
    fetchData(timeSlotSelector.value);
});
