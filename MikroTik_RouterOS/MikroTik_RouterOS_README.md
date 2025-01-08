# Notes on MikroTik RouterOS device setup for Windows NPS RADIUS auth
MikroTik RouterOS RADIUS AAA device management uses the VSA described here: <https://forum.mikrotik.com/viewtopic.php?t=174229>

# Notes for MikroTik RouterOS plays  
Typical execution would be similar to this:

# Make an encrypted backup the devices' configs
ansible-playbook mikrotikros.yml --ask-vault-pass --tags backup
# Same thing, but limit to the one host or group
ansible-playbook mikrotikros.yml --ask-vault-pass --tags backup --limit DEVICE1
ls -l backups/DEVICE1.backup
# View the encrypted backup
ansible-vault decrypt --output - backups/DEVICE1.backup 

# Get the devices' management interface source IPs (the ones that are needed for acls and the 
# syslog and tacplus/radius source-address commands) and add the src_ipv4 variable for each host
# You must run this step or manually set src_ipv4 for each host if you plan to run the filer_acl rule (if you later plan to specify an of the *_acl tags)
ansible-playbook mikrotikros.yml --ask-vault-pass --tags src_ip
cat host_vars/DEVICE1.yml

# Test building the configuration for every service type of role, but don't push it to the device
ansible-playbook mikrotikros.yml -v --ask-vault-pass --tags syslog,clear_syslog,aaa,clear_radius,ntp,clear_ntp,config_dry_run
cat config/DEVICE1/all.conf

# Build the configuration for every service type of role, push it to the device and commit it
ansible-playbook mikrotikros.yml --ask-vault-pass --tags syslog,clear_syslog,aaa,clear_radius,ntp,clear_ntp
```  
> TAGS:  
> - clear_ntp - includes commands to remove existing ntp targets, otherwise it just adds the new ones  
> - clear_syslog - includes commands to remove existing syslog targets, otherwise it just adds the new one  
> - clear_radius - includes commands to remove existing radius sources, otherwise the aaa role will fail if a radius source exists  

```sh
# Generate a new random password for each device's [group_vars: pw.user] account, encrypt and save it in the pw/ directory.
# It optionally creates an entry in host_vars/DEVICE1.yml, allowing the next playbook run to use that user/pass. 
# It also resets and removes all local user accounts except for the pw.user and aaa.user_templates accounts
# and finishes with recreating the pw.user account as a super-user and resets its and roots passwords 
ansible-playbook mikrotikros.yml --ask-vault-pass --tags pw_reset
```  
> TAGS:  
> - make_host_vars - create host_vars/DEVICE1.yml with the new encrypted password, so the same ansible_user can be use to reconnect with the next ansible-playbook run, without this, ansible_user will have 

## Troubleshooting
```sh
# Set the ANSIBLE_LOG_PATH and use -vvvv to get details about the network connections
ANSIBLE_LOG_PATH=/tmp/ansible.log ansible-playbook mikrotikros.yml -vvvv --ask-vault-pass --tags backup --limit mikrotik1

#
# Review inventory variables for a host (without decrypting vault variables)
ansible-inventory --host mikrotik1

#
# Review inventory variables for a host (with decrypted vault variables)
ansible --ask-vault-pass -m debug -a "var=hostvars[inventory_hostname]" mikrotik1
```
