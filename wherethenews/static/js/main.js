
var map = L.map('llmap').setView([48.517587, 8.648699], 5);

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

function renderData() {
	if (from_date.toLocaleDateString() == to_date.toLocaleDateString()) {
		document.getElementById("dates").innerText = from_date.toLocaleDateString();
	} else {
		document.getElementById("dates").innerText = from_date.toLocaleDateString() + " - " + to_date.toLocaleDateString();
	}
	var request = new XMLHttpRequest();
	var fromrq = "from_date=" + from_date.toLocaleString();
	var torq = "to_date=" + to_date.toLocaleString();
	request.open('GET', '/points?' + fromrq + "&" + torq, true);

	request.onload = function() {
		if (this.status >= 200 && this.status < 400) {
			// Success
			// Create MapMarkers
			var data = JSON.parse(this.response);
			var markers = data.points.map(function(arr) {
				const t = document.createElement("b");
				t.innerHTML = arr.word + "<br>";
				const links = arr.links.map(function (l) {
					//<a href='{a.link}' target='_blank' class='truncate'>{a.title}...</a><br>
					const a = document.createElement("a");
					a.href = l;
					a.className = "truncate";
					a.innerText = l;
					a.target = "_blank";
					const b = document.createElement("br");
					a.append(b);
					t.append(a);
				});
				return L.marker([arr.lat, arr.lon]).bindPopup(t);
			});
			map.removeLayer(layer);
			layer = L.layerGroup(markers);
			map.addLayer(layer);
			// Create Cards
			var myNode = document.getElementById("card-collection");
			while (myNode.firstChild) {
				myNode.removeChild(myNode.firstChild);
			}
			data.articles.map(function (arr) {
				const span = document.createElement("span");
				span.className = "card-title";
				span.innerText = arr.title;
				const para = document.createElement("p");
				para.className = "truncate";
				para.innerHTML = arr.words;
				const d = document.createElement("div");
				d.className = "card-content white-text";
				d.appendChild(span);
				d.appendChild(para);
				// const diva = document.createElement("div");
				// diva.className = "card-action";
				// diva.innerHTML = arr.link;
				const card = document.createElement("div")
				card.className = "card blue-grey lighten-1 collection-item"
				card.appendChild(d);
				// card.appendChild(diva);
				const cardlink = document.createElement("a");
				cardlink.href = arr.link;
				cardlink.target = "_blank";
				cardlink.appendChild(card);
				document.getElementById("card-collection").appendChild(cardlink);
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

function setToToday() {
	today = new Date();
	from_date = new Date(today.getFullYear(), today.getMonth(), today.getDate(),0,0);
	to_date = new Date(today.getFullYear(), today.getMonth(), today.getDate(),23,59);
}

var today, from_date, to_date;
setToToday();
var layer = L.layerGroup();
window.onload = () => renderData();

// Date Buttons
function modDates(f1,t1,f2,t2) {
	if (from_date.toLocaleDateString() == to_date.toLocaleDateString()) {
		from_date.setDate(from_date.getDate()+f1);
		to_date.setDate(to_date.getDate()+t1);
	} else {
		from_date.setDate(from_date.getDate()+f2);
		to_date.setDate(to_date.getDate()+t2);
	}
	renderData();
}

document.getElementById("today").onclick = () => {
	setToToday();
	renderData();
};
document.getElementById("m1d").onclick = () => modDates(-1, -1, -1, -8);
document.getElementById("p1d").onclick = () => modDates(1, 1, 8, 1);
document.getElementById("m1w").onclick = () => modDates(-7, 0, -7, -7);
document.getElementById("p1w").onclick = () => modDates(0, 7, 7, 7);
