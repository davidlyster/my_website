

## Quick start

> UNZIP the sources or clone the private repository. After getting the code, open a terminal and navigate to the working directory, with product source code.

```bash
$ # Virtualenv modules installation (Unix based systems)
$ cd my_website
$ virtualenv env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Storage
$ pip3 install -r requirements.txt
$
$ # Create tables
$ python manage.py makemigrations
$ python manage.py migrate
$
$ # Start the application (development mode)
$ python manage.py runserver # default port 8000
$
$ # Start the app - custom port
$ # python manage.py runserver 0.0.0.0:<your_port>
$
$ # Access the web app in browser: http://127.0.0.1:8000/
```

> Note: To use the app, please access the registration page and create a new user. After authentication, the app will unlock the private pages.

<br />

## Packages

Packages that will neeed to be installed in your environment: Tweepy, Pandas, Pandas DataReader, YFinance (Yahoo! Finance API)

```bash
pip3 install tweepy
pip3 install pandas
pip3 install pandas_datareader
pip3 install yfinance
```

## Yahoo Finance API 

- The API is provided by rapidAPI @ https://rapidapi.com/apidojo/api/yahoo-finance1 (*note: cannot seem to log in on chrome*). A free subscription allows for 500 API calls a day.
- The endpoint used is stock/v3/get-historical-data and can be found/searched on the left hand side of the page in the Endpoints tab.
- Once selected the code block on the right will provide some sample code on how to use the API, make sure to select Node.js->Axios if copying from here. This code will also contain your access keys.

## Boilerplate Template Provider

> Free product - **Black Django Dashboard** template

[Black Dashboard Django](https://www.creative-tim.com/product/black-dashboard-django) - Provided by [Creative Tim](https://www.creative-tim.com/) and [AppSeed](https://appseed.us)
