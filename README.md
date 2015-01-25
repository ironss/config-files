config-files
============


i3 Setup
--------

1. git clone config-files somewhere

2. Create symlinks as follows:

   * cd somewhere
   * mkdir -p ~/.config/i3 && ln -s i3/config ~/.config/i3
   * mkdir -p ~/.config/i3status && ln -s i3status/config ~/.config/i3status
   * mkdir -p ~/bin && ln -s i3-gnome/i3-gnome-logout ~/bin

3. Copy .desktop and .session files to the right places

   * sudo cp i3-gnome/i3-gnome.desktop /usr/share/xsessions/i3-gnome.desktop
   * sudo cp i3-gnome/i3-gnome.session /usr/share/gnome-session/sessions/i3-gnome.session
   
4. Prevent Nautilus from opening desktop
   
   * gsettings set org.gnome.desktop.background show-desktop-icons false
   
   This is a live setting, and removes the background immediately.

5. Turn off unwanted Gnome startup applications
   
   * run gnome-session-properties


Packages to install
-------------------
   * i3
   * i3status
   * gnome-settings-daemon
   * gnome-control-center   (for gnome-sound-applet)
   * python-appindicator    (for logout program)
      
Things to work on
-----------------

1. Unlock default keyring on login

2. Backup is failing

