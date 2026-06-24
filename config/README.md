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

## CLI format

```sh
python cli.py --env <dev|staging|prod> [--configset <name>] [--provider ssm] [--prefix <path>] [--region <aws-region>] [--output <dir>]
python cli.py --env <dev|staging|prod> [--configset <name>] --upload-file <file>
python cli.py --env <dev|staging|prod> [--configset <name>] --upload-value <key>=<value>
```

### Arguments

| Argument         | Required | Default | Description                                                                                                   |
|------------------|----------|---|---------------------------------------------------------------------------------------------------------------|
| `--env`          | yes      | — | Target environment: `dev`, `staging`, or `prod`                                                               |
| `--configset`    | no       | — | Target configset. If not specified, all configsets are dumped. For uploading, will be asked if not specified. |
| `--provider`     | no       | `ssm` | Configuration provider: `ssm` (AWS SSM Parameter Store)                                                       |
| `--prefix`       | no       | `my-handicapped-pet/config` | SSM parameter path prefix                                                                                     |
| `--region`       | no       | `$AWS_DEFAULT_REGION` | AWS region (SSM provider only)                                                                                |
| `--output`       | no       | `.` (current dir) | Directory where `<configset>.env` files are written                                                           |
| `--upload-file`  | no       | — | Path to a file to upload; all key=value pairs are written to the provider                                     |
| `--upload-value` | no       | — | Upload a single value in the format `<key>=<value>`                                                           |

### Examples

Dump config for the `dev` environment using AWS SSM (default prefix, region from env):
```sh
python cli.py --env dev
```

Dump config for `prod` with an explicit region and custom output directory:
```sh
python cli.py --env prod --region eu-west-1 --output ./envfiles
```

Dump config for `staging` with a custom SSM prefix:
```sh
python cli.py --env staging --prefix my-handicapped-pet/config --region us-east-1 --output ./out
```

Upload an entire file to the provider for the `prod` environment (configset prompted if not given):
```sh
python cli.py --env prod --upload-file ./my-config.env --configset backend
```

Upload a single value to the provider (configset prompted if not given):
```sh
python cli.py --env dev --configset backend --upload-value DATABASE_URL=postgres://localhost/mydb
```

Each run writes one `<configset>.env` file per configset found in the provider, e.g.:
```
./out/backend.env
./out/frontend.env
```

Each `.env` file contains `key=value` lines, sorted alphabetically:
```dotenv
DATABASE_URL=postgres://...
SECRET_KEY=s3cr3t
```

