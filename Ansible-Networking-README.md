# Multi-Vendor/Model Ansible Networking Automation Example

> based on the structure of this repo: <https://gitlab.com/stuh84/network-automation-ansible>

## Getting Started Overview
1. Setup your Linux/Ansible/Python environment
2. Clone this to a linux host where Ansible is installed
3. Edit the hosts.yml files to match your devices
4. Edit the group_vars_all.yml file to match your general networking environment
    - Each ```Vendor_Model```/group_vars/all.yml is linked to this one file
5. Edit the group_vars/```vendormodel```.yml files within each of your Vendor_Model folders
    - Adjust variables to match your devices
    - Generate Ansible vault password vars for each of your network devices / device groups
6. Edit each ```Vendor_Model```/roles/```Service_Name```/tasks/main.yml to define details of the playbook's tasks
    - Define the appropriate device cli commands and how the tasks will run them
7. Run the playbooks from withing the ```Vendor_Model``` folders

## Install required ansible and python packages
```sh
sudo apt install ansible ansible-lint
# needed for ansible cliconf
sudo apt install python3-paramiko
# needed for ansible.netcommon.net_get
sudo apt install python3-scp
# needed for ansible.builtin.expect module
sudo apt install python3-pexpect
# if you need to debug custom modules
sudo apt install python3-pip
sudo pip install epdb
```

## Setup Ansible Galaxy community modules in the current user profile
```sh
ansible-galaxy collection install community.network
ansible-galaxy collection install community.ciscosmb
ansible-galaxy collection list
# community.routeros is very outdated, so update it
ansible-galaxy collection install community.routeros
```

## Clone this example project to your Ansible script location

```sh
git clone https://github.com/snowplacelikehome/Multi-Vendor-Ansible-Network-Automation.git
cd Multi-Vendor-Ansible-Network-Automation
```

### Creating new Vendor_Model playbook (or customize an existing)
```sh
# 1. 
# Duplicate another Vendor_Model (Example below) if needed
cp -a Cisco_SMB Juniper_SRX
cd Juniper_SRX

# 2.
# Reference: <https://docs.ansible.com/ansible/latest/network/getting_started/first_inventory.html>  
# Edit the group, host names and IPs with your favorite editor or run some search/replace commands
vi hosts.yml
#perl -pni -e 's/ciscosmb/junipersrx/; s/ciscocore/juniperfw1/; s/(ansible_host:)\s+.*/\1 10.1.1.4/' hosts.yml
perl -pni -e 's/ciscosmb/junipersrx/;' hosts.yml # replace a group
perl -pni -e 's/ciscocore/juniperfw1/;' hosts.yml # replace a host
perl -pni -e 's/(ansible_host:)\s+.*/\1 10.1.1.4/;' hosts.yml # change all the IPs to 

# 3.
# Add encrypted vault strings for the local admin password of all Juniper SRX models. If unique
# passwords are used per host add these vault passwords to host_vars/[HOSTNAME].yml files
# After executing the command, type/paste the password and hit CTRL-D twice without a newline
# Then edit group_vars/junipersrx.yml and move the content to the correct spot in the file
ansible-vault encrypt_string --ask-vault-pass --name 'ansible_password' >> group_vars/junipersrx.yml
# Generate RADIUS/TACACS+ shared_secret vault strings like the admin password above
ansible-vault encrypt_string --ask-vault-pass --name 'shared_secret' >> group_vars/junipersrx.yml
vi group_vars/junipersrx.yml

# 4.
# Edit the playbook for each role (backup, aaa, ntp, syslog, pw_reset) to define the commands/tasks unique to this model 
vi roles/backup/tasks/main.yml

# 5.
# Create completely new roles for this model
ansible-galaxy init roles/new_role
vi roles/new_role/tasks/main.yml
# include the new role in the main playbook
vi junipersrx.yml
```

### Folder structure of a vendor_model playbook

| Path                          | Description                                           |
|-------------------------------|-------------------------------------------------------|
|.                              |  |
|├── ansible.cfg -> ../ansible.cfg | config options for Ansible |
|├── ciscosmb.yml               | Main playbook for Cisco SMB |
|├── hosts.yml                  | Invnetory of Cisco SMB hosts |
|├── group_vars                 | |
|.   ├── all.yml -> ../../group_vars_all.yml | variables applied to all vendors and models |
|.   └── ciscosmb.yml           | variables specific to this model |
|├── host_vars                  | |
|.   └── ciscocore.yml          | variables specific to this host |
|└── roles                      | tasks to configure the roles for this model |
|.   ├── backup                 | |
|.   │   └── tasks              | |
|.   │       └── main.yml       | tasks for the backup role |
|.   ├── aaa                    | |
|.   │   └── tasks              | |
|.   │       └── main.yml       | tasks for the aaa role |
|.   ├── ntp                    | |
|.   │   └── tasks              | |
|.   │       └── main.yml       | tasks for the ntp role |
|.   ├── syslog                 | |
|.   │   └── tasks              | |
|.   │       └── main.yml       | tasks for the syslog role |
|.   └── pw_reset               | |
|.       └── tasks              | |
|.           └── main.yml       | tasks for the pw_reset role |

# Common Ansible commands used

### Check ansible facts
```sh
# Cisco SMB switches don't behave enough like IOS to work effectively
#ansible ciscocore -m ios_facts --tree ./facts --ask-vault-pass

#
# community.ciscosmb cliconf comes from `ansible-galaxy collection install community.ciscosmb` and is in ~/.ansible/collections/ansible_collections/community/ciscosmb
ansible ciscocore -m community.ciscosmb.facts --tree ./facts --ask-vault-pass
# facts will be all null values for these two
ansible unifiattic -m edgeos_facts --tree ./facts --ask-vault-pass
ansible unififamilyrm -m edgeos_facts --tree ./facts --ask-vault-pass
# community.network.routeros facts/cliconf comes from the base Ubuntu Ansible install and is in /usr/lib/python3/dist-packages/ansible_collections/community/network/plugins
ansible mikrotikcore -m community.network.routeros_facts --tree ./facts --ask-vault-pass
python3 -m json.tool facts/ciscocore > facts/ciscocore.json
#python3 -m json.tool facts/unifiattic > facts/unifiattic.json
#python3 -m json.tool facts/unififamilyrm > facts/unififamilyrm.json
python3 -m json.tool facts/mikrotikcore > facts/mikrotikcore.json
```

### Typical Playbook Commands to run playbooks in the Vendor_Model folder structure
```sh
#
# limit (-l, --limit) to host names that match 'ciscocore' pattern (https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html)
cd Cisco_SMB
ansible-playbook ciscosmb.yml --ask-vault-pass --limit ciscocore --tags backup

#
# use a different inventory file than the one specified in ansible.cfg
ansible-playbook ciscosmb.yaml -i hosts.yml --list-tags

# select the dry-run tagged tasks only
ansible-playbook ciscosmb.yml --ask-vault-pass --tags backup-dry-run

#
# edgeswitchash cliconf is custom and the paths to is's source need to be in ./ansible.cfg or added to environment variables 
ANSIBLE_TERMINAL_PLUGINS="./terminal_plugins" ANSIBLE_CLICONF_PLUGINS="./cliconf_plugins" ansible-playbook edgeswitchash.yml --ask-vault-pass --limit unifiattic

#
# Review inventory variables for a host (without decrypting vault variables)
ansible-inventory --host ciscocore

#
# Review inventory variables for a host (with decrypted vault variables)
ansible --ask-vault-pass -m debug -a "var=hostvars[inventory_hostname]" ciscocore
```

## Writing and Debuggin Cliconf
> [Ansible Environment Variables for Cliconf](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_CLICONF_PLUGINS)  
> [Ansible Developer Guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html#developer-guide)  
>    [Developing network_cli plugins](https://docs.ansible.com/ansible/latest/network/dev_guide/developing_plugins_network.html#developing-network-cli-plugins)  
>    [Debugging Modules](https://docs.ansible.com/ansible/latest/dev_guide/debugging.html#debugging-modules)  
>    [Enhanced Python Debugger](https://pypi.org/project/epdb/)  
>    [PDB Cheatsheet](https://ugoproto.github.io/ugo_py_doc/pdf/Python-Debugger-Cheatsheet.pdf)

```sh
vi cliconf_plugins/edgeswitchash.py
# Add epdb trace point
#> class Cliconf(CliconfBase):
#    import epdb; epdb.set_trace()

ANSIBLE_KEEP_REMOTE_FILES=1 ANSIBLE_TERMINAL_PLUGINS="./terminal_plugins" ANSIBLE_CLICONF_PLUGINS="./cliconf_plugins" ansible unifiattic -m cli_command -a "command='show run'" --ask-vault-pass -vvv

```

# References  
> - General [Ansible Tips and Tricks](https://docs.ansible.com/ansible/latest/tips_tricks/sample_setup.html)  
>    * [Sample Setup - file tree](https://docs.ansible.com/ansible/latest/tips_tricks/sample_setup.html#sample-setup)  
> - [Ansible Network Getting Started](https://docs.ansible.com/ansible/latest/network/getting_started/index.html)  
>    * Building Inventory  
>    * Network Roles  
> - [Network Advanced Topics - User Guide](https://docs.ansible.com/ansible/latest/network/user_guide/index.html)  
>    * Ansible Network Examples - Platform Specific and Platform Independent modules  
>    * The Platform Independent modules are likely the best solution in environments with a diverse inventory of vendors and models: [Simplified playbook with cli_command platform independe module](https://docs.ansible.com/ansible/latest/network/user_guide/network_best_practices_2.5.html#example-2-simplifying-playbooks-with-platform-independent-modules)
> - [Platform Specific Options](https://docs.ansible.com/ansible/latest/network/user_guide/platform_index.html#settings-by-platform)  
> - [Collections Index](https://docs.ansible.com/ansible/latest/collections/index.html)  
>    * Cisco.IOS command, facts, VLANs, cliconf...
>        <https://docs.ansible.com/ansible/latest/collections/cisco/ios/index.html#plugin-index>  
>    * MikroTik command, facts, VLANs, cliconf... 
>        <https://docs.ansible.com/ansible/latest/collections/community/routeros/index.html#plugins-in-community-routeros>  
>    - [Collections - Platform Independent - Ansible.Netcommon Collection (cli_command, cli_config...)](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html)  
>       * Makes use of [Cliconf Plugins](https://docs.ansible.com/ansible/latest/plugins/cliconf.html#cliconf-plugins)  
>       * Good Introduction article for cli_command/cli_config [Deep Dive cli_command for network automation](https://www.ansible.com/blog/deep-dive-on-cli-command-for-network-automation)  
>    - [Collections - Community.Network Plugin Index](https://docs.ansible.com/ansible/latest/collections/community/network/index.html#plugin-index>)  
>       * Platform specific command, config, facts, cliconf modules  
>       * Ubiquiti EdgeOS/Edgeswitch facts and VLANs  
>          <https://docs.ansible.com/ansible/latest/collections/community/network/edgeswitch_facts_module.html#ansible-collections-community-network-edgeswitch-facts-module>  
>          <https://docs.ansible.com/ansible/latest/collections/community/network/edgeswitch_vlan_module.html#ansible-collections-community-network-edgeswitch-vlan-module>  
>
> - IF all else fails, use the Raw module  
>    <https://docs.ansible.com/ansible/latest/collections/ansible/builtin/raw_module.html>  
> - Or, try building your own Cliconf module  
>    <https://docs.ansible.com/ansible/latest/network/dev_guide/developing_plugins_network.html#developing-network-cli-plugins>  
> - For cleaner output logging, use json_query and flatten  
>    <https://www.logitblog.com/ansible-combining-loop-results-in-a-single-list/>  
