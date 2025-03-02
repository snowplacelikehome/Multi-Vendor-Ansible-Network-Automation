# Notes on JunOS device setup for Windows NPS RADIUS auth
JunOS RADIUS AAA device management use the VSA described here: <https://community.juniper.net/discussion/juniper-local-user-name-vsa-with-windows-nps>

# Notes for JunOS plays  
Typical execution would be similar to this:
```sh
# Collect facts and review info
ansible -m junipernetworks.junos.junos_facts -a 'gather_subset="!config"' --tree ./facts --ask-vault-pass junos

# Fist, enable netconf on each device (i.e.: Ansible host)
ansible-playbook junos.yml --extra-vars 'ansible_connection=ansible.netcommon.network_cli' --ask-vault-pass --tags netconf

# Make an encrypted backup the devices' configs
ansible-playbook junos.yml --ask-vault-pass --tags backup
ls -l backups/DEVICE1.backup
# View the encrypted backup
ansible-vault decrypt --output - backups/DEVICE1.backup 

# Get the devices' management interface source IPs (the ones that are needed for acls and the 
# syslog and tacplus/radius source-address commands) and add the src_ipv4 variable for each host
# You must run this step or manually set src_ipv4 for each host if you plan to run the filer_acl rule (if you later plan to specify an of the *_acl tags)
ansible-playbook junos.yml --ask-vault-pass --tags src_ip
cat host_vars/DEVICE1.yml

# Test building the configuration for every service type of role, including their acls, but don't push it to the device
ansible-playbook junos.yml -v --ask-vault-pass --tags netconf_acl,syslog,clear_syslog,syslog_acl,aaa,clear_radius,aaa_acl,ntp,clear_ntp,ntp_acl,config_dry_run
cat config/DEVICE1/all.conf

# Build the configuration for every service type of role, including their acls, push it to the device and commit it
ansible-playbook junos.yml --ask-vault-pass --tags netconf_acl,syslog,clear_syslog,syslog_acl,aaa,clear_radius,aaa_acl,ntp,clear_ntp,ntp_acl
```  
> TAGS:  
> - clear_ntp - includes commands to remove existing ntp targets, otherwise it just adds the new ones  
> - clear_syslog - includes commands to remove existing syslog targets, otherwise it just adds the new one  
> - clear_radius - includes commands to remove existing radius sources (tacplus sources will always be removed), otherwise the aaa role will fail if a radius source exists  
> - *_acl - include ACE's to allow the service's packets through the src_ip's interface if that interface has a filter ACL  

```sh
# Generate a new random password for each device's [group_vars: pw.user] account, encrypt and save it in the pw/ directory.
# It optionally creates an entry in host_vars/DEVICE1.yml, allowing the next playbook run to use that user/pass. 
# It also resets and removes all local user accounts except for the pw.user and aaa.user_templates accounts
# and finishes with recreating the pw.user account as a super-user and resets its and roots passwords 
ansible-playbook junos.yml --ask-vault-pass --tags pw_reset
```  
> TAGS:  
> - make_host_vars - create host_vars/DEVICE1.yml with the new encrypted password, so the same ansible_user can be use to reconnect with the next ansible-playbook run, without this, ansible_user will have 