#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_ENV_FILE = Path(__file__).resolve().parent.parent / ".env.local"


def load_env_file(path: str | Path) -> dict[str, str]:
    env: dict[str, str] = {}
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"env file not found: {env_path}")

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def build_mysql_command(config: dict[str, str]) -> list[str]:
    command = [
        "mysql",
        f"--host={config['MYSQL_HOST']}",
        f"--port={config['MYSQL_PORT']}",
        f"--user={config['MYSQL_USER']}",
        "--default-character-set=utf8mb4",
    ]
    database = config.get("MYSQL_DATABASE")
    if database:
        command.append(database)
    return command


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Execute SQL from stdin against local MySQL")
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path to env file with MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD[/MYSQL_DATABASE]",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    sql = sys.stdin.read()
    if not sql.strip():
        raise SystemExit("stdin SQL is empty")

    config = load_env_file(args.env_file)
    required_keys = ("MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        raise SystemExit(f"missing env keys: {', '.join(missing)}")

    command = build_mysql_command(config)
    env = os.environ.copy()
    env["MYSQL_PWD"] = config["MYSQL_PASSWORD"]

    result = subprocess.run(
        command,
        input=sql,
        text=True,
        capture_output=True,
        env=env,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
