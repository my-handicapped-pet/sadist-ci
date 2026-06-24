import os

from providers.base import BaseProvider


ALL_ENV = "all"


def resolve(provider: BaseProvider, env: str) -> dict[str, dict[str, str]]:
    """Resolve configuration for a specific environment.

    Returns a dict mapping configset → {key: value}.
    Values under "all" are applied first; environment-specific values override them.
    """
    raw = provider.get_all()

    # Collect "all" values first, then override with env-specific values
    merged: dict[str, dict[str, str]] = {}

    for (configset, entry_env, key), value in raw.items():
        if entry_env == ALL_ENV:
            merged.setdefault(configset, {})[key] = value

    for (configset, entry_env, key), value in raw.items():
        if entry_env == env:
            merged.setdefault(configset, {})[key] = value

    return merged


def render(configset: str, values: dict[str, str]) -> str:
    """Render a configset's values as .env file content (key=value lines)."""
    lines = [f"{key}={value}" for key, value in sorted(values.items())]
    return "\n".join(lines) + "\n" if lines else ""


def upload_value(provider: BaseProvider, configset: str, env: str, key: str, value: str) -> None:
    """Write a single key=value into the provider."""
    if not value:
        print(f"WARNING: skipping {configset}/{env}/{key} — value is empty (provider does not support empty values)")
        return
    provider.put(configset, env, key, value)
    print(f"Uploaded {configset}/{env}/{key}")


def upload_file(provider: BaseProvider, env: str, path: str, configset: str) -> None:
    """Read a file and upload all key=value pairs into the provider.

    Lines starting with '#' and blank lines are ignored.
    """
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            upload_value(provider, configset, env, key.strip(), value.strip())


def dump(provider: BaseProvider, env: str, output_dir: str = ".", configset: str | None = None) -> None:
    """Resolve config and write <configset>.env files into output_dir.

    If configset is given, only that configset is written.
    """
    resolved = resolve(provider, env)
    if configset is not None:
        resolved = {k: v for k, v in resolved.items() if k == configset}
    os.makedirs(output_dir, exist_ok=True)
    for configset, values in resolved.items():
        path = os.path.join(output_dir, f"{configset}.env")
        content = render(configset, values)
        with open(path, "w") as f:
            f.write(content)
        print(f"Written {path}")
