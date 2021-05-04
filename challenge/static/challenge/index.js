console.log('JavaScript loaded');
hideAbout();

function showAbout() {
    console.log('About clicked');
    document.getElementById("about").style.display = "block";
}

function hideAbout() {
    document.getElementById("about").style.display = "none";
}
