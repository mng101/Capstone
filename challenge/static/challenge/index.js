console.log('JavaScript loaded');
hideAbout();

function titleUpdate(watchlist_id) {
    console.log("Watchlist title update")
    console.log(watchlist_id)

    let title = document.getElementById("new_title").value;

    if (title.length === 0) {
        console.log("Cannot submit a Null Title")
        alert("Cannot submit a Null Title")
        return false
    }

    // BASE_URL = window.location.href;
    const BASEURL = window.location.protocol + "//" + window.location.host

    fetch(`${BASEURL}/updatetitle/${watchlist_id}`, {
        method: "PUT",
        body: JSON.stringify({title:title})
    })
        .then ( response => {
            console.log('Response:', response);
        })
        .then (result => {
            console.log('Result:', result);
        })
        .catch (error => {
            conosle.log('Error:', error);
        })
        .finally (function() {
            console.log("Finally section of Update Watchlist Title")
        })

}

function showAbout() {
    console.log('About clicked');
    document.getElementById("about").style.display = "block";
}

function hideAbout() {
    document.getElementById("about").style.display = "none";
}
