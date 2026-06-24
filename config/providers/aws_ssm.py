import boto3

from .base import BaseProvider


class SSMProvider(BaseProvider):
    """Reads configuration from AWS SSM Parameter Store.

    Expected key format:
        /<prefix>/<configset>/<env>/<KEY>

    The special env segment "all" means the value applies to all environments
    unless overridden by a specific environment entry.
    """

    def __init__(self, prefix: str, region: str | None = None) -> None:
        self._prefix = "/" + prefix.strip("/")
        self._client = boto3.client("ssm", region_name=region)

    def get_all(self) -> dict[tuple[str, str, str], str]:
        result: dict[tuple[str, str, str], str] = {}
        paginator = self._client.get_paginator("get_parameters_by_path")
        pages = paginator.paginate(
            Path=self._prefix + "/",
            Recursive=True,
            WithDecryption=True,
        )
        for page in pages:
            for param in page["Parameters"]:
                name: str = param["Name"]
                value: str = param["Value"]
                # Strip the leading prefix and split into parts
                relative = name[len(self._prefix):].lstrip("/")
                parts = relative.split("/")
                if len(parts) != 3:
                    continue
                configset, env, key = parts
                result[(configset, env, key)] = value
        return result

    def put(self, configset: str, env: str, key: str, value: str) -> None:
        """Write a single configuration value to SSM Parameter Store as SecureString."""
        name = f"{self._prefix}/{configset}/{env}/{key}"
        self._client.put_parameter(
            Name=name,
            Value=value,
            Type="SecureString",
            Overwrite=True,
        )
