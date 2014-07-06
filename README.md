weatherboy
==========
Weatherboy is weather tray app written in Python, perfect for lightweight environments (like OpenBox, Awesome, etc.).

![alt text](http://i61.tinypic.com/zjxhuf.png "Weatherboy")

So, there are no additional dependencies, only GTK and Python. 
It fetches weather data from Yahoo! Weather, uses your icon theme for displaying weather icons.
If you click on weather icon, it opens your default web browser with Yahoo! Weather page.
If you are minimalistic person or like to keep things simple - weatherboy is good choice for you.

    zengeist@spectre /tmp/weatherboy (git)-[master] % weatherboy -h
    usage: weatherboy [-h] -l WOEID [-u c|f] [-d N] [-a]
    
    Simple weather applet
    
    optional arguments:
      -h, --help            show this help message and exit
      -l WOEID, --location WOEID
                            location WOEID (more on
                            http://developer.yahoo.com/weather/)
      -u c|f, --units c|f   units to display
      -d N, --delta N       timeout in minutes between next weather data query
      -a, --advanced        Advanced tooltip

Install
--------
Download weatherboy.py and put it where you want.
Weatherboy is available for ArchLinux with AUR, so you can install this way
    yaourt -S weatherboy
or download PKGBUILD and build package manually.
Cause I used ArchLinux before, no packages for another distros are provided.

Prepare and run
--------
Weatherboy uses Yahoo! Weather feed, so at first, you need to go to http://weather.yahoo.com and look for your location.
Weather url for Prague will looks like https://weather.yahoo.com/czech-republic/prague/prague-796597/  
and you will need to copy a location code (796597 in that case)

    weatherboy.py -l 796597 -u c -d 10 -a
It will show you weather for Prague with metric units, tooltip with advenced information and update delta 10min.
