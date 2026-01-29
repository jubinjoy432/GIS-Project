document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Map
    // Focusing on Rajagiri Valley/Kochi area
    const map = L.map('map').setView([10.028, 76.308], 15);

    // Dark Mode Map Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    // Layer Group for Markers
    const markersLayer = L.layerGroup().addTo(map);

    // Heatmap Layer
    const beatLayer = L.heatLayer([], {
        radius: 25,
        blur: 15,
        maxZoom: 17,
    }).addTo(map);

    // 2. Initialize Chart
    const ctx = document.getElementById('vehicleChart').getContext('2d');
    const vehicleChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Car', 'Bike', 'Bus', 'Truck'],
            datasets: [{
                label: 'Vehicle Dist.',
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#00d4ff', // Car - Blue
                    '#ffcc00', // Bike - Yellow
                    '#ff4444', // Bus - Red
                    '#44ff44'  // Truck - Green
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#fff' }
                }
            }
        }
    });

    // 3. Fetch Data & Update UI
    function fetchData() {
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                updateDashboard(data);
            })
            .catch(err => console.error('Error fetching data:', err));
    }

    function updateDashboard(data) {
        // Update Total Count
        document.getElementById('total-count').innerText = data.total_vehicles;

        // Update Chart
        const dist = data.distribution;
        vehicleChart.data.datasets[0].data = [
            dist.car, dist.bike, dist.bus, dist.truck
        ];
        vehicleChart.update();

        // Update Heatmap Data
        const heatPoints = data.locations.map(loc => [loc.lat, loc.lng, loc.total]);
        beatLayer.setLatLngs(heatPoints);

        // Update Map Markers (Static Icons instead of Circles)
        markersLayer.clearLayers();
        const alertsList = document.getElementById('alerts-list');
        alertsList.innerHTML = ''; // Clear old alerts

        data.locations.forEach(loc => {
            // Determine Color based on Intensity
            let color = '#44ff44'; // Green (Low)
            if (loc.intensity === 'moderate') color = '#ffcc00';
            if (loc.intensity === 'high') color = '#ff4444';

            // Create Simple Marker for Interaction
            const marker = L.circleMarker([loc.lat, loc.lng], {
                radius: 8, // Fixed small size
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            });

            // Popup Info
            const popupContent = `
                <div style="color: #000; text-align:center;">
                    <h3 style="margin: 0 0 5px;">${loc.name}</h3>
                    <span style="font-size:0.8rem; background:${color}; color:#fff; padding:2px 8px; border-radius:10px;">${loc.intensity.toUpperCase()}</span>
                </div>
            `;

            marker.bindPopup(popupContent);

            // Interaction: Click to View Feed
            marker.on('click', () => {
                const img = document.querySelector('.live-feed-card img');
                const title = document.querySelector('.live-feed-card h3');

                if (img && title) {
                    // Add timestamp to prevent caching
                    img.src = '/video_feed/' + loc.id + '?t=' + new Date().getTime();
                    title.innerText = 'Live Feed: ' + loc.name;
                }
            });

            markersLayer.addLayer(marker);

            // Add Side Panel Alert if High Traffic
            if (loc.intensity === 'high') {
                const li = document.createElement('li');
                li.innerHTML = `<strong style="color: #ff4444;">CONGESTION:</strong> ${loc.name}`;
                alertsList.appendChild(li);
            }
        });
    }

    // Poll every 2 seconds
    setInterval(fetchData, 2000);
    fetchData(); // Initial Call
});
