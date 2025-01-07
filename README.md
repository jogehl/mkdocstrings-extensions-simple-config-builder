# mkdocstrings_extensions_simple_config_builder

[![PyPI - Version](https://img.shields.io/pypi/v/mkdocstrings-extensions-simple-config-builder.svg)](https://pypi.org/project/mkdocstrings-extensions-simple-config-builder)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocstrings-extensions-simple-config-builder.svg)](https://pypi.org/project/mkdocstrings-extensions-simple-config-builder)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install mkdocstrings-extensions-simple-config-builder
```

## How to use

You can use this extension as a extension for the mkdocs python handler
to get extra information for the @configclass decorated classes.
    
```yaml
- mkdocstrings:
    handlers:
        python:
            options:
                extensions:
                    - mkdocstrings_extensions_simple_config_builder
```

## License

`mkdocstrings-extensions-simple-config-builder` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
