# Tokenomics Blockchain Decentralization

This repository provides a CLI tool for analyzing the wealth ownership of various blockchains and measuring their 
subsequent levels of decentralization. Please refer to the project's
[documentation pages](https://blockchain-technology-lab.github.io/tokenomics-decentralization/) for details on its architecture,
required input, produced output, and more.

Currently, the supported blockchains are:
- Bitcoin
- Bitcoin Cash
- Cardano
- Dogecoin
- Ethereum
- Litecoin
- Tezos
We intend to add more ledgers to this list in the future.

## Installation

To install the tool, simply clone this project:

    git clone https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization.git

The [requirements file](requirements.txt) lists the dependencies of the project.
Make sure you have all of them installed before running the scripts. To install
all of them in one go, run the following command from the root directory of the
project:

    python -m pip install -r requirements.txt

### Mapping information

The mapping information for Cardano is too large for Github.
To retrieve it do the following:
- Download the file from
[here](https://uoe-my.sharepoint.com/:u:/g/personal/dkarakos_ed_ac_uk/ETgyf9W-JdtGlF5Ln8yj7zQB2uwtQLzB22oQDEfbvIn9Zg?e=HjXlxd&download=1).
- Move the file to the folder `mapping_information/addresses/`. Note that the file should be named `cardano.json`.

## Run the tool

Place all raw data (which could be collected from [BigQuery](https://cloud.google.com/bigquery/) for example) in the `input` directory. 
Each file named as `<project_name>_<snapshot_date>_raw_data.json` (e.g. `bitcoin_{2023-01-01}_raw_data.json`). By default, there
is a (very small) sample input file for some supported projects. To use the
samples, remove the prefix `sample_`. For more extended raw data and instructions on how to retrieve it, see
[here](https://blockchain-technology-lab.github.io/tokenomics-decentralization/data/).

Run `python run.py --ledgers <ledger_1> ... <ledger_n> --snapshots <date_1> <date_2>` to produce and analyze the database files.
For each ledger and for each snapshot one SQLite file is created, which contains the address mapping and the balance information.
Note that both arguments are optional, so it's possible to omit one or both of them (in which case the default values
will be used). Specifically:

- The `ledgers` argument accepts any number of supported ledgers (case-insensitive). 
For example, `--ledgers bitcoin` runs the analysis for Bitcoin, `--ledgers Bitcoin Ethereum Cardano` runs the analysis 
for Bitcoin, Ethereum and Cardano, etc. Ledgers with  more words should be defined with an underscore; for example 
Bitcoin Cash should be set as `bitcoin_cash`.
- The `snapshots` argument should be of the form `YYYY-MM-DD`. 
For example, `--snapshots 2022-02-01` runs it for 1 February 2022.

`run.py` prints on stdout the output of each implemented metric for the specified ledgers and snapshot.

To mass produce and analyze data, omit one or both arguments. If some arguments
are omitted, the default values from `config.yaml` will be used. If only the
`ledgers` is given, all snapshots for which a raw data and/or database file exists will be
analyzed. If only the timeframe is specified, all ledgers will be analyzed for
the given timeframe (if the raw data and/or database files exist).

A single file `output.csv` is also created in the `output` directory, containing the output data from the 
last execution of `run.py`.

## Contributing

Everyone is welcome to contribute ideas, report bugs, and make the code more efficient. We especially welcome contributions to the following areas:

- Add support for a ledger that is not already supported.
- Update and/or add mapping information for a ledger.
- Add a new metric.

For detailed information on how to contribute see the relevant [documentation
page](https://blockchain-technology-lab.github.io/tokenomics-decentralization/contribute/).

## Maintainers

The tool is actively maintained by the following developers:

- [Dimitris Karakostas](https://github.com/dimkarakostas)
- [Christina Ovezik](https://github.com/LadyChristina)

*Note*: When opening a Pull Request, you must request a review from at least *2*
people in the above list.

## License

The code of this repository is released under the [MIT License](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/LICENSE).
The documentation pages are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
