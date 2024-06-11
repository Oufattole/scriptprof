import json
import os
import subprocess
import sys
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path
from typing import Any

import hydra
import pandas as pd
from loguru import logger

config_yaml = files("scriptprof").joinpath("config.yaml")
if not config_yaml.is_file():
    raise FileNotFoundError("Core configuration not successfully installed!")


def parse_times(log_dir: Path) -> Mapping[str, Any]:
    output_dict = dict()
    timings = open(Path(log_dir) / "cmd.stderr").read()
    times = [time.split("\t") for time in timings.split("\n")[-4:-1]]
    for key, value in times:
        output_dict[key + "_time"] = value
    output_dict
    return output_dict


def get_avg_memory(log_dir: Path):
    mprofile_path = log_dir / "mprofile.dat"
    df = pd.read_csv(mprofile_path, sep=r"\s+", skiprows=1, usecols=[1], names=["Memory"])
    avg_mem = df.Memory.mean()
    return avg_mem


def extract_peak_memory(log_dir: Path):
    memory = open(log_dir / "peak_memory_usage.txt").read()
    return memory.split("\t")[1].strip()


def extract_profile(log_dir: Path):
    output_dict = parse_times(log_dir)
    output_dict["avg_memory"] = get_avg_memory(log_dir)
    output_dict["peak_memory"] = extract_peak_memory(log_dir)
    return output_dict


@hydra.main(version_base=None, config_path=str(config_yaml.parent.resolve()), config_name=config_yaml.stem)
def run_profile(cfg):
    script, log_dir = cfg.script, cfg.log_dir
    os.makedirs(log_dir, exist_ok=True)
    # Run the profiling
    single_quote = "'"
    double_quote = '"'
    stripped_script = script.strip(single_quote).strip(double_quote)
    profile_cmd = (
        f"time mprof run --include-children --exit-code --output '{log_dir}/mprofile.dat' {stripped_script}"
    )
    status = subprocess.run(profile_cmd, shell=True, text=True, executable="/bin/bash", capture_output=True)
    open(f"{log_dir}/cmd.stderr", "w").write(status.stderr)
    open(f"{log_dir}/cmd.stdout", "w").write(status.stdout)
    # Check the exit status
    if status.returncode != 0:
        logger.error(f"Script failed with status {status.returncode}.")
        with open(f"{log_dir}/cmd.stderr") as stderr_file:
            logger.error(f"Stderr from script {script} (see cmd.stderr):")
            logger.error(stderr_file.read())
        sys.exit(status.returncode)
    # Generate plots and peak memory usage
    subprocess.run(f"mprof plot -o {log_dir}/mprofile.png {log_dir}/mprofile.dat", shell=True)
    subprocess.run(f"mprof peak {log_dir}/mprofile.dat > {log_dir}/peak_memory_usage.txt", shell=True)
    # Extract the profile
    profile = extract_profile(Path(log_dir))
    json.dump(profile, open(f"{log_dir}/profile_summary.json", "w"))


if __name__ == "__main__":
    run_profile()
