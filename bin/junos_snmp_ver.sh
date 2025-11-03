#!/usr/bin/sh
# snmpwalk -c public -v2c 198.167.173.139 1.3.6.1.4.1.2636.3.1.2
#   iso.3.6.1.4.1.2636.3.1.2.0 = STRING: "Juniper SRX300 Internet Router"
# snmpget -c public -v2c 198.167.173.139 1.3.6.1.2.1.25.6.3.1.2.2 
#   iso.3.6.1.2.1.25.6.3.1.2.2 = STRING: "JUNOS Software Release [15.1X49-D230]"

defcommunity="public"

echo "ip,devname,model,uptime,sw"
while read ip_community; do
    # set ip = first word, community = second word
    eval `echo $ip_community | awk '{print "ip=" $1 " community=" $2}'`
    if [ -z "$community" ]; then
        community=$defcommunity
    fi
    model=""
    devname=""
    uptime=""
    sw=""
    model=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.2636.3.1.2.0 | awk -F'STRING: ' '{print $2}'`
    if [ -n "$model" ]; then
        devname=`snmpget -c $community -v2c $ip 1.3.6.1.2.1.1.5.0 | awk -F'STRING: ' '{print $2}'`
        uptime=`snmpget -c $community -v2c $ip 1.3.6.1.2.1.1.3.0 | awk -F'Timeticks: ' '{print $2}'`
        sw=`snmpget -c $community -v2c $ip 1.3.6.1.2.1.25.6.3.1.2.2 | awk -F'\\\]|\\\[' '{print $2}'`
    fi
    echo "${ip},${devname},${model},\"${uptime}\",${sw}"
done
