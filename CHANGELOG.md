Changelog for yeelightsunflower
===============================

0.0.7 (2017-02-25)
------------------

- Don't close socket when there's a send/receive error
- Set availability of lights as False if hub is unavailable


0.0.6 (2017-02-23)
------------------

- Add time check to use cached data instead of fetching new data via TCP. This is useful since multiple bulb objects will get the hub's data in short succession, and all should just use the same values.

0.0.5 (2017-02-17)
------------------
- Make library thread safe with threading.Lock
