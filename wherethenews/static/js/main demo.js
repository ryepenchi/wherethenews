// BASECOORDS = [-13.9626, 33.7741];
BASECOORDS = [48.210033,16.363449]

function makeMap() {
    var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
    var MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    mymap = L.map('llmap').setView(BASECOORDS, 8);
    L.tileLayer(TILE_URL, {attribution: MB_ATTR}).addTo(mymap);
}

var layer = L.layerGroup();

// function renderData(districtid) {
//     $.getJSON("/district/" + districtid, function(obj) {
//         var markers = obj.data.map(function(arr) {
//             return L.marker([arr[0], arr[1]]).bindPopup(arr[2]);
//         });
//         mymap.removeLayer(layer);
//         layer = L.layerGroup(markers);
//         mymap.addLayer(layer);
//     });
// }

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
            mymap.removeLayer(layer);
            layer = L.layerGroup(markers);
            mymap.addLayer(layer);
        } else {
            //Reached target Server, but it returned an error
            console.log("Mimimi")
        }
    };

    request.onerror = function() {
        //There was a connection error of some sort
    };

    request.send();

}

function $(x) {return document.getElementById(x);}

$(function() {
    makeMap();
    renderData('0');
    $('#distsel').change(function() {
        var val = $('#distsel option:selected').val();
        renderData(val);
    });
})

// document.getElementById(
//     function() {
//         makeMap();
//         renderData('0');
//         document.getElementById('distsel').change(
//             function() {
//                 var val = document.getElementById('distsel option:selected').val();
//                 renderData(val);
//             }
//         );
//     }
// );