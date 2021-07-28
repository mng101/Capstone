**The Challenge Game site**

This web site is the Capstone Project developed for the CS50's Web Programming with Python and Javascript course.

This site is available to anybody that wants to fine tune their stock picking skills, without risking their hard earned tax dollars against the uncertainty of the financial markets. There is no money to be made, and no money to be lost. All you earn is the bragging rights to the notional profit you would have made executing the same trades in the real _**Stock Market**_.

To build the runtime environment

    pip install -r requirements.txt

The site requires subscription to the Yahoo Finance API to retreive Market Data used to provide the functionality offered by the site. A Basic API plan ($0.00) offers a **plan quota** of 500 requests per month, which is sufficient to review the full functionality of the site. Instructions on signing up for a free RapidAPI account is available at 
    
    https://docs.rapidapi.com/docs/consumer-quick-start-guide

Create a new file `local_settings.py` in the same directory as the `settings.py` file to store the RapidAPI key assigned. The following is an sample of the file contents.

    # RapidAPI Key
    # Required to make API calls to retreive market data and news
    # Imported into the main settings.py file    
    #
    X_RAPIDAPI_KEY = "Insert RapidAPI Key here"

The following lines of code are added to the `settings.py` file to import in the RapidAPI key

    # Import RapidAPI key from local_settings.py
    try:
        from .local_settings import *
    except ImportError:
        pass  # No local_settings file

Sqlite database with sample data is included in the repository. Migration is not required

Superuser credentials:      username: admin     password: admin
Sample user credentials:    username: roger     password: mypwd101
