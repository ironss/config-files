mbsync service
##############

Systemd timer and service files for synchronising mailboxes using mbsync.
Needs the following

* 

Overview
========

* mbsync can synchronise IMAP and Maildir mailboxes ('mailstores' in mbsync jargon).
* mbsyc is configured using a single RC file ~/.mbsyncrc (or %h/.mbsyncrc in systemd jargon)
* In mbsync, a 'channel' is a sync-configuration between two mailstores. The
  channel is given a unique name.
* These systemd configuration files use that channel name to tie together
    * a systemd timer configuration file
    * a systemd service configuration file
    * the mbsync channel
    
* The system timer file is unique per channel, to allow different timing    
* The systemd service files are instance-specific


Activate a service
==================

* 
