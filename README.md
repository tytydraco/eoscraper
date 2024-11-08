# eoscraper
Essentialoils.org database scraper.

# Setup
Copy `example.env` to `.env` and insert the relevant cookies and payload data. You can find this data by logging in to your essentialoils.org account and navigating to https://essentialoils.org/db while having the browser network debug menu open. You should see a GET request like this: `compound?fields=id,name,name_sort,CAS`. Click on this and take the following data:

* XSRF_TOKEN: `Cookies -> XSRF-TOKEN`
* LARAVEL_SESSION: `Cookies -> laravel_session`
* LARAVEL_TOKEN: `Cookies -> laravel_token`
* LARAVEL_SESSION: `Headers -> X-Csrf-Token`

# Usage
`python scrape.py`
