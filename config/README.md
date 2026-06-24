# Configuration tool for [my-handicapped-pet.io](https://my-handicapped-pet.io)

The goal is to provide the project's services with configuration values and secrets.
The idea is to build a small, explicit “config compiler” with pluggable backends (strategy pattern).

Let’s build a minimal but extensible Python draft that does:

- multiple providers (strategy pattern)
- per-environment (dev/staging/prod)
- per-service config
- merging + overrides
- outputs .env

## Core idea

```text
Providers → return dict[str, str]
        ↓
Merge + resolve
        ↓
Render → .env
```

There are three dimensions of configuration:
- configuration set, which can correspond to one or more services;
- environment (dev, staging, prod)
- actual configuration key

For example, in AWS SSM we can use keys in format my-handicapped-pet/config/<configset>/<env>/<KEY>

It must be possible to specify "all" instead of a particular environment to 
provide a given key-value for all environments. Values under "all" are applied
if there is no value with the same configset and key under a specific 
environment. Values under a specific environment can override them.

Let's stay with the static (docker-compose-based) configuration for now (update
will require restart of the docker containers.)

Before deploy, we call config (also in docker, but locally on the
dev or CI machine, unlike the project's containers, which are spawned remotely).
It reads from the given configuration provider, and dumps a number of files
<configset>.env for each configset in the env file format (key=value).

## High-level design

```text
config/
 ├── providers/
 │    ├── base.py
 │    ├── aws_ssm.py
 │
 ├── core.py        # orchestration
 └── cli.py         # entrypoint
```
