console.log('JavaScript loaded');
// hideAbout();

// Define gloabl variables for use when creating transactions
// var symbol
// var activity

document.addEventListener('DOMContentLoaded', function() {
    page = location.pathname
    if (page === "/transaction/") {
        // If the form is beign rendered a 2nd time, because of errors, show the relevant field
        if (document.getElementsByClassName("alert").length != 0) {
            a = document.getElementById("id_activity").value
            if (["B", "S"].indexOf(a) > -1) {
                document.getElementById("div_id_quantity").style.display = "block"
            } else {
                document.getElementById("div_id_amount").style.display = "block"
            }
        }
    }
})

// getCookie function from Django documentation
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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
    const csrftoken = getCookie('csrftoken')
    const request = new Request(
        `${BASEURL}/updatetitle/${watchlist_id}`,
        {headers: {'X-CSRFToken': csrftoken}}
    )

    fetch(request, {
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

function recordActivity(value) {
    console.log("Activity Selected: ", value)
    if (["B", "S"].indexOf(value) > -1) {
        // document.getElementById("id_quantity").setAttribute("required", "required")
        document.getElementById("div_id_quantity").style.display = "block"
        document.getElementById("id_quantity").value = ""
        document.getElementById("div_id_amount").style.display = "none"
    }
    if (value === 'D') {
        document.getElementById("div_id_quantity").style.display = "none"
        document.getElementById("div_id_amount").style.display = "block"
        document.getElementById("id_amount").value=""
    }
}
