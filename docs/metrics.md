# Metrics

The metrics that have been implemented so far are the following:

1. **Nakamoto coefficient**: The Nakamoto coefficient represents the minimum number of entities that
   collectively produce more than 50% of the total blocks within a given timeframe. The output of the metric is an
   integer.
2. **Gini coefficient**: The Gini coefficient represents the degree of inequality in block production. The
   output of the metric is a decimal number in [0,1]. Values close to 0 indicate equality (all entities in
   the system produce the same number of blocks) and values close to 1 indicate inequality (one entity
   produces most or all blocks).
3. **Entropy**: Shannon entropy represents the expected amount of information in the distribution of blocks across entities.
   The output of the metric is a real number. Typically, a higher value of entropy indicates higher decentralization
   (lower predictability).
4. **HHI**: The Herfindahl-Hirschman Index (HHI) is a measure of market concentration. It is defined as the sum of the
   squares of the market shares (as whole numbers, e.g. 40 for 40%) of the entities in the system. The output of the
   metric is a real number in (0, 10000]. Values close to 0 indicate low concentration (many entities produce a similar
   number of blocks) and values close to 1 indicate high concentration (one entity produces most or all blocks).
   The U.S. Department of Justice has set the following thresholds for interpreting HHI values (in traditional markets):
    - (0, 1500): Competitive market
    - [1500, 2500]: Moderately concentrated market
    - (2500, 10000]: Highly concentrated market
5. **Theil index**: The Theil index is another measure of entropy which is intended to capture the lack of diversity,
   or the redundancy, in a population. In practice, it is calculated as the maximum possible entropy minus the observed
   entropy. The output is a real number. Values close to 0 indicate equality and values towards infinity indicate
   inequality. Therefore, a high Theil Index suggests a population that is highly centralized.
6. **Max power ratio**: The max power ratio represents the share of blocks that are produced by the most "powerful"
   entity, i.e. the entity that produces the most blocks. The output of the metric is a decimal number in [0,1].
7. **Tau-decentralization index**: The tau-decentralization index is a generalization of the Nakamoto coefficient.
   It is defined as the minimum number of entities that collectively produce more than a given threshold of the total
   blocks within a given timeframe. The threshold parameter is a decimal in [0, 1] (0.66 by default) and the output of
   the metric is an integer.
