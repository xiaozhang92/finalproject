// Google Map
let map;

// Markers for map
let markers = [];

// Info window
let info = new google.maps.InfoWindow();


// Execute when the DOM is fully loaded
$(document).ready(function() {

    // Styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    let styles = [

        // Hide Google's labels
        {
            featureType: "all",
            elementType: "labels",
            stylers: [
                {visibility: "off"}
            ]
        },

        // Hide roads
        {
            featureType: "road",
            elementType: "geometry",
            stylers: [
                {visibility: "on"}
            ]
        }

    ];

    // Options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    let options = {
        center: {lat: 40.7831, lng: -73.9712}, // Manhattan, NY
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 30,
        panControl: true,
        styles: styles,
        zoom: 12,
        zoomControl: true
    };

    // Get DOM node in which map will be instantiated
    let canvas = $("#map-canvas").get(0);

    // Instantiate map
    map = new google.maps.Map(canvas, options);

    // Configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);


});



// Add marker for place to map
function addMarker(place)
{
    var myLatlng = new google.maps.LatLng(place["lat"], place["lng"]);

      //instantiate mark
    var marker = new google.maps.Marker({
        position: myLatlng,
        map: map,
        icon: {
            path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
            scale: 3
          },
    });

    // listen for clicks on marker
    google.maps.event.addListener(marker, 'click', function() {
        // showInfo(marker);

        $.getJSON("/articles",  {geo: place.key}, function(data, textStatus, jqXHR) {

            //only show articles when there are articles
            if (!$.isEmptyObject(data)){
                console.log(data[0].Address)
                //get articles for places
                var article= '<ul>';

                //build list of links to articles
                article += "<li>" + "<strong>"+"Address: " + "</strong>"+ data[0].Address + "</li>";
                article += "<li>" + "<strong>"+"Building Area: "+ "</strong>" + data[0].BldgArea + "</li>";
                article += "<li>" + "<strong>"+ "Shape Area: "+ "</strong>" + data[0].SHAPE_Area.toFixed(2) +" sqf"+ "</li>";
                article += "<li>" + "<strong>"+ "Number of Floors: "+ "</strong>" + data[0].NumFloors + "</li>";
                article += "<li>" + "<strong>"+ "Price per sqft: "+ "</strong>"+"$" + data[0].Price_per_sqft.toFixed(2) + "</li>";

                article += '</ul><br>'
                article += '<input type="hidden" name="skey" value=' + place.key + '>'

                //console.log(place.key)

                article += "<button  class='btnS' type='submit'> Convert </button>"

            }

            else{
                var article= " No articles found."
            }
            showInfo(marker, article);

        })

    });

    //remember maker
    markers.push(marker);

}


// Configure application
function configure()
{
    // Update UI after map has been dragged
    google.maps.event.addListener(map, "dragend", function() {

        // If info window isn't open
        // http://stackoverflow.com/a/12410385
        if (!info.getMap || !info.getMap())
        {
            update();
        }
    });

    // Update UI after zoom level changes
    google.maps.event.addListener(map, "zoom_changed", function() {
        update();
    });

    // Configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>" +
                "{{Address}}, {{ZipCode}}"
                +
                "</div>"
            )
        }
    });

    // Re-center map after place is selected from drop-down
    $("#q").on("typeahead:selected", function(eventObject, suggestion, name) {

        // Set map's center
        map.setCenter({lat: parseFloat(suggestion.lat), lng: parseFloat(suggestion.lng)});
        map.setZoom(16);

        // Update UI
        update();
    });

    // Hide info window when text box has focus
    $("#q").focus(function(eventData) {
        info.close();
    });

    // Re-enable ctrl- and right-clicking (and thus Inspect Element) on Google Map
    // https://chrome.google.com/webstore/detail/allow-right-click/hompjdfbfmmmgflfjdlnkohcplmboaeo?hl=en
    document.addEventListener("contextmenu", function(event) {
        event.returnValue = true;
        event.stopPropagation && event.stopPropagation();
        event.cancelBubble && event.cancelBubble();
    }, true);

    // Update UI
    update();

    // Give focus to text box
    $("#q").focus();
}


// Remove markers from map
function removeMarkers()
{
    // find reference online: https://stackoverflow.com/questions/16482949/google-map-api-removing-markers

    for (var i = 0, n = markers.length; i < n; i++)
    {

	    markers[i].setMap(null);
    }


}


// Search database for typeahead's suggestions
function search(query, syncResults, asyncResults)
{
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/search", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);
    });
}


// Show info window at marker with content
function showInfo(marker, content)
{
    // Start div
    let div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // End div
    div += "</div>";

    // Set info window's content
    info.setContent(div);

    // Open info window (if not already open)
    info.open(map, marker);
}


// Update UI's markers
function update()
{
    // Get map's bounds
    let bounds = map.getBounds();
    let ne = bounds.getNorthEast();
    let sw = bounds.getSouthWest();

    // Get places within bounds (asynchronously)
    let parameters = {
        ne: `${ne.lat()},${ne.lng()}`,
        q: $("#q").val(),
        sw: `${sw.lat()},${sw.lng()}`
    };
    $.getJSON("/update", parameters, function(data, textStatus, jqXHR) {

       // Remove old markers from map
       removeMarkers();
       console.log(data);

       // Add new markers to map
       for (let i = 0; i < data.length; i++)
       {
           addMarker(data[i]);
       }
    });
};
