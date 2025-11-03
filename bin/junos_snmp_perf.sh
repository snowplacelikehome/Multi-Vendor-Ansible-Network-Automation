#!/usr/bin/sh
# snmpwalk -c public -v2c 172.16.17.0 
#   iso.3.6.1.4.1.664.5.53.4.1.4.7 = Gauge32: HeapSize 	.1.3.6.1.4.1.664.5.53.1.4.7
#   iso.3.6.1.4.1.664.5.53.4.1.4.7 = Gauge32: HeapFree 	.1.3.6.1.4.1.664.5.53.1.4.8
#OID 1.3.6.1.4.1.2636.3.1.13.1.11.9 (jnxOperatingCPU or jnxOperatingBuffer) for CPU and memory information of the Routing Engine
#OID 1.3.6.1.4.1.2636.3.39.1.12 (jnxJsSPUMonitoringCPUUsage) for SPU CPU utilization on SRX devices
defcommunity="public"

echo "IP,Device Name,Memory Total_MB,%Memory Used,load Avg 1 min,Load Avg 5 min"
while read ip_community; do
    # set ip = first word, community = second word
    eval `echo $ip_community | awk '{print "ip=" $1 " community=" $2}'`
    if [ -z "$community" ]; then
        community=$defcommunity
    fi
    memfree=""
    memtotal=""
    memtotal=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.2636.3.1.13.1.15.9.1.0.0 | awk -F'INTEGER: ' '{print $2}'`
    if [ -n "$memtotal" ]; then
        mempctused=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.2636.3.1.13.1.11.9.1.0.0 | awk -F'Gauge32: ' '{print $2}'`
        loadavg1m=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.2636.3.1.13.1.20.9.1.0.0 | awk -F'Gauge32: ' '{print $2}'`
        loadavg5m=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.2636.3.1.13.1.21.9.1.0.0 | awk -F'Gauge32: ' '{print $2}'`
        devname=`snmpget -c $community -v2c $ip 1.3.6.1.2.1.1.5.0 | awk -F'STRING: ' '{print $2}'`

        printf "%s,%s,%d,%d%%,%d,%d\n" $ip "$devname" "$memtotal" "$mempctused" "$loadavg1m" "$loadavg5m"
    else
        printf "%s,%s\n" $ip "snmpget failed"
    fi
done
