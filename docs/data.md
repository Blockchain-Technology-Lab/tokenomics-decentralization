# Data collection

Currently, the data for the analysis of the different ledgers is collected through 
[Google BigQuery](https://console.cloud.google.com/bigquery) .


## Queries

One can retrieve the data directly from BigQuery using the queries below:

### Bitcoin

```
WITH double_entry_book AS (
        SELECT array_to_string(inputs.addresses, ",") as address, inputs.type, -inputs.value as value
        FROM `bigquery-public-data.crypto_bitcoin.inputs` as inputs
        WHERE block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT array_to_string(outputs.addresses, ",") as address, outputs.type, outputs.value as value
        FROM `bigquery-public-data.crypto_bitcoin.outputs` as outputs
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address, type, sum(value) as balance
    FROM double_entry_book
    GROUP BY 1,2
    HAVING balance > 0
    ORDER BY balance DESC
```

### Bitcoin Cash

```
WITH double_entry_book AS (
        SELECT array_to_string(inputs.addresses, ",") as address, inputs.type, -inputs.value as value
        FROM `bigquery-public-data.crypto_bitcoin_cash.inputs` as inputs
        WHERE block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT array_to_string(outputs.addresses, ",") as address, outputs.type, outputs.value as value
        FROM `bigquery-public-data.crypto_bitcoin_cash.outputs` as outputs
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address, type, sum(value) as balance
    FROM double_entry_book
    GROUP BY 1,2
    HAVING balance > 0
    ORDER BY balance DESC
```

### Dogecoin

```
WITH double_entry_book AS (
        SELECT array_to_string(inputs.addresses, ",") as address, inputs.type, -inputs.value as value
        FROM `bigquery-public-data.crypto_dogecoin.inputs` as inputs
        WHERE block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT array_to_string(outputs.addresses, ",") as address, outputs.type, outputs.value as value
        FROM `bigquery-public-data.crypto_dogecoin.outputs` as outputs
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address,   type,   sum(value) as balance
    FROM double_entry_book
    GROUP BY 1,2
    HAVING balance > 0
    ORDER BY balance DESC
```

### Ethereum

```
WITH double_entry_book AS (
        SELECT to_address as address, value AS value
        FROM `bigquery-public-data.crypto_ethereum.traces`
        WHERE to_address IS NOT null
        AND status = 1
        AND (call_type NOT IN ('delegatecall', 'callcode', 'staticcall') OR call_type IS null)
        AND block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT from_address as address, -value AS value
        FROM `bigquery-public-data.crypto_ethereum.traces`
        WHERE from_address IS NOT null
        AND status = 1
        AND (call_type NOT IN ('delegatecall', 'callcode', 'staticcall') OR call_type IS null)
        AND block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT miner AS address, sum(cast(receipt_gas_used as numeric) * cast(gas_price as numeric)) AS value
        FROM `bigquery-public-data.crypto_ethereum.transactions` AS transactions
        JOIN `bigquery-public-data.crypto_ethereum.blocks` AS blocks on blocks.number = transactions.block_number
        WHERE transactions.block_timestamp < "{{timestamp}}"
        GROUP BY blocks.miner
        UNION ALL
        SELECT from_address AS address, -(cast(receipt_gas_used as numeric) * cast(gas_price as numeric)) AS value
        FROM `bigquery-public-data.crypto_ethereum.transactions`
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address, sum(value) AS balance
    FROM double_entry_book
    GROUP BY address
    HAVING balance > 0
    ORDER BY balance DESC
```

### Litecoin

```
WITH double_entry_book AS (
        SELECT array_to_string(inputs.addresses, ",") as address, inputs.type, -inputs.value as value
        FROM `bigquery-public-data.crypto_litecoin.inputs` as inputs
        WHERE block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT array_to_string(outputs.addresses, ",") as address, outputs.type, outputs.value as value
        FROM `bigquery-public-data.crypto_litecoin.outputs` as outputs
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address,   type,   sum(value) as balance
    FROM double_entry_book
    GROUP BY 1,2
    HAVING balance > 0
    ORDER BY balance DESC
```

### Tezos

```
WITH double_entry_book as (
        SELECT IF(kind = 'contract', contract, delegate) AS address, change AS value
        FROM `public-data-finance.crypto_tezos.balance_updates`
        WHERE (status IS NULL OR status = 'applied') AND (timestamp < "{{timestamp}}")
        UNION ALL
        SELECT address, balance_change
        FROM `public-data-finance.crypto_tezos.migrations`
        WHERE timestamp < "{{timestamp}}"
    )
    SELECT address, SUM(value) AS balance
    FROM double_entry_book
    GROUP BY address
    HAVING balance > 0
    ORDER BY balance DESC
```

### Zcash

```
WITH double_entry_book AS (
        SELECT array_to_string(inputs.addresses, ",") as address, inputs.type, -inputs.value as value
        FROM `bigquery-public-data.crypto_zcash.inputs` as inputs
        WHERE block_timestamp < "{{timestamp}}"
        UNION ALL
        SELECT array_to_string(outputs.addresses, ",") as address, outputs.type, outputs.value as value
        FROM `bigquery-public-data.crypto_zcash.outputs` as outputs
        WHERE block_timestamp < "{{timestamp}}"
    )
    SELECT address,   type,   sum(value) as balance
    FROM double_entry_book
    GROUP BY 1,2
    HAVING balance > 0
    ORDER BY balance DESC
```

## Automating the data collection process

Instead of executing each of these queries separately on the BigQuery console and saving the results manually, it is
also possible to automate the process using a
[script](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/data_collection_scripts/big_query_balance_data.py)
and collect all relevant data in one go. Executing this script will run queries
from [this file](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/data_collection_scripts/queries.yaml).

IMPORTANT: the script uses service account credentials for authentication, therefore before running it, you need to
generate the relevant credentials from Google, as described 
[here](https://developers.google.com/workspace/guides/create-credentials#service-account) and save your key in the
`data_collections_scripts/` directory of the project under the name 'google-service-account-key-0.json'. Any additional
keys should be named 'google-service-account-key-1.json', 'google-service-account-key-2.json', and so on.
There is a
[sample file](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/data_collection_scripts/google-service-account-key-SAMPLE.json) 
that you can consult, which shows what your credentials are supposed to look like (but note that this is for
informational purposes only, this file is not used in the code).

Once you have set up the credentials, you can just run the following command from the root
directory to retrieve data for all supported blockchains:

`python -m data_collection_scripts.big_query_balance_data`

There are also three command line arguments that can be used to customize the data collection process:

- `ledgers` accepts any number of the supported ledgers (case-insensitive). For example, adding `--ledgers bitcoin`
  results in collecting data only for Bitcoin, while `--ledgers Bitcoin Ethereum` would collect data for
  Bitcoin and Ethereum. If the `ledgers` argument is omitted, then the default value is used, which 
  is taken from the
  [configuration file](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/config.yaml)
  and typically corresponds to all supported blockchains.
- `snapshot_dates` accepts any number of dates formatted as YYYY-MM-DD, YYYY-MM, or YYYY. Then, data is collected for
  the specified date(s). Again, if this argument is omitted, the default value is taken from the 
  [configuration file](https://github.com/Blockchain-Technology-Lab/tokenomics-decentralization/blob/main/config.yaml).
- `--force-query` forces the collection of all raw data files, even if some or all of the files already
  exist. By default, this flag is set to False and the script only fetches data for some blockchain if the
  corresponding file does not already exist.
