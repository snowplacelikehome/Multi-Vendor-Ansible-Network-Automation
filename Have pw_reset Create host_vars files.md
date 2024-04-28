# Add plays to pw_reset role that creates host_vars YAML files for each devices with the new random idempotent vault encrypted ansible_password 
```sh
##
cd MikroTik_RouterOS/

## Add pw.vault_pass
vi group_vars/mikrotikros.yml

## Add plays
vi roles/pw_reset/tasks/main.yml

## Add templates
mkdir templates
cd templates
ln -s ../../templates/host_vars.j2 host_vars.j2 
cd ..

## Run the palybook dry_run
ansible-playbook mikrotikros.yml --ask-vault-pass --limit mikrotikcore --tags pw_dry_run

## Check variables in host_vars are loading in ansible_user and ansible_password
ansible --ask-vault-pass -m debug -a "var=hostvars[inventory_hostname]" mikrotikcore

## If the playbook failed before encrypting pw/mikrotikcore.ps, encrypt it again
ansible-vault encrypt --ask-vault-pass pw/mikrotikcore.pw 
```

