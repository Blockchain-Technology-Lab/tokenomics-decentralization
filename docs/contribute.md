# How to contribute

You can contribute to the tool by adding support for a ledger, updating the
mapping process for an existing ledger, or adding a new metric. In all cases,
the information should be submitted via a GitHub PR.

## Add support for ledgers

You can add support for a ledger that is not already supported as follows.

### Mapping information

In the directory `mapping_information/`, there exist two folders: `addresses`
and `special_addresses`.

`addresses` contains information about the owner or manager of an address. This
information should be publicly available and verifiable, for example it may come
from a public explorer, social media or forum posts, articles, etc. Each file in
this folder is named `<project_name>.jsonl` (for the corresponding ledger) and
contains a dictionary per line with the following information:
(i) the address;
(ii) the name of the entity (that controls the address);
(iii) the source of the information (e.g., an explorer's URL);
(iv) (optional) a boolean value `is_contract` (if omitted then it is assumed false);
(v) (optional) `extra_info` that might be relevant or interesting (not used for
the analysis).

`special_addresses` contains information about addresses that should be treated
specially, e.g., excluded from the analysis. This includes burn addresses,
protocol-related addresses (e.g., Ethereum's staking contract), treasury
addresses, etc. Here each file is named `<project_name>.json` and contains a
list of dictionaries with the following information:
(i) the address;
(ii) the source of the information;
(iii) `extra_info` which describes the reason why the address is special.

To contribute mapping information you can either update an existing file, by
changing and/or adding some entries, or create a new file for a newly-supported
ledger.

Note: If you add an entry in `mapping_addresses` with a source that does not
already exist, you should also add this source in the file
`mapping_information/sources.json`. Specifically, if it comes from a
publicly-available website you should add it under "Explorers", otherwise either
use an existing appropriate keyword or create a new one. If you create a new
one, make sure to also include it in the configuration file `config.yaml` and in
the description of the [Setup
page](https://blockchain-technology-lab.github.io/tokenomics-decentralization/setup/)).

### Price information

The directory `price_data/` contains information about the supported ledgers'
market price. Each file in this folder is named `<project_name>.csv` (for the
corresponding ledger). The csv file has no header and each line contains two
comma-separated values:
(i) a day (in the form YYYY-MM-DD);
(ii) the USD market price of the token on the set day.

To contribute price information you can either update an existing file, by
adding entries for days where data is missing, or create a new file for a
newly-supported ledger and add historical price data.

## Add metrics

To add a new metric, you should do the following steps.

First, create a relevant function in the script
`tokenomics_decentralization/metrics.py`. The function should be named
`compute_{metric_name}` and is given two parameters:
(i) a list of tuples, where each tuple's first value is a numeric type that
defines the balance of an address;
(ii) an integer that defines the circulation (that is the sum of all address
balances).

Second, import this new function to `tokenomics_decentralization/analyze.py`.
In this file, include the function as the value to the dictionary
`compute_functions` of the `analyze_snapshot` function, using as a key the name
of the function (which will be used in the config file).

Third, add the name of the metric (which was used as the key to the dictionary
in `analyze.py`) to the file `config.yaml` under `metrics`. You can optionally
also add it under the plot parameters, if you want it to be included in the
plots by default.

Finally, you should add unit tests for the new metric
[here](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/tree/main/tests)
and update the [corresponding documentation
page](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/docs/metrics.md)
