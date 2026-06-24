from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Base class for configuration providers (strategy pattern)."""

    @abstractmethod
    def get_all(self) -> dict[tuple[str, str, str], str]:
        """Return all configuration values as a dict keyed by (configset, env, key).

        The special env value "all" means the value applies to all environments
        unless overridden by a specific environment entry.
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, configset: str, env: str, key: str, value: str) -> None:
        """Write a single configuration value.

        Args:
            configset: The configuration set name.
            env: The environment name (dev/staging/prod/all).
            key: The configuration key.
            value: The configuration value.
        """
        raise NotImplementedError
