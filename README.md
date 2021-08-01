**The Challenge Game site**

**Showcase your expertise in picking winning Stocks**

This web site is the Capstone Project developed for the CS50's Web Programming with Python and Javascript course.

This site is available to anybody that wants to fine tune their stock picking skills, without risking their hard earned tax dollars against the uncertainty of the financial markets. There is no money to be made, and no money to be lost. All you earn is the bragging rights to the notional profit you would have made executing the same trades in the real _**Stock Market**_.

The site leverages the Yahoo Finance API to retreive General Market Data, News Headlines, and Quotes for individual Stocks.

Following are some of the features of the site:
1.	Upon registration, the user account is allocated a cash credit of $250,000 (CAD) to apply against stock trades
2.	Trading is only permitted for the symbols listed in the TSXStock model. This is necessary to limit the number of API calls required to validate symbols input by the user
3.	A user's portfolio is limited to 10 holding. The portfolio view shows the investment in each of the holdings, the current price, the 52 week target price suggested by the analysts, and profit or loss associated with the holding
4.	The user is assigned 5 Watchlists that can be populated with the stocks of interest. The Watchlist view shows when the item was added to the Watchlist, the price at the time, the current price, and the change in price since the stock was added to the Watchlist
5.	To avoid portfolio churn, the users are limited to a maximum of 10 transactions in a 7 day interval. Dividend transactions are not inlcuded in this count. For the same reason, each Watchlist can hold a maximum of 10 symbols

The Models that support the web Site are; Account, TSXStock, Holding, Transaction, Watchlist, and WatchlistItem.  The ‘signal dispatcher’ is used to complete creation of a User accoutn, and to update the Holdings when a transaction is submitted.

The ‘utils.py’ file defines the functions to retreive Market Data and News Headlines, and combine the Market Data with the Holding and WatchlistItem.

The ‘challenge_extra.py’ file defines the currency filter as suggested in ‘djangosnippets’.
 
The Web Site uses ‘django-bootstrp-v5’. All templates extend from ‘base.html’, with itself extends from ‘bootstrap.html’. As noted, certain sections of ‘base.html’ are adapted from the examples for django-bootstrap-v5.

The Javascript file ‘index.js’ defines the functions to show and hide the appropriate sections of the Transaction Entry page, and perform initial calculations.

To build the runtime environment

    pip install -r requirements.txt

The site requires subscription to the Yahoo Finance API to retreive Market Data used to provide the functionality offered by the site. A Basic API plan ($0.00) offers a **plan quota** of 500 requests per month, which is sufficient to review the full functionality of the site. Instructions on signing up for a free RapidAPI account is available at 
    
    https://docs.rapidapi.com/docs/consumer-quick-start-guide

To secure the API Keys, create a new file `local_settings.py` in the same directory as the `settings.py` file to store the RapidAPI key assigned. The following is an sample of the file contents.

    # RapidAPI Key
    # Required to make API calls to retreive market data and news
    # Imported into the main settings.py file    
    #
    X_RAPIDAPI_KEY = "Insert RapidAPI Key here"

The following lines of code are added to the `settings.py` file to import 'local_settings.py'

    # Import RapidAPI key from local_settings.py
    try:
        from .local_settings import *
    except ImportError:
        pass  # No local_settings file

Sqlite database with sample data is included in the repository. Migration is not required

Superuser credentials:      username: admin     password: admin
Sample user credentials:    username: roger     password: mypwd101
