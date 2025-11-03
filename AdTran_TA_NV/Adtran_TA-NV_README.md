# Notes for ADTRAN plays  
Typical execution would be similar to this:
```sh
# Create encrypted variables for ansible_password and ansible_become_password to go in group_vars/adtranTANV.yml
ansible-vault encrypt_string --ask-vault-pass --stdin-name 'ansible_password'
ansible-vault encrypt_string --ask-vault-pass --stdin-name 'ansible_become_password'
# Create an encrypted variable for backup encryption password
ansible-vault encrypt_string --ask-vault-pass --stdin-name 'vault_pass'

# Run the roles using their tags
# Make an encrypted configuration backup of the devices in inventory labled wave1 and collects some facts in a CSV
ansible-playbook adtranTANV.yml --tags backup,get_facts --ask-vault-pass --limit wave1
ls -l backups/DEVICE1.backup
ls -l facts/adtranTANV.csv
# View the encrypted backup
ansible-vault decrypt --output - backups/DEVICE1.backup 
```

> OTHER TAGS:  
>   dry_run - connecte to the devices and get their configs in order to build roles 
>             commands, but do not send the commands
