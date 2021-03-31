const input = document.getElementById("location");
const options = {
    types: ['(cities)'],
    componentRestrictions: { country: "us" },
}

function initAutocomplete() {
    const autocomplete = new google.maps.places.Autocomplete(input, options);
}