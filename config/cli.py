#!/usr/bin/env python3
"""Config CLI entrypoint.

Usage:
    python cli.py --provider ssm --env dev --prefix my-handicapped-pet/config --output ./out
"""

import argparse
import sys

from core import dump, upload_file, upload_value
from providers.aws_ssm import SSMProvider


PROVIDERS = {
    "ssm": SSMProvider,
}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile configuration from a provider and write <configset>.env files.",
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDERS),
        default="ssm",
        help="Configuration provider to use (default: ssm).",
    )
    parser.add_argument(
        "--env",
        required=True,
        choices=["dev", "staging", "prod", "all"],
        help="Target environment.",
    )
    parser.add_argument(
        "--configset",
        default=None,
        help="Target configset. If not specified, all configsets are dumped (download) or prompted (upload).",
    )
    parser.add_argument(
        "--prefix",
        default="my-handicapped-pet/config",
        help="Provider-specific path prefix (SSM: parameter path prefix).",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region (SSM provider only; falls back to AWS_DEFAULT_REGION env var).",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Directory where <configset>.env files will be written (default: current dir).",
    )
    parser.add_argument(
        "--upload-file",
        metavar="FILE",
        default=None,
        help="Upload all key=value pairs from a file to the provider.",
    )
    parser.add_argument(
        "--upload-value",
        metavar="KEY=VALUE",
        default=None,
        help="Upload a single value. Format: <key>=<value>.",
    )
    return parser


def prompt_configset() -> str:
    """Ask the user to enter a configset name interactively."""
    while True:
        value = input("Enter configset name: ").strip()
        if value:
            return value
        print("Configset name cannot be empty.")


def confirm_upload(configset: str, env: str) -> bool:
    """Ask the user to confirm the upload operation."""
    answer = input(f"Upload configuration for configset '{configset}', env '{env}'? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.provider == "ssm":
        provider = SSMProvider(prefix=args.prefix, region=args.region)
    else:
        print(f"Unknown provider: {args.provider}", file=sys.stderr)
        sys.exit(1)

    if args.upload_file:
        configset = args.configset or prompt_configset()
        if not confirm_upload(configset, args.env):
            print("Upload cancelled.")
            sys.exit(0)
        upload_file(provider, env=args.env, path=args.upload_file, configset=configset)
    elif args.upload_value:
        # Expected format: <key>=<value>
        if "=" not in args.upload_value:
            print(
                "Invalid --upload-value format. Expected: <key>=<value>",
                file=sys.stderr,
            )
            sys.exit(1)
        key, _, value = args.upload_value.partition("=")
        key = key.strip()
        if not key:
            print("Key cannot be empty in --upload-value.", file=sys.stderr)
            sys.exit(1)
        configset = args.configset or prompt_configset()
        if not confirm_upload(configset, args.env):
            print("Upload cancelled.")
            sys.exit(0)
        upload_value(provider, configset=configset, env=args.env, key=key, value=value)
    else:
        dump(provider, env=args.env, output_dir=args.output, configset=args.configset)


if __name__ == "__main__":
    main()
