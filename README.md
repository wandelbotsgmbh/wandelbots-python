# @wandelbots/wandelbots-python

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/wandelbotsgmbh/wandelbots-python/HEAD?labpath=examples%2F05_notebook.ipynb)

This library provides a wrapper around the Wandelbots API. Under the hood it queries the API endpoints directly, not using [`wandelbots_api_client`](https://pypi.org/project/wandelbots-api-client/) (_which is still required as dependencies since the auto-generated types are used from the package for type-checking convenience_).

The wrapper is meant to ease the interaction with the Wandelbots API by providing a simpler interface for initializing a `MotionGroup` and interacting with it.
For the full feature set of our API please refer to the [official documentation](https://docs.wandelbots.com/) and use the [`wandelbots_api_client`](https://pypi.org/project/wandelbots-api-client/) package directly.

You can try the features of this library in a Jupyter notebook by clicking the Binder badge above. Create a new Instance by registering on the [Wandelbots website](https://portal.wandelbots.io/) and use the credentials to interact with the API.

Current Features:

- Sync and Async Planning and Execution
- Pose Transformations

## Table Of Contents

- [Requirements](#requirements)
- [Build](#build)
- [Basic Usage](#basic-usage)
- [Testing](#testing)

### Requirements

This library requires

- Python >=3.9

### Installation

To use the library, first install it using the following command

```bash
pip install wandelbots
```

Then import the library in your code

```python
from wandelbots import Instance, MotionGroup, Planner
```

### Development

To install the development dependencies, run the following command

```bash
poetry install
```

To remove an old virtual environment and create a new one, first get the name of the old environment by running

```bash
poetry env info
```

Then remove the old environment and create a new one with the following commands

```bash
poetry env remove <name-of-env>
poetry install
```

Run the poetry shell to activate the virtual environment

```bash
poetry shell
```

### Build

To build the package locally, run the following command

```bash
poetry build
```

This will create a `dist/` directory with the built package (`.tar.gz` and `.whl` files).

#### Installation

```bash
pip install wandelbots
```

##### Install a development branch in Poetry

```bash
wandelbots = { git = "https://github.com/wandelbotsgmbh/wandelbots-python.git", branch = "feature/set-ios-on-path" }
```

### Basic Usage

The wrapper provides a simple interface for initializing a `Instance`, `MotionGroup` and a `Planner` object, which can be used to interact with the Wandelbots API:

```python
from wandelbots import Instance, MotionGroup, Planner

my_instance = Instance(
    url=https://<my-instance-url>,
    user=<username>,
    password=<password>
)

my_robot = MotionGroup(
    instance=my_instance,
    cell="cell",
    motion_group="0@motion_group",
    default_tcp="Flange"
)
```

For further examples take a look at the [examples](https://github.com/wandelbotsgmbh/wandelbots-python/blob/main/examples/README.md).

### Testing

```bash
poetry run pytest -rs -v
```

#### Integration Tests

By default integration tests will be skipped.
To run them localy create an env file at `envs/.env.tests` with your values.

```txt
WANDELAPI_BASE_URL=
NOVA_ACCESS_TOKEN=
CELL_ID=
MOTION_GROUP=
TCP=
```
