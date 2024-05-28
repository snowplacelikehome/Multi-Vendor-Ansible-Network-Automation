#!/usr/bin/bash

usage () {
        echo "Usage: $(basename $0) example|home" 2>&1
        exit 1
}

# if less than 1 option and its argument are found, exit the script with usage
if [ ${#} -ne 1 ]; then
	echo 'ERROR: one argument is required. Valid argeuments are "example" or "home"'
	usage
fi

# Run the find command from one directory lower than this script lives
pushd $PWD
cd `dirname $0`
cd ..

# find symbolic links of all *.yml files except for main.yml and all.yml. Remove the link and
# add a new link with .$0 before .yml
find . -type l -a -name \*.yml -a \! -name main.yml -a \! -name all.yml -print -execdir sh -c 'f="'{}'"; f="${f##*/}"; echo "  " rm "$f"; rm "$f"; echo "  " ln -s "${f%.yml}.'$1'.yml" "$f"; ln -s "${f%.yml}.'$1'.yml" "$f"' \;

popd
