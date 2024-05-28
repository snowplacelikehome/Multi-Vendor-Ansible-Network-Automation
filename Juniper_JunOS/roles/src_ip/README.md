Role Name
=========

This role is meant to determine an IPv4 address the device should use as it's source address when configuring services like syslog radius to make outbound connections from the device.

tasks/main.yml attempts to do this by searching for the most common management and loopback interfaces that typically get a management IP assigned and if it has an IPv4 configure a host_vars file the device with a src_ipv4 variable set to that IP.

tasks/src_via_messages_log.yml provides an alternative approach by connecting to the device and checking the messages log to see if it contains the IP the device was listening on, assuming that would be the best IP to use for it's other services. It could be renamed to main.yml if needed.

Requirements
------------


Role Variables
--------------

None

Dependencies
------------

The netconf role need to be run before this will work.

Example Playbook
----------------

License
-------

Author Information
------------------


