# Setup

## Installation

To install the tokenomics decentralization analysis tool, simply clone this GitHub repository:

    git clone https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization.git

The tool is written in Python 3, therefore a Python 3 interpreter is required in order to run it locally.

The [requirements file](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/requirements.txt) lists 
the dependencies of the project.
Make sure you have all of them installed before running the scripts. To install
all of them in one go, run the following command from the root directory of the
project:

    python -m pip install -r requirements.txt

## Execution

The tokenomics decentralization analysis tool is a CLI tool.
To run the tool simply do:

    python run.py

The execution is controlled and parameterized by the configuration file
`config.yml` as follows.

`metrics` defines the metrics that should be computed in the analysis. By
default all supported metrics are included here (to add support for a new metric
see the [conributions
page](https://blockchain-technology-lab.github.io/tokenomics-decentralization/contribute/)).

`ledgers` defines the ledgers that should be analyzed. By default, all supported
ledgers are included here (to add support for a new ledger see the [conributions
page](https://blockchain-technology-lab.github.io/tokenomics-decentralization/contribute/)).

`execution_flags` defines various flags that control the data handling:

* `force_map_addresses`: the address helper data from the directory
  `mapping_information` is re-computed; you should set this flag to true if the
  data has been updated since the last execution for the given ledger
* `force_map_balances`: the balance data of the ledger's addresses is
  recomputed; you should set this flag to true if the data has been updated
  since the last execution for the given ledger
* `force_analyze`: the computation of a metric is recomputed; you should set
  this flag to true if any type of data has been updated since the last
  execution for the given ledger

`analyze_flags` defines various analysis-related flags:

* `no_clustering`: a boolean that disables clustering of addresses (under the
  same entity, as defined in the mapping information)
* `top_limit_type`: a string of two values (`absolute` or `percentage`) that
  enables applying a threshold on the addresses that will be considered
* `top_limit_value`: the value of the top limit that should be applied; if 0,
  then no limit is used (regardless of the value of `top_limit_type`); if the
  type is `absolute`, then the `top_limit_value` should be an integer (e.g., if
  set to 100, then only the 100 wealthiest entities/addresses will be considered
  in the analysis); if the type is `percentage` the the `top_limit_value` should
  be an integer (e.g., if set to 0.50, then only the top 50% of wealthiest
  entities/addresses will be considered)
* `exclude_contract_addresses`: a boolean value that enables the exclusion of
  contract addresses from the analysis
* `exclude_below_usd_cent`: a boolean value that enables the exclusion of
  addresses, the balance of which at the analyzed point in time was less than
  $0.01 (based on the historical price information in the directory
  `price_data`)

`snapshot_dates` and `granularity` control the snapshots for which an analysis
will be performed. `granularity` is a string that can be empty or one of `day`, `week`,
`month`, `year`. If granularity is empty, then `snapshot_dates` define the exact
time points for which an analysis will be conducted, in the form YYYY-MM-DD.
Otherwise, if granularity is set, then the two farthest entries in
`snapshot_dates` define the timeframe over which the analysis will be conducted,
at the set granular rate. For example, if the farthest points are `2010` and
`2023` and the granularity is set to `month`, then (the first day of) every
month in the years 2010-2023 (inclusive) will be analyzed.

`input_directories` and `output_directories` are both lists of directories that
define the source of data. `input_directories` defines the directories that
contain raw address balance information, as obtained from BigQuery or a full
node (for more information about this see the [data collection
page](https://blockchain-technology-lab.github.io/tokenomics-decentralization/data/)).
`output_directories` defines the directories to store the databases which
contain the mapping information and analyzed data. The first entry in the output
directories is also used to store the output files of the analysis and the
plots.

Finally, `plot_parameters` contains various parameters that control the type and
data that will be produced as plots.
...
