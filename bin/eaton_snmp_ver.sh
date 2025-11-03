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
while read ip; do
    upsver=""
    netver=""
    netmodel=""
    model=`snmpget -c public -v1 $ip 1.3.6.1.2.1.33.1.1.2.0 | awk -F'STRING: ' '{print $2}'`
    if [ -n "$model" ]; then
        upsver=`snmpget -c public -v1 $ip 1.3.6.1.2.1.33.1.1.3.0 | awk -F'STRING: ' '{print $2}'`
        netver=`snmpget -c public -v1 $ip 1.3.6.1.2.1.33.1.1.4.0 | awk -F'STRING: ' '{print $2}'`
        # for Network-MS cards, strip the prefix version text
        net_ms_model="${netver##'"Network Management Card V6.00 '}"
        # if it stripped the text, also strip the end quote
        if [ "$net_ms_model" != "$netver" ]; then
            net_ms_model="${net_ms_model%'"'}"
        fi
        if [ "$net_ms_model" = "$netver" ]; then
            # Assume one of the newer model cards that has the xUPS mib
            # iso.3.6.1.4.1.534.1.14.2.0 = STRING: "Eaton Gigabit Network Card"
            netmodel=`snmpget -c public -v1 $ip 1.3.6.1.4.1.534.1.14.2.0 | awk -F'STRING: ' '{print $2}'`
        else
            # Old model Network-MS cards that don't have the xUPS mib
            netmodel="Network-MS $net_ms_model"
        fi
    fi
    echo "${ip},${model},${upsver},${netver},${netmodel}"
done