console.log('JavaScript loaded');
// hideAbout();

document.addEventListener('DOMContentLoaded', function() {
    const page = location.pathname
    if (page === "/transaction/") {
        // If the form is being rendered a 2nd time, because of errors, show the relevant field
        // if (document.getElementsByClassName("alert").length != 0) {
            const a = document.getElementById("id_activity").value
            if (["B", "S"].indexOf(a) > -1) {
                document.getElementById("div_id_quantity").style.display = "block"
                document.getElementById("div_id_price").style.display = "block"
                document.getElementById("id_price").readOnly = true
                document.getElementById("div_id_amount").style.display = "block"
                document.getElementById("id_amount").readOnly = true
            } else if (a === "D") {
                document.getElementById("div_id_amount").style.display = "block"
            }
        // }
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

// function registerDividend() {
//     console.log("Recording Dividend")
//     divident = document.getElementById("id_amount").value
//     console.log("Divident Amount: ", divident)
//
// }

function show_buySell_elem() {
    // Display the quantity, price and amount field. Mark price and amount as readOnly
    // Price and amount field will be populated from the stock quote
    document.getElementById("div_id_quantity").style.display = "block"
    document.getElementById("id_quantity").value = ""
    //
    document.getElementById("div_id_price").style.display = "block"
    document.getElementById("id_price").readOnly = true
    document.getElementById("div_id_amount").style.display = "block"
    document.getElementById("id_amount").readOnly = true
    //
    document.getElementById("market_data").style.display = "block"

    // Add eventlistener to trigger transaction process on focusout
    document.getElementById("id_quantity").addEventListener('focusout', function() {
        processTransaction()
    })
}

function show_dividend_elem() {
    document.getElementById("div_id_quantity").style.display = "none"
    document.getElementById("id_quantity").value="0.00"
    document.getElementById("div_id_price").style.display = "none"
    document.getElementById("id_price").value="0.00"
    //
    document.getElementById("div_id_amount").style.display = "block"
    document.getElementById("id_amount").value=""
    document.getElementById("id_amount").readOnly = false

}

function recordActivity(value) {
    console.log("Activity Selected: ", value)
    if (["B", "S"].indexOf(value) > -1) {
        // // Display the quantity, price and amount field. Mark price and amount as readOnly
        // // Price and amount field will be populated from the stock quote
        // document.getElementById("div_id_quantity").style.display = "block"
        // document.getElementById("id_quantity").value = ""
        // //
        // document.getElementById("div_id_price").style.display = "block"
        // document.getElementById("id_price").readOnly = true
        // document.getElementById("div_id_amount").style.display = "block"
        // document.getElementById("id_amount").readOnly = true
        //
        // // Add eventlistener to trigger transaction process on focusout
        // document.getElementById("id_quantity").addEventListener('focusout', function() {
        //     processTransaction()
        // })

        show_buySell_elem()

        // Get the symbol selected by the user
        const sym_id = document.getElementById("id_symbol").value

        // Get Market Data for the symbol
        const BASEURL = window.location.protocol + "//" + window.location.host
        const csrftoken = getCookie('csrftoken')
        const request = new Request(
            `${BASEURL}/market_quote/${sym_id}`,
            {headers: {'X-CSRFToken': csrftoken}}
        )

        fetch(request, {
            method: "GET",
        })
            .then (response => {
                return response.json()
            })
            .then (data => {
                console.log('Data Received:', data)
                process_quote(data)
            })
            // .then (result => {
            //     console.log('Result:', result)
            // })
            .catch (error => {
                console.log('Error:', error)
            })
            .finally (function() {
                console.log('Finally section of market_quote')
            })
    }

    if (value === 'D') {

        show_dividend_elem()

        // document.getElementById("div_id_quantity").style.display = "none"
        // document.getElementById("id_quantity").value=""
        // document.getElementById("div_id_price").style.display = "none"

        // document.getElementById("div_id_amount").style.display = "block"
        // document.getElementById("id_amount").value=""
        // document.getElementById("id_amount").readOnly = false

        // Add eventlistener to trigger dividend process on focusout
        // document.getElementById("id_amount").addEventListener('focusout', function() {
        //     registerDividend()
        // })
        // document.getElementById("id_amount").addEventListener('pointerout', function() {
        //     registerDividend()
        // })
        // document.getElementById("id_amount").addEventListener('keyup', function(event) {
        //     if (event.keyCode === 13) {
        //         registerDividend()
        //     }
        // })
        // console.log("Event listener added")
    }
}

function process_quote(data) {
    console.log('In process quote')

    // Populate the quote data on the page
    bidask = data.bid + " - " + data.ask
    document.getElementById("bid_ask").innerHTML = bidask
    document.getElementById("day_range").innerHTML = data.regularMarketDayRange
    document.getElementById("volume").innerHTML = data.regularMarketVolume
    document.getElementById("div_yield").innerHTML = data.dividendYield
    document.getElementById("year_range").innerHTML = data.fiftyTwoWeekRange

    const tp = data.targetPriceLow + " - " + data.targetPriceHigh
    document.getElementById("target_price").innerHTML = tp

    price = ((data.bid + data.ask)/2).toFixed(2)
    document.getElementById("id_price").value = price
}

function processTransaction() {
    activity = document.getElementById("id_activity").value
    qty = document.getElementById("id_quantity").value
    price = document.getElementById("id_price").value

    amount = (qty * price).toFixed(2)
    document.getElementById("id_amount").value = amount

    // x = new Intl.NumberFormat('en-US',
    //     {style: 'currency', currency: 'USD'}
    //     ).format(amount)
    //
    // document.getElementById("this_txn").innerHTML = x
    //
    // // Get the cash before the transaction and convert it into a numeric variable
    // cashBefore = document.getElementById("cash_before").innerHTML
    // cashBefore = cashBefore.replace("$", "")
    // cashBefore = cashBefore.replace(",", "")
    //
    // cash = Number(cashBefore)
    //
    // if (activity === "B") {
    //     balance = (cash - amount).toFixed(2)
    // } else {
    //     // This is a sell or dividend transaction
    //     balance = (cash + amount).toFixed(2)
    // }
    //
    // if (balance < 0 ) {
    //     alert("Insufficient funds to cover this transaction")
    // } else {
    //     document.getElementById("cash_after").innerHTML = new Intl.NumberFormat('en-US',
    //     {style: 'currency', currency: 'USD'})
    // }
}
