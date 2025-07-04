# Mica Python [![CI](https://github.com/obiba/mica-python-client/actions/workflows/ci.yml/badge.svg)](https://github.com/obiba/mica-python-client/actions/workflows/ci.yml)

This Python-based command line tool allows to access to a Mica server through its REST API. This is the perfect tool
for automating tasks in Mica. This will be the preferred client developed when new features are added to the REST API.

* Read the [documentation](http://micadoc.obiba.org).
* Have a bug or a question? Please create a [GitHub issue](https://github.com/obiba/mica-python-client/issues).
* Continuous integration is on [GitHub actions](https://github.com/obiba/mica-python-client/actions).

## Usage

Install with:

```
pip install obiba-mica
```

To get the options of the command line:

```
mica --help
```

This command will display which sub-commands are available. For each sub-command you can get the help message as well:

```
mica <subcommand> --help
```

The objective of having sub-command is to hide the complexity of applying some use cases to the Mica REST API. More
sub-commands will be developed in the future.

## Development

Mica Python client can be easily extended by using the classes defined in `core.py` file.

## Mailing list

Have a question? Ask on our mailing list!

obiba-users@googlegroups.com

[http://groups.google.com/group/obiba-users](http://groups.google.com/group/obiba-users)

## License

OBiBa software are open source and made available under the [GPL3 licence](http://www.obiba.org/pages/license/). OBiBa software are free of charge.

## OBiBa acknowledgments

If you are using OBiBa software, please cite our work in your code, websites, publications or reports.

"The work presented herein was made possible using the OBiBa suite (www.obiba.org), a  software suite developed by Maelstrom Research (www.maelstrom-research.org)"
