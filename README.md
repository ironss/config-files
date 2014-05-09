config-files
============


i3 Setup
--------

1. git clone config-files somewhere

2. Create symlinks as follows:

   * .config/i3 -> somewhere/i3
   * .config/i3status -> somewhere/i3status

3. Copy .desktop and .session files to the right places

   * sudo cp i3-gnome/i3-gnome.desktop /usr/share/xsessions/i3-gnome.desktop
   * sudo cp i3-gnome/i3-gnome.session /usr/share/gnome-session/sessions/i3-gnome.session
   
4. Prevent Nautilus from opening desktop
   
   * gsettings set org.gnome.desktop.background show-desktop-icons false
   
   This is a live setting, and removes the background immediately.


