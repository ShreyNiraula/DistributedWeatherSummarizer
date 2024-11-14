const searchBar = document.getElementById("searchBar");
const suggestionsContainer = document.getElementById("suggestions");
const latitudeDisplay = document.getElementById("latitude");
const longitudeDisplay = document.getElementById("longitude");
const confirmButton = document.getElementById("confirmButton");

let selectedLocation = { lat: null, lon: null };

searchBar.addEventListener("input", async () => {
    const query = searchBar.value;

    if (query.length < 3) {
        suggestionsContainer.style.display = "none";
        return;
    }

    // URL to limit search results to the USA
    const url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&countrycodes=us&q=${encodeURIComponent(query)}`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        suggestionsContainer.innerHTML = "";
        suggestionsContainer.style.display = "block";

        data.forEach(location => {
            const suggestion = document.createElement("div");
            suggestion.textContent = location.display_name;
            suggestion.addEventListener("click", () => {
                // When a location is selected, update lat/lng and enable the confirm button
                selectedLocation = { lat: location.lat, lon: location.lon };
                searchBar.value = location.display_name;
                latitudeDisplay.textContent = location.lat;
                longitudeDisplay.textContent = location.lon;
                suggestionsContainer.style.display = "none";
                confirmButton.disabled = false;  // Enable the confirm button
            });
            suggestionsContainer.appendChild(suggestion);
        });
    } catch (error) {
        console.error("Error fetching location suggestions:", error);
    }
});

// JavaScript to send the POST request without handling the response
confirmButton.addEventListener("click", () => {
    if (selectedLocation.lat && selectedLocation.lon) {
        fetch('/get_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(selectedLocation)
        })
        .then(response => {
            console.log('here')
            console.log("response.redirected", response.redirected)
            if (response.redirected) {
                // If Flask sends a redirect, follow it
                console.log('redirect to')
                console.log(response.url)
                window.location.href = response.url;
            }
        })
        .catch(error => {
            console.error("Error fetching weather data:", error);
        });
    }
});


// Close the suggestions when clicking outside
document.addEventListener("click", (e) => {
    if (!suggestionsContainer.contains(e.target) && e.target !== searchBar) {
        suggestionsContainer.style.display = "none";
    }
});
