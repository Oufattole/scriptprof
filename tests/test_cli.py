import rootutils

root = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=True)

import json
import subprocess
import tempfile
from pathlib import Path

from hydra import compose, initialize

from src.scriptprof.main import run_profile


def run_command(script: str, args: list[str], hydra_kwargs: dict[str, str], test_name: str):
    command_parts = [script] + args + [f"{k}={v}" for k, v in hydra_kwargs.items()]
    command_out = subprocess.run(" ".join(command_parts), shell=True, capture_output=True)
    stderr = command_out.stderr.decode()
    stdout = command_out.stdout.decode()
    if command_out.returncode != 0:
        raise AssertionError(f"{test_name} failed!\nstdout:\n{stdout}\nstderr:\n{stderr}")
    return stderr, stdout


def test_scriptprof():
    with tempfile.TemporaryDirectory() as d:
        log_dir = Path(d)

        kwargs = {
            "script": "\"'echo hello, world $time'\"",
            "log_dir": str(log_dir.resolve()),
        }

        with initialize(version_base=None, config_path="../src/scriptprof/"):  # path to config.yaml
            overrides = [f"{k}={v}" for k, v in kwargs.items()]
            cfg = compose(config_name="config", overrides=overrides)  # config.yaml
        run_profile(cfg)
        output = json.load(open(log_dir / "profile_summary.json"))
        assert output.keys() == {"real_time", "user_time", "sys_time", "avg_memory", "peak_memory"}


def test_scriptprof_cli():
    with tempfile.TemporaryDirectory() as d:
        log_dir = Path(d)

        kwargs = {
            "script": "\"'echo hello, world $time'\"",
            "log_dir": str(log_dir.resolve()),
        }

        _, stdout = run_command("script-prof", [], kwargs, "test_script_prof")
        assert not stdout
        output = json.load(open(log_dir / "profile_summary.json"))
        assert output.keys() == {"real_time", "user_time", "sys_time", "avg_memory", "peak_memory"}
