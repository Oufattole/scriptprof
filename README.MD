This script uses `mprofile` and `time` in bash, redirects the outputs to a common log directory and summarizes the outputs into a `summary.json` file.

```bash
#!/bin/bash

# set -x # un-comment to see what's going on when you run the script

# Create a temporary directory and store its name in a variable.
TEMPD=$(mktemp -d)

# Exit if the temp directory wasn't created successfully.
if [ ! -e "$TEMPD" ]; then
    >&2 echo "Failed to create temp directory"
    exit 1
fi

script-prof log_dir=$TEMPD script="sleep 1"
cat "${TEMPD}/profile_summary.json"

# Make sure the temp directory gets removed on script exit.
trap "exit 1"           HUP INT PIPE QUIT TERM
trap 'rm -rf "$TEMPD"'  EXIT
```

The script will output something like:

```bash
cmd.stderr  cmd.stdout  mprofile.dat  mprofile.png  peak_memory_usage.txt  profile_summary.json
{"real_time": "0m1.354s", "user_time": "0m0.314s", "sys_time": "0m0.140s", "avg_memory": 1.003906, "peak_memory": "1.004 MiB"}
```

1. `cmd.stderr` and `cmd.stdout` are the outputs of the script. `cmd.stderr` contains the timing information for how long the script ran.
2. `mprofile.dat` is the sampled memory usage over time of the script
3. `mprofile.png` is a generated plot of the memory usage over time.
4. `peak_memory_usage.txt` contains the peak memory usage.
5. `profile_summary.json` summarizes the above stats and is the second line outputted by the script above^.
