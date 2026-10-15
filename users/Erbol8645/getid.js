var urls;
var id;

fetch("urls.txt")
    .then(response => response.text())
    .then((data) => {
        urls = data.split("\n").filter(url => url.trim() !== ""); // Remove empty lines
        process();
    })
    .catch(error => console.error("Error fetching URLs:", error));

function process() {
    var urlParams = new URLSearchParams(window.location.search);
    id = parseInt(urlParams.get('id')); // Parse id as an integer

    if (isNaN(id) || id < 0 || id >= urls.length) {
        // If id is invalid, try to find it based on the referrer
        id = -1;
        var ref = document.referrer.replace(/[^/]*$/, '');

        for (var i = 0; i < urls.length; i++) {
            var full = new URL(urls[i].trim(), location.href).href;  // list entries can be relative
            if (full === ref || full + "/" === ref) {
                id = i;
                break;
            }
        }

        // If referrer is not found, default to the first URL
        if (id === -1) {
            id = 0;
        }
    }

    // Call activate() after urls and id are initialized
    activate();
}