# Plugin example

End-to-end demonstration of a custom giton plugin.

This example registers a tiny shell-script plugin (`my_lint`) that simply
echoes the staged paths it received. It then stages a file, runs the
`pre-commit` trigger, and asserts the plugin actually executed and the
`{paths}` placeholder was correctly expanded.

## Running

```bash
# from the repo root
python -m pytest examples/plugins/test_plugin_lifecycle.py -v
```

You should see:

```
PASSED  test_register_run_and_unregister
PASSED  test_default_catalog_pyqual_command_is_valid
```

## What it covers

| Step                           | API used                                        |
| ------------------------------ | ----------------------------------------------- |
| Build a fake plugin executable | plain `chmod +x`                                |
| Register a plugin record       | `giton.config.upsert_plugin`                    |
| Run the hook trigger           | `giton.runner.run_trigger("pre-commit")`        |
| Inspect placeholder expansion  | reading the file the fake plugin wrote         |
| Unregister                     | `giton.config.remove_plugin`                    |

## Verifying the real default catalog

The catalog ships three default plugins (`pyqual`, `vallm`, `pretest`)
that point at sibling repos under `semcod/`. They are real Python
packages with real CLIs, so you can install one and run it for real:

```bash
giton plugin install pyqual
giton hook pre-commit          # runs `pyqual gates --workdir <repo>`
```

If `pyqual` reports a missing `pyqual.yaml`, run `pyqual init` first —
that's a `pyqual` configuration step, unrelated to giton.
