// Initialize Leaflet Map with OSM tiles
function initMap() {
    // Center on Nairobi by default
    var map = L.map('map').setView([-1.2921, 36.8219], 12);

    // Load OSM tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
    }).addTo(map);

    // Markers for pickup and destination
    var pickupMarker, destinationMarker;

    // When user clicks map, set pickup if empty, then destination
    map.on('click', function(e) {
        if (!pickupMarker) {
            pickupMarker = L.marker(e.latlng).addTo(map).bindPopup("Pickup").openPopup();
            document.getElementById("pickup").value = `${e.latlng.lat}, ${e.latlng.lng}`;
        } else if (!destinationMarker) {
            destinationMarker = L.marker(e.latlng).addTo(map).bindPopup("Destination").openPopup();
            document.getElementById("destination").value = `${e.latlng.lat}, ${e.latlng.lng}`;
        }
    });
}

// Run map init when page loads
document.addEventListener("DOMContentLoaded", initMap);



// ---------- Driver Dashboard: Leaflet Map ----------
(function () {
    // only run on pages that have the driver map
    const mapEl = document.getElementById("driver-map");
    if (!mapEl) return;
  
    // Nairobi default center
    const DEFAULT_CENTER = [-1.2921, 36.8219];
    const DEFAULT_ZOOM = 12;
  
    // init map
    const map = L.map("driver-map").setView(DEFAULT_CENTER, DEFAULT_ZOOM);
  
    // OSM tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
    }).addTo(map);
  
    // helpers
    const locInput = document.getElementById("driver-current-location");
    const setLocInput = (latlng) => {
      if (locInput) {
        locInput.value = `${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}`;
      }
    };
  
    let driverMarker = null;
  
    // click-to-set current location
    map.on("click", (e) => {
      const { latlng } = e;
      if (!driverMarker) {
        driverMarker = L.marker(latlng, { draggable: true })
          .addTo(map)
          .bindPopup("Your current location")
          .openPopup();
  
        driverMarker.on("dragend", (evt) => {
          setLocInput(evt.target.getLatLng());
        });
      } else {
        driverMarker.setLatLng(latlng);
      }
      setLocInput(latlng);
    });
  
    // try browser geolocation for convenience
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const latlng = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          map.setView(latlng, 14);
          if (!driverMarker) {
            driverMarker = L.marker(latlng, { draggable: true })
              .addTo(map)
              .bindPopup("Your current location")
              .openPopup();
            driverMarker.on("dragend", (evt) => setLocInput(evt.target.getLatLng()));
          } else {
            driverMarker.setLatLng(latlng);
          }
          setLocInput(latlng);
        },
        // on error -> ignore; user can click map instead
        () => {}
      );
    }
  
    // plot pending rides (pickup & destination). We expect "pickup" and "destination"
    // may be either "lat, lng" pairs or free-text addresses. We'll plot coordinates if present.
    const rides = Array.isArray(window.__PENDING_RIDES__) ? window.__PENDING_RIDES__ : [];
    const markers = [];
    const latLngFromText = (txt) => {
      if (!txt) return null;
      // accept "lat, lng" with optional spaces
      const m = String(txt).trim().match(/^(-?\d+(\.\d+)?)\s*,\s*(-?\d+(\.\d+)?)$/);
      if (!m) return null;
      const lat = parseFloat(m[1]);
      const lng = parseFloat(m[3]);
      if (isNaN(lat) || isNaN(lng)) return null;
      // quick sanity
      if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
      return { lat, lng };
    };
  
    rides.forEach((ride) => {
      const pickupLL = latLngFromText(ride.pickup);
      const destLL = latLngFromText(ride.destination);
  
      if (pickupLL) {
        const m = L.marker(pickupLL).addTo(map).bindPopup(
          `<b>Pickup</b><br/>${ride.pickup}`
        );
        markers.push(m);
      }
      if (destLL) {
        const m = L.marker(destLL).addTo(map).bindPopup(
          `<b>Destination</b><br/>${ride.destination}`
        );
        markers.push(m);
      }
    });
  
    // fit map to all markers (driver + rides)
    const allLayers = [];
    if (driverMarker) allLayers.push(driverMarker);
    markers.forEach((m) => allLayers.push(m));
    if (allLayers.length > 0) {
      const group = L.featureGroup(allLayers.map((l) => l));
      map.fitBounds(group.getBounds().pad(0.2));
    }
  })();
  
