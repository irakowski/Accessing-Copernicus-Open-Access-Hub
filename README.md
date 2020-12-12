## Accessing Copernicus Open Access Hub

Account @ Copernicus is needed in order to access Open Access Hub.

``s.auth = ('your_username', 'your_password')``

1. Python script establishes connection with API. 
2. Fetches 3 randomly selected products within 2 days daterange.
Due to high change of timeouts for older products, 
the range for number of product results got decreased by 100 times.

``number_of_products = max(map(int, range_list))//100.``

3. Fetches download links for selected products. 
4. Creates local database.
5. Downloads selected products.
6. Checks downloaded files md5checksum.
6. Saves filename, path, and md5checksum to database if both, downloaded file checksum and checksum provided by Open Access match.

![Program flow](assets/34.png?raw=true)



### API documentation for Open Access Hub available @ https://scihub.copernicus.eu/userguide/WebHome