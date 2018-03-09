Changelog for yeelightsunflower
===============================

0.0.9 (2018-03-09)
------------------

- Handle and log invalid responses when getting lights (avoid IndexError)
        

0.0.8 (2017-02-25)
------------------

- Correct problem with CHANGELOG missing in PyPi package (update MANIFEST.in) 


0.0.7 (2017-02-25)
------------------

- Try to reconnect socket when there's a send/receive error 
- Set availability of lights to False if hub is unavailable


0.0.6 (2017-02-23)
------------------

- Add time check to use cached data instead of fetching new data via TCP. This is useful since multiple bulb objects will get the hub's data in short succession, and all should just use the same values.

0.0.5 (2017-02-17)
------------------
- Make library thread safe with threading.Lock
