# Examples

Here you can find examples of how to use the library. Most examples are configured using environment variables, so make sure to set them before running the examples. The easiest way to do this is to create a `.env` file in the root of the project and set the environment variables there. The following is an example of a `.env` file:

```bash
# .env
WANDELAPI_BASE_URL=https://fjzerrus.instance.wandelbots.io
NOVA_USERNAME=wb
NOVA_PASSWORD=ys7uYhiVBGCUW3UrQGQFmvri11kdTC6R
MOTION_GROUP=0@virtual
CELL_ID=cell
TCP=Flange
```

# Python Examples

## 01-Basic

The [01_basic](01_basic.py) example demonstrates how to create an `Instance` and `MotionGroup` object, and how to use them to interact with the Wandelbots API.

## 02-Plan-and-Execute

The [02_plan_and_execute](02_plan_and_execute.py) example demonstrates how to plan a motion using the `Planner` and execute it on the configured motion group.

## 03-Plan-and-Execute-Async

The [03_plan_and_execute_async](03_plan_and_execute_async.py) example demonstrates how to plan a motion asynchronously and execute it on the configured motion group asynchronously.

## 04-Execute-in-Background

The [04_execute_in_background](04_execute_in_background.py) example demonstrates how to execute a motion in the background.

# Jupyter-Notebook Examples

## 05-Jupyter-Notebook

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/wandelbotsgmbh/wandelbots-python/HEAD?labpath=examples%2F05_notebook.ipynb)

The [05_notebook](05_notebook.ipynb) example demonstrates how to use the library in a Jupyter notebook.
