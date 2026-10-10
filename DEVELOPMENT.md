# Development environment setup

## Create and configure a virtual environment

On Linux:

* Install [uv](https://docs.astral.sh/uv/) if not already available:
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

## Copier templates

This repository uses the following `copier` templates:

* [qgis-plugin-copier-template](https://github.com/osgeosuomi/qgis-plugin-copier-template/tree/main)

To get the newest version of the template, check each template's repository
README.md for update instructions.

## Code quality and style

The included `globebuilder.code-workspace` file is preconfigured for
VS Code and provides recommended settings for:

* Formatting
* Linting
* Type checking
* Test execution
* Recommended extensions

## Commit message convention

Commit messages should follow the
[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) convention.

## Release steps

When the branch is in a releasable state, trigger the `Create draft release`
workflow from GitHub Actions. Pass the to-be-released version number as an input
to the workflow.

Workflow creates two commits in the target branch, one with the release state
and one with the post-release state. It also creates a draft release from the
release state commit with auto-generated release notes.
Check the draft release notes and modify those if needed.
After the release is published, the tag will be created,
release workflow will be triggered, and it publishes a new version
to QGIS plugin repository.

Publishing requires QGIS plugin repository (OSGeo) credentials stored as
repository secrets `QGIS_REPO_USERNAME` and `QGIS_REPO_PASSWORD`
(Settings → Secrets and variables → Actions). Set them before the first
release, otherwise the release workflow fails at the publish step.
