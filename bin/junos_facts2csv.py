import json
import csv
import sys
import os
import subprocess

# Run the following to review the facts file in readable JSON format:
#   python3 -m json.tool facts/inventory_hostname

def get_inventory(basedir):
    try:
        invnetory_result = subprocess.run(f"ansible-inventory --playbook-dir {basedir} --inventory {basedir}/hosts.yml --list --export", capture_output=True, text=True, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stderr: {e.stderr}")
        return None

    try:
        inv_data = json.loads(invnetory_result.stdout)
        return inv_data
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in ansible-inventory output")
        print(f"ansible-inventory stdout: \n{invnetory_result.stdout.strip()}")
        return

def json_to_csv(json_dirpath, csv_filepath, inventory_data):
    """
    Reads JSON data from files in the dir, and writes their data to a CSV file.

    Args:
        json_dirpath (str): Path to the JSON file.
        csv_filepath (str): Path to the output CSV file.
    """

    #
    # Open the target CSV file for writing
    try:
        with open(csv_filepath, 'w', newline='') as csv_file:

            #
            # Write a CSV header
            writer = csv.writer(csv_file)
            header = ['Inventory_Hostname', 'Ansible_Host', 'Device_HostName', 'Model', 'SerialNum', 'OS_Version', '2RE']
            writer.writerow(header)

            #
            # Process each JSON file in the dir
            for json_filename in os.listdir(json_dirpath):

                json_filepath = os.path.join(json_dirpath, json_filename)

                if os.path.isfile(json_filepath):  # Ensure it's a file, not a subdirectory
                    #
                    # Open the file and try reading it in as JSON
                    print(f"Processing file: {json_filename}")

                    try:
                        with open(json_filepath, 'r') as json_file:
                            data = json.load(json_file)
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON format in '{json_filepath}'")
                        return

                    #
                    # Write the JSON data as CSV rows
                    if not data:
                        print("Warning: JSON data is empty. No CSV data will be added.")
                        return

                    if isinstance(data, dict):

                        # example data
                        #data['ansible_facts']['ansible_net_hostname']
                        #'eve-ng.vex1'
                        #data['ansible_facts']['ansible_net_model']
                        #'ex9214'
                        #data['ansible_facts']['ansible_net_serialnum']
                        #'VM6643C043BD'
                        #data['ansible_facts']['ansible_net_version']
                        #'23.2R1.14'
                        #data['ansible_facts']['ansible_net_has_2RE']

                        if 'ansible_facts' in data:
                            row = [ json_filename ]
                            if 'ansible_net_hostname' in data['ansible_facts']:
                                row += [ data['ansible_facts']['ansible_net_hostname'] ]
                                #
                                # See if the ansible inventory has an ansible_host for this ansible_net_hostname
                                if '_meta' in inventory_data:
                                    if 'hostvars' in inventory_data['_meta']:
                                        if json_filename in inventory_data['_meta']['hostvars']:
                                            row += [ inventory_data['_meta']['hostvars'][json_filename]['ansible_host'] ]
                                        else:
                                            row += [ "" ]
                                    else:
                                        row += [ "" ]
                                else:
                                    row += [ "" ]
                            else:
                                row += [ "" ]
                            if 'ansible_net_model' in data['ansible_facts']:
                                row += [data['ansible_facts']['ansible_net_model'] ]
                            else:
                                row += [ "" ]
                            if 'ansible_net_serialnum' in data['ansible_facts']:
                                row += [data['ansible_facts']['ansible_net_serialnum'] ]
                            else:
                                row += [ "" ]
                            if 'ansible_net_version' in data['ansible_facts']:
                                row += [data['ansible_facts']['ansible_net_version'] ]
                            else:
                                row += [ "" ]
                            if 'ansible_net_has_2RE' in data['ansible_facts']:
                                row += [data['ansible_facts']['ansible_net_has_2RE'] ]
                            else:
                                row += [ "" ]
                        elif 'msg' in data:
                            msg = data['msg'].replace("\n", " ")
                            row = [
                                json_filename,
                                msg
                            ]
                        else:
                            row = [ json_filename ]

                        writer.writerow(row)


                    else:
                        print("Error: Unsupported JSON data format. The JSON data should be a dict.")
                        return

            print(f"Successfully converted JSON files in '{json_dirpath}' to '{csv_filepath}'")

    except Exception as e:
        print(f"An error occurred during CSV writing: {e}")

# end sub json_to_csv()

#
# __main__
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_dir_path = sys.argv[1]
        if len(sys.argv) > 2:
            csv_file_path = sys.argv[2]
        else:
            csv_file_path = 'output.csv'
        if len(sys.argv) > 3:
            inventory_basedir = sys.argv[3]
        else:
            inventory_basedir = '.'

        inventory_data = get_inventory(inventory_basedir)
        json_to_csv(json_dir_path, csv_file_path, inventory_data)
    else:
        print("Usage: python script.py <json_dirname> <csv_filename> <inventory_basedir>")
