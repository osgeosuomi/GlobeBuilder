# Development environment setup

## Create and configure a virtual environment

On Linux:

* Install [uv](https://docs.astral.sh/uv/) if not already available:

  ```bash
  pip install uv
  ```

* Create a Python virtual environment with access to the libraries provided by
  the QGIS installation:

  ```bash
  uv venv .venv --system-site-packages
  ```

On Windows:

* You can use the [qgis-venv-creator tool](https://github.com/GispoCoding/qgis-venv-creator)
  to make sure the virtual environment is configured correctly for QGIS
* Install `uv` to the virtual environment:

  ```bash
  python -m pip install --upgrade pip
  pip install uv
  ```

When virtual environment is ready and activated:

* Install dependencies
* Install pre-commit hooks
* Run tests

```bash
uv sync
prek install
pytest
```

## Running QGIS in development mode

Before starting development, create a `.env` file by copying `.env.example` and update
the configuration values as needed. Set the `QGIS_EXECUTABLE_PATH` variable to point to
the same QGIS installation the venv was created by.

Start QGIS with the plugin loaded in development mode:

```bash
qgis-plugin-dev-tools start

# Short form
qpdt s
```

For more information about the development workflow, see the [qgis-plugin-dev-tools documentation](https://github.com/nlsfi/qgis-plugin-dev-tools#plugin-development-mode).

## Managing dependencies

This project uses [uv](https://docs.astral.sh/uv/concepts/projects/dependencies/) for
dependency management.

## Code quality and style

The included `globe-builder.code-workspace` file is preconfigured for
VS Code and provides recommended settings for:

* Formatting
* Linting
* Type checking
* Test execution
* Recommended extensions

## Commit message convention

Commit messages should follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) convention.
