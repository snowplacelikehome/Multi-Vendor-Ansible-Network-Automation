#!/usr/bin/sh
# enterrpise(1).6141.wwpModules(2)
#snmpwalk -c public -v2c 10.6.20.2 1.3.6.1.4.1.6141.2.60.1.1.1.2.1
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.1.1 = Timeticks: (43043400) 4 days, 23:33:54.00
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.2.1 = STRING: "B9298115"
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.3.1 = STRING: "1703903820/009"
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.4.1 = STRING: "Passed"
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.5.1 = Gauge32: 0
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.6.1 = Hex-STRING: 07 E1 0B 07 00 00 00 00 2B 00 00
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.7.1 = STRING: "3903 Service Delivery Switch"
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.8.1 = Gauge32: 15
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.9.1 = INTEGER: 3
#iso.3.6.1.4.1.6141.2.60.1.1.1.2.1.10.1 = INTEGER: 1
echo "IP,Name,Model,Serial"
while read ip; do
    name=""
    netmodel=""
    model=`snmpget -c public -v1 $ip 1.3.6.1.2.1.1.1.0 | awk -F'STRING: ' '{print $2}'`
    if [ -n "$model" ]; then
        name=`snmpget -c public -v1 $ip 1.3.6.1.2.1.1.5.0 | awk -F'STRING: ' '{print $2}'`
        serial=`snmpget -c public -v1 $ip 1.3.6.1.4.1.6141.2.60.1.1.1.2.1.2.1 | awk -F'STRING: ' '{print $2}'`
    fi
    echo "${ip},${name},${model},${serial}"
done
