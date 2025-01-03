#!/usr/bin/bash

usage () {
        echo "Usage: $(basename $0)" 2>&1
        exit 1
}

# if a command line argument is found, exit the script with usage
if [ ${#} -ne 0 ]; then
	echo 'ERROR: no argument is expected.'
	usage
fi

# Run the commands from one directory lower than this script lives
echo "Switching to base directory."
pushd $PWD
cd `dirname $0`
cd ..

echo -e "\nBacking up Git ignored (.gitignore) files to:\n    ../`basename $PWD.private.tgz`.\n"
# build a list of files that aren't include in the Git repo (files excluded by .gitignore)
rsync -rv --filter='+ **/' --include-from=./.gitignore --filter='- *' --dry-run . ../copy | grep -Ev "/$|^sending |^created |^sent |^total " > ../`basename $PWD`.ignored
# make a backup of those files
tar -czvf ../`basename $PWD`.private.tgz --files-from=../`basename $PWD`.ignored

echo -e "\nReturning to initial directory."
popd