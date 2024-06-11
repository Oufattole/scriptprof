#!/bin/bash

# set -x # un-comment to see what's going on when you run the script

# Create a temporary directory and store its name in a variable.
TEMPD=$(mktemp -d)

# Exit if the temp directory wasn't created successfully.
if [ ! -e "$TEMPD" ]; then
    >&2 echo "Failed to create temp directory"
    exit 1
fi

# Run the script-prof command with the specified arguments.
script-prof log_dir="${TEMPD}" script="sleep 1" hydra.run.dir=. hydra/job_logging=disabled hydra/hydra_logging=disabled
ls "${TEMPD}"
cat "${TEMPD}/profile_summary.json"
echo

# Make sure the temp directory gets removed on script exit.
trap "exit 1"           HUP INT PIPE QUIT TERM
trap 'rm -rf "$TEMPD"'  EXIT
