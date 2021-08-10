**The Challenge Game site**

**Showcase your expertise in picking winning Stocks**

This web site is the Capstone Project developed for the CS50's Web Programming with Python and Javascript course.

This site is available to anybody that wants to fine tune their stock picking skills, without risking their hard earned tax dollars against the uncertainty of the financial markets. There is no money to be made, and no money to be lost. All you earn is the bragging rights to the notional profit you would have made executing the same trades in the real _**Stock Market**_.

The site leverages the Yahoo Finance API to retrieve General Market Data, News Headlines, and Quotes for individual Stocks.

**Distinctiveness and Complexity**

The Challenge Game site involves trading securities based on the real time market price of the security. The site processes the transaction at the mid-point between the 'bid' and 'ask' for the security being traded, immediately updating the participants cash balance. The local processing of the transactions, allows users to submit trades at any time, independent of the Stock Market hours. The functionality of the project makes it distinct from the other projects in the course.

The complexity of the project revolves around validating each transaction confirms to the numerous business rules. Another area of complexity is the interface to the Yahoo Finance API, and the associated error handling.

**Project Functionality**

Following are some of the features of the site:
1.	Upon registration, the user account is allocated a cash credit of $250,000 (CAD) to apply against stock trades
2.	Trading is only permitted for the symbols listed in the TSXStock model. This is necessary to limit the number of API calls required to validate symbols input by the user
3.	A user's portfolio is limited to 10 holding. The portfolio view shows the investment in each of the holdings, the current price, the 52 week target price suggested by the analysts, and profit or loss associated with the holding
4.	The user is assigned 5 Watchlists that can be populated with the stocks of interest. The Watchlist view shows when the item was added to the Watchlist, the price at the time, the current price, and the change in price since the stock was added to the Watchlist. Each watchlist can hold a maximum of 10 symbols.
5.	To avoid portfolio churn, the users are limited to a maximum of 10 transactions in a 7 day interval. Dividend transactions are not included in this count.


The Models that support the web Site are:
  Account - Users Name and Address and Cash Balance
  TSXStock - Symbol and Company Name of the Securities permitted for trading
  Holding - Details on the shares owned by the user
  Transaction - Details of the Transactions executed by the user
  Watchlist - Watchlist Id and Title for the 5 Watchlists automatically created for each user
  WatchlistItem - Details of the Symbols listed under each Watchlist for the user
  
The ‘signal dispatcher’ is used to complete creation of a User account, and to update the Holdings when a transaction is submitted.

The ‘utils.py’ file defines the functions to retrieve Market Data and News Headlines, and combine the Market Data with the Holding and WatchlistItem.

The ‘challenge_extra.py’ file defines the currency filter as suggested in ‘djangosnippets’.
 
The Web Site uses ‘django-bootstrp-v5’. All templates extend from ‘base.html’, with itself extends from ‘bootstrap.html’. As noted inline, certain sections of ‘base.html’ are adapted from the examples for django-bootstrap-v5.

The Javascript file ‘index.js’ defines the functions to show and hide the appropriate sections of the Transaction Entry page, and perform initial calculations.

To build the runtime environment

    pip install -r requirements.txt

The site requires subscription to the Yahoo Finance API to retrieve Market Data used to provide the functionality offered by the site. A Basic API plan ($0.00) offers a **plan quota** of 500 requests per month, which is sufficient to review the full functionality of the site. Instructions on signing up for a free RapidAPI account is available at 
    
    https://docs.rapidapi.com/docs/consumer-quick-start-guide

To secure the API Keys, create a new file `local_settings.py` in the same directory as the `settings.py` file to store the RapidAPI key assigned. The following is an sample of the file contents.

    # RapidAPI Key
    # Required to make API calls to retrieve market data and news
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

Superuser credentials:      username: _admin_     password: _admin_

Sample user credentials:    username: _roger_     password: _mypwd101_
