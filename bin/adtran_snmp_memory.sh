#!/usr/bin/sh
# snmpwalk -c PuBlIcAw7200 -v2c 172.16.17.0 
#   iso.3.6.1.4.1.664.5.53.4.1.4.7 = Gauge32: HeapSize 	.1.3.6.1.4.1.664.5.53.1.4.7
#   iso.3.6.1.4.1.664.5.53.4.1.4.7 = Gauge32: HeapFree 	.1.3.6.1.4.1.664.5.53.1.4.8
defcommunity="public"

echo "IP,Dev_Name,Mem_Total_MB,Mem_Free_MB,,%Mem_Free"
while read ip_community; do
    # set ip = first word, community = second word
    eval `echo $ip_community | awk '{print "ip=" $1 " community=" $2}'`
    if [ -z "$community" ]; then
        community=$defcommunity
    fi
    memfree=""
    memtotal=""
    memtotal=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.664.5.53.1.4.7.0 | awk -F'Gauge32: ' '{print $2}'`
    if [ -n "$memtotal" ]; then
        devname=`snmpget -c $community -v2c $ip 1.3.6.1.2.1.1.5.0 | awk -F'STRING: ' '{print $2}'`
        memfree=`snmpget -c $community -v2c $ip 1.3.6.1.4.1.664.5.53.1.4.8.0 | awk -F'Gauge32: ' '{print $2}'`

        # calulate memory in MB with 3 decimal points of percision
        mbfree_e4="$((10000 * memfree/1024/1024))"
        mbtotal_e4="$((10000 * memtotal/1024/1024))"
        pfree_e4="$((10000 * memfree/memtotal * 100))"
        printf "%s,%s,%.2f,%.2f,%.2f\n" $ip "$devname" "${mbtotal_e4}e-4" "${mbfree_e4}e-4" "${pfree_e4}e-4"
    fi
done
