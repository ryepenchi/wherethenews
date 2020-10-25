
var map = L.map('llmap').fitWorld();

// var TILE_URL = "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYWhvcm5zaXJ1cCIsImEiOiJjazNqNTBxeHgwM2trM2RydnozbDdwMXMwIn0.0xe5TIh6XSo1pKrjsAUgEA";
var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
var MB_ATTR = 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>';
L.tileLayer(TILE_URL, {
	zoom: 8,
	maxZoom: 18,
	id: 'mapbox/light-v10',
	attribution: MB_ATTR,
	// zoomOffset: -1
}).addTo(map);

function onLocationFound(e) {
	var radius = e.accuracy / 2;

	L.marker(e.latlng).addTo(map)
		.bindPopup("You are within " + radius + " meters from this point").openPopup();

	L.circle(e.latlng, radius).addTo(map);
}

function onLocationError(e) {
	alert(e.message);
}

map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);

map.locate({setView: true, maxZoom: 16});

function renderData() {
	var request = new XMLHttpRequest();
	var from_date = new Date();
	var to_date = new Date();
	var fromrq = "from_date=" + from_date.toISOString();
	var torq = "to_date=" + to_date.toISOString();
	request.open('GET', '/points?' + fromrq + "&" + torq, true);

	request.onload = function() {
		if (this.status >= 200 && this.status < 400) {
			// Success
			var data = JSON.parse(this.response);
			var markers = data.data.map(function(arr) {
				return L.marker([arr[0], arr[1]]).bindPopup(arr[2]);
			});
			map.removeLayer(layer);
			layer = L.layerGroup(markers);
			map.addLayer(layer);
			// Create Cards
			data.data.map(function (arr) {
				var card = document.createElement("div")
				card.className = "card blue-grey lighten-1 collection-item"
				card.innerHTML = `
				<div class="card-content white-text">
				  <span id="card-title" class="card-title">Placename</span>
				  <p id="card-p" class="truncate">Titel des Artikels, könnte auch mal länger sein, aber was solls</p>
				</div>
				<div id="card-action" class="card-action">
				  <a href="#">Link zum Artikel</a>
				</div>
				`
				// card.getElementById("card-title").innerHTML = arr[3];
				// card.getElementById("card-action").innerHTML = arr[4];
				document.getElementById("card-collection").appendChild(card);
			});
		} else {
			//Reached target Server, but it returned an error
			console.log("Mimimi")
		}
	};

	request.onerror = function() {
		//There was a connection error of some sort
	};

	request.send();
	console.log("Lalalalalala")

}
var layer = L.layerGroup();
// renderData();
window.onload = function () {
	renderData();
};