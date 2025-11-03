import snmp_client
import csv

def get_snmp_data(host_ips, oid_string, community_string='public'):
    """
    Retrieves SNMP data for a list of host IPs and a given OID.

    Args:
        host_ips (list): List of host IP addresses.
        oid_string (str): SNMP OID string to query.
        community_string (str, optional): SNMP community string. Defaults to 'public'.

    Returns:
        list: List of tuples containing host IP and SNMP value.
    """
    results = []
    for ip in host_ips:
        try:
            snmp_value = snmp_client.get_snmp_value(ip, oid_string, community_string)
            results.append((ip, snmp_value))
        except Exception as e:
            print(f"Error querying {ip}: {e}")
            results.append((ip, 'Error'))
    return results

def write_to_csv(data, filename='snmp_output.csv'):
    """
    Writes SNMP data to a CSV file.

    Args:
        data (list): List of tuples containing host IP and SNMP value.
        filename (str, optional): Name of the CSV file to write to. Defaults to 'snmp_output.csv'.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Host IP', 'SNMP Value'])
        writer.writerows(data)
    print(f"Data written to {filename}")

if __name__ == "__main__":
    host_ips = input("Enter host IPs separated by commas: ").split(',')
    oid_string = input("Enter SNMP OID string: ")
    snmp_community = input("Enter SNMP read community string: ")
    
    snmp_data = get_snmp_data(host_ips, oid_string)
    write_to_csv(snmp_data)