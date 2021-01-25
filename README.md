config-files
============


i3 Setup
--------

This works for Ubuntu 18.04 with an almost standard Gnome

1. I created a new .config/i3/config file, as the one from
   this repository did not work: I suspect one of the auto-start
   applications was blocking i3 during startup.
   
   Then I manually copied the various settings across to the new
   file as I found somethat the needed to be changed.


2. Create symlinks as follows:

   * cd somewhere
   * mkdir -p ~/.config/i3 && ln -s $PWD/i3/config ~/.config/i3
   * mkdir -p ~/.config/i3status && ln -s $PWD/i3status/config ~/.config/i3status
   * mkdir -p ~/bin && ln -s $PWD/i3-gnome/i3-gnome-logout ~/bin

3. Use Gnome i3 from https://github.com/51v4n/i3-gnome
       git clone https://github.com/51v4n/i3-gnome
       sudo make install
   
4. Turn off unwanted Gnome startup applications
   
   * run gnome-session-properties



Packages to install
-------------------
   * i3
   * i3status
   * python-appindicator    (for logout program)

Programs to install from source
-------------------------------

   * pa-applet (
      
Things to work on
-----------------

1. My i3-gnome-logout is not working

2. There is no suitable sound control applet. pa-applet does not
   compile anymore.
