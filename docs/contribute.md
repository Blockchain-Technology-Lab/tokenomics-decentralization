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
this folder is named `<project_name>.json` (for the corresponding ledger) and
contains a dictionary where the key is the address and the value is a dictionary
with the following information:
(i) the name of the entity (that controls the address);
(ii) the source of the information (e.g., an explorer's URL);
(iii) (optional) a boolean value `is_contract` (if omitted then it is assumed false);
(iv) (optional) `extra_info` that might be relevant or interesting (not used for
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
