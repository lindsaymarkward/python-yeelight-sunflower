# yeelightsunflower

[![Build Status](https://travis-ci.org/lindsaymarkward/python-yeelight-sunflower.svg?branch=master)](https://travis-ci.org/lindsaymarkward/python-yeelight-sunflower)

yeelightsunflower is a Python package for interacting with Yeelight Sunflower light bulbs.

Product details for these bulbs can be found at the following website (but note that they may not be available any more): https://www.yeelight.com/en_US/product/yeelight-sunflower

This library was written primarily to work with Home Assistant: https://home-assistant.io

Communication is via TCP commands, e.g.  
Sending `GL,,,,0,\r\n` to the IP address of the Yeelight hub gets the current state of all lights and would return something like: `GLB 143E,1,1,22,255,10,10,0,0;287B,1,1,64,255,10,10,0,0;0001,1,1,0,255,10,10,0,0;`  

Sending `C 143F,255,0,255,50,\r\n` would set the light identified by `143F` to magenta at 50% brightness.  

The library wraps these commands in a form suitable as a platform for the Home Assistant light platform, and could be used by other modules.  
 
This library does not implement the SSDP hub identification that Yeelight Sunflower hubs support.

An [implementation in Go also exists](https://github.com/lindsaymarkward/go-yeelight)
 
## Console Commands
(Mostly for my reference when needed)

```
# Get state:
echo "GL,,,,0,\r\n" | nc 192.168.1.59 10003
# Response will be something like:
GLB 6532,1,1,92,19,120,255,0,0;3CB8,1,1,25,255,255,108,0,0;50F5,1,1,33,255,255,255,100,0;0002,1,1,44,255,255,255,0,0;0001,1,1,16,255,255,255,0,0;143E,1,1,19,255,255,255,0,0;287B,1,1,14,255,255,255,0,0;3CB9,1,1,33,255,255,255,0,0;4016,1,1,22,19,120,255,0,0;6533,1,0,25,255,255,255,100,0;

# All off:
echo "C G000,,,,0,\r\n" | nc 192.168.1.59 10003
``` 