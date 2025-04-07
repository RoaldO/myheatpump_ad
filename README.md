myheatpump_ad
=============

myheatpump integration in appdaemon. Home assistant wrapper for myheatpump.com

**THIS SOLUTION IS ABSOLUTELY WITHOUT WARRANTY!**

**USE AT YOUR OWN RISK!**

caveat
------
Since it is a very generic platform and every heat pump installation is unique,
it requires quite a bit of configuration, and it also requires logging into the
website with your web browser to intercept and investigate the http calls being
made.

**Don't say I didn't warn**

Installation
------------
1. Install AppDaemon following the official guides
2. Copy the file `myheatpump.py` to the `apps` folder in your AppDeamon
   environment. There should already by a `hello.py` in that folder by default.
3. In this same folder is a file called `apps.yaml` that needs to be edited.
   Add a section as described in the section _Configuration_.

Configuration
-------------
The app needs to be configured by adding the following configuration to the 
`apps.yaml` file:
```yaml
myheatpump:
  module: myheatpump
  class: MyHeatPump
```
(Watch out, no extra whitespaces before `myheatpump`)

as siblings of the `module` and `class` parameters you also need the following 
parameters:

`username`: this of course the username you use to connect to myheatpump.com
`password`: and of course this is the password to connect
`session_url`: when you log in to the website and follow the network traffic, 
  you'll see that there is a call that returns a cookie with name `JSESSIONID`.
  The url that returned this cookie is the `session_url` to fill in.
`mn`: I think this is the id of the installation site, and you can also find 
  this value using the network tab in your webbrowser.
`devid`: this is probably the device id within the installtaion site. This value
  can also be found using the developer tools of your web browser.
`sensors`: is a dict like configuration of, where the key is the entity_id to 
  use. The value of each item is also a dict like with the keys `parameter` and 
  `unit_of_measurement`. The value of `parameter` is the name of a sensor value
  that the website returns. Expect it to be something like `par24`. The 
  `unit_of_measurement` is that value of the `unit_of_measurement` attribute of
  the sensor. This is probably something like `°C`, `°F`.

Note: You can have multiple sensors and their `unit_of_measurement` is not limited to
the 2 values I described. Use anything you need here.
