#!/usr/bin/perl -w

# Usage: csv2yaml.pl [file_name]
#   If file_name is not provided, the CSV data is read from STDIN

# Example: ./bin/csv2yaml.pl ~/Downloads/ports.csv
# Sample ports.csv input
# Port_Num will be skipped and Port_Name will be used as the YAML "name" keys in the dictionary of key:value lists
# All remaining columns will be additional key:value under that name
#   Port_Num,Port_Name,Description,Bridge,Mode,Edge,PVID
#   0,ether1,WAN - Outside,WAN,Access,yes,1
#   2,ether2,VMWareHost1 Trunk,LAN,Trunk,yes,1
#   3,ether3,,LAN,,,1
#
# Will result in:
#   dict_name:
#     - name: ether1
#       Description: WAN - Outside
#       Bridge: WAN
#       Mode: Access
#       Edge: True
#       PVID: 1
#     - name: ether3
#       Description: VMWareHost1 Trunk
#       Bridge: LAN
#       Mode: Trunk
#       Edge: True
#       PVID: 1
#     - name: ether3
#       Description: 
#       Bridge: LAN
#       Mode: 
#       Edge: 
#       PVID: 1

use strict;
use Text::CSV;
use Getopt::Std;
use File::Basename;

our($opt_c,$opt_s,$opt_n,$opt_h); # Skip_Cols and Dictionary name Options

getopts('cs:n:h');

if ( $#ARGV >= 0 ) {
   if ( $ARGV[0] eq "help" ) {
      $opt_h = 1;
   }
}
if ( $opt_h ) {
    print "Usage: $0 [-s \"#Cols_to_Skip\"] [-n NAME_OF_DICTIONARY] [CSV_FILE] \n\n" .
    "       Read CSV input from CSV_FILE if provided, otherwise from STDIN. Output a\n" .
    "       YAML dictionary of lists, with a list for each CSV row, using the key\n" .
    "       names from the names of the CSV column headings and values from each CSV cell.\n" .
    "       The column header names are converted from calmel case to lower case separated\n" .
    "       by '_' for better standardization, unless the -c option is specified.\n" .
    "       -h : show this help message\n" .
    "       -c : (optional, default = convert) Skip conversion of column headers from camel\n" .
    "            case to lower case separated by '_'\n" .
    "       -s #Cols_to_Skip : (optional, default = 0) The number of columns from the left\n" .
    "                          to skip. The next column will be the YAML '- name' key and\n" .
    "                          The all of the following columns will be keys named by their\n" .
    "                          column headers\n" .
    "       -n NAME_OF_DICTIONARY : (optional, default = 'dictionary_name')\n" .
    "                               the name of the YAML dictionary printed before all of the\n" .
    "                               lists of key:values\n" .
    "       CSV_FILE : (optional, default is STDIN) The name of a CSV file to read \n\n";
    exit 1;
}

# Set the number of columns to skip. The next column will be used as the "- name" key
# and all of the following columns will be additional keys in that list
my $skipCols;
if ($opt_s) {
    $skipCols = $opt_s;
} else {
    $skipCols = 0;
}

# set the name of the YAML dictionary printed before all of the lists of key:values\n" .
my $dictName;
if ($opt_n) {
    $dictName = $opt_n;
} else {
    $dictName = "dictionary_name";
}


# Initialize the Text::CSV object
my $csv = Text::CSV->new ({ skip_empty_rows => 1, auto_diag => 1 });

# Open the input file for reading or use STDIN
my $fh;
if ($#ARGV >= 0) {
    open $fh, "<:encoding(utf8)", $ARGV[0] or die "$ARGV[0]: $!";
} else {
    $fh = *STDIN;
}

# Print the YAML dictionary name
print "\n${dictName}:\n";

#
# Print the YAML list of key:value's
#

# Get the header row (the first row)
my @cols = @{$csv->getline ($fh)};

# Convert camel case names to lower case separated by "_"
if (not $opt_c) {
    for (my $i = 0; $i <= $#cols; $i++) {
        print "#cols = $#cols; i = $i; col = $cols[$i]\n";
        my $lCaseCol = $cols[$i]; 
        $lCaseCol =~ s/([a-z])([A-Z])/${1}_\L$2/g;
        $lCaseCol =~ s/(\w)/\L$1/g;
        $cols[$i] = $lCaseCol;
    }
}

# Set the column names needed by the Text::CSV->getline_hr function
$csv->column_names (@cols);

# Read through each row of the CSV and output the keys based on the column header
# names and the values based on each CSV cell value
while (my $row = $csv->getline_hr ($fh)) {
    print "  - name: ", $row->{$cols[$skipCols]}, "\n";
    for (my $col = $skipCols + 1; $col <= $#cols; $col = ++$col) {
        # if the value is boolean, always output in the true/false format accepted
        # by the default yamllint options
        if ($row->{$cols[$col]} =~ /true|yes/i) {
           print "    $cols[$col]: true", "\n";
        } elsif ($row->{$cols[$col]} =~ /false|no/i) {
           print "    $cols[$col]: false", "\n";
        } else {
           print "    $cols[$col]: $row->{$cols[$col]}", "\n";
        }
    }
}