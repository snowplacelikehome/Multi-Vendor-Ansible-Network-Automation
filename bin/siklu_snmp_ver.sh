#!/usr/bin/sh
# XUPS-MIB::xups.14
# snmpwalk -c public -v1 10.7.77.99 1.3.6.1.4.1.534.1.14
#   iso.3.6.1.4.1.534.1.14.1.0 = STRING: "Eaton"
#   iso.3.6.1.4.1.534.1.14.2.0 = STRING: "Eaton Gigabit Network Card"
#   iso.3.6.1.4.1.534.1.14.3.0 = STRING: "3.1.15"
#   iso.3.6.1.4.1.534.1.14.4.0 = STRING: "744-A3983PH-01"
#   iso.3.6.1.4.1.534.1.14.5.0 = STRING: "P312M08AEF"
#UPS-MIB::upsIdentModel.0
#UPS-MIB::upsIdentUPSSoftwareVersion.0
#UPS-MIB::upsIdentAgentSoftwareVersion.0
v2community="public"
echo "ip,devname,model,uptime,swbank1ver,swbank1running,swbank2ver,swbank2running,authmode"
while read ip; do
    model=""
    devname=""
    uptime=""
    swbank1ver=""
    swbank2ver=""
    authmode=""
    model=`snmpget -c $v2community -v1 $ip 1.3.6.1.2.1.1.1.0 | awk -F'STRING: ' '{print $2}'`
    if [ -n "$model" ]; then
        devname=`snmpget -c $v2community -v1 $ip 1.3.6.1.2.1.1.5.0 | awk -F'STRING: ' '{print $2}'`
        uptime=`snmpget -c $v2community -v1 $ip 1.3.6.1.2.1.1.3.0 | awk -F'Timeticks: ' '{print $2}'`
        swbank1ver=`snmpget -c $v2community -v1 $ip 1.3.6.1.4.1.31926.1.5.0 | awk -F'STRING: ' '{print $2}'`
        swbank2ver=`snmpget -c $v2community -v1 $ip 1.3.6.1.4.1.31926.1.6.0 | awk -F'STRING: ' '{print $2}'`
        # Enumeration: 'running': 2, 'noRunning': 1, 'running-wait-accept': 3.
        swbank1running=`snmpget -c $v2community -v1 $ip 1.3.6.1.4.1.31926.1.7.0 | awk -F'INTEGER: ' '{print $2}'`
        swbank2running=`snmpget -c $v2community -v1 $ip 1.3.6.1.4.1.31926.1.8.0 | awk -F'INTEGER: ' '{print $2}'`
        #  Enumeration: 'radius': 2, 'local': 1, 'tacacs': 3.
        authmode=`snmpget -c $v2community -v1 $ip 1.3.6.1.4.1.31926.1.12.0 | awk -F'INTEGER: ' '{print $2}'`
    fi
    echo "${ip},${devname},${model},\"${uptime}\",${swbank1ver},${swbank1running},${swbank2ver},${swbank2running},${authmode}"
done