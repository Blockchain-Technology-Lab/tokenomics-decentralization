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

### System requirements

Running the tool requires loading the raw input data on memory. To avoid running
out of memory, we recommend RAM at least double the largest raw data file.

### Mapping information

The mapping information for Cardano is too large for Github.
To retrieve it do the following:
- Download the file from
[here](https://uoe-my.sharepoint.com/:u:/g/personal/dkarakos_ed_ac_uk/EXseoT-v1xBHn1TWG1IvqHIB2L3Pm35-UtKIcUKmk1IQZw?e=YgTfjR&download=1).
- Move the file to the folder `mapping_information/addresses/`. The file _should be named_ `cardano.jsonl`.

## Run the tool

Place all raw data (which could be collected from
[BigQuery](https://cloud.google.com/bigquery/) for example) in the `input`
directory.  Each file named as `<project_name>_<snapshot_date>_raw_data.json`
(e.g.  `bitcoin_2023-01-01_raw_data.json`). By default, there is a (very
small) sample input file for some supported projects. To use the samples, remove
the prefix `sample_`. For more extended raw data and instructions on how to
retrieve it, see [here](https://blockchain-technology-lab.github.io/tokenomics-decentralization/data/).

Edit the configuration file `config.yaml` to choose which ledgers to analyze,
for which snapshots, with which metrics, etc (see
[here](https://blockchain-technology-lab.github.io/tokenomics-decentralization/setup/)
for more information on each parameter).

Run `python run.py` to perform the analysis and print on stdout the output of
each implemented metric for the specified ledgers and snapshot.

For each ledger and for the chosen combination of mapping sources, a SQLite file
is created in `mapping_information/addresses`, which contains the address
mapping information.

A single file `output_{params}.csv` is also created in the `output` directory,
containing the output data from the last execution of `run.py`. Here, "params"
corresponds to analysis parameters like whether to apply clustering,
thresholding, etc.

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


## License

The code of this repository is released under the [MIT License](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/LICENSE).
The documentation pages are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
