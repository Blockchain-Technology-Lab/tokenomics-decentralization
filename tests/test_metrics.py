from tokenomics_decentralization.metrics import compute_gini, compute_hhi, compute_shannon_entropy, \
    compute_tau, compute_total_entities, compute_max_power_ratio, compute_theil_index


def test_tau_50():
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=6, threshold=0.5)
    assert tau_index == 1

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=9, threshold=0.5)
    assert tau_index == 2

    tokens_per_entity = [(1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=1, threshold=0.5)
    assert tau_index == 1


def test_tau_33():
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=6, threshold=0.33)
    assert tau_index == 1

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=9, threshold=0.33)
    assert tau_index == 1

    tokens_per_entity = [(1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=1, threshold=0.33)
    assert tau_index == 1


def test_tau_66():
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=6, threshold=0.66)
    assert tau_index == 2

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=9, threshold=0.66)
    assert tau_index == 3

    tokens_per_entity = [(1, )]
    tau_index = compute_tau(tokens_per_entity, circulation=1, threshold=0.66)
    assert tau_index == 1


def test_gini():
    """
    Ensure that the results of the compute_gini function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    gini = compute_gini(tokens_per_entity, circulation=6)
    assert round(gini, 5) == 0.22222

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    gini = compute_gini(tokens_per_entity, circulation=9)
    assert round(gini, 5) == 0.24074

    tokens_per_entity = [(1, )]
    gini = compute_gini(tokens_per_entity, circulation=1)
    assert gini == 0

    tokens_per_entity = [(1, ), (1, ), (1, )]
    gini = compute_gini(tokens_per_entity, circulation=3)
    assert round(gini, 5) == 0  # Note that this test case fails if we don't round, because of floating point errors


def test_hhi():
    """
    Ensure that the results of the compute_hhi function are consistent with online calculators,
    such as https://www.unclaw.com/chin/teaching/antitrust/herfindahl.htm
    """
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    hhi = compute_hhi(tokens_per_entity, circulation=6)
    assert round(hhi) == 3889

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    hhi = compute_hhi(tokens_per_entity, circulation=9)
    assert round(hhi) == 2099

    tokens_per_entity = [(1, )]
    hhi = compute_hhi(tokens_per_entity, circulation=1)
    assert round(hhi) == 10000

    tokens_per_entity = [(1, ), (1, ), (1, )]
    hhi = compute_hhi(tokens_per_entity, circulation=3)
    assert round(hhi) == 3333


def test_shannon_entropy():
    """
    Ensure that the results of the compute_shannon_entropy function are consistent with online calculators,
    such as: https://www.omnicalculator.com/statistics/shannon-entropy
    """
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=6)
    assert round(entropy, 3) == 1.459

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=9)
    assert round(entropy, 3) == 2.419

    tokens_per_entity = [(1, )]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=1)
    assert entropy == 0

    tokens_per_entity = [(1, ), (1, ), (1, )]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=3)
    assert round(entropy, 3) == 1.585


def test_total_entities():
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    total_entities = compute_total_entities(tokens_per_entity, circulation=6)
    assert total_entities == 3

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    total_entities = compute_total_entities(tokens_per_entity, circulation=9)
    assert total_entities == 6

    tokens_per_entity = [(1, )]
    total_entities = compute_total_entities(tokens_per_entity, circulation=1)
    assert total_entities == 1


def test_compute_max_power_ratio():
    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    max_mpr = compute_max_power_ratio(tokens_per_entity, circulation=6)
    assert max_mpr == 0.5

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    max_mpr = compute_max_power_ratio(tokens_per_entity, circulation=9)
    assert max_mpr == 1 / 3

    tokens_per_entity = [(1, )]
    max_mpr = compute_max_power_ratio(tokens_per_entity, circulation=1)
    assert max_mpr == 1

    tokens_per_entity = [(1, ), (1, ), (1, )]
    max_mpr = compute_max_power_ratio(tokens_per_entity, circulation=3)
    assert max_mpr == 1 / 3


def test_compute_theil_index():
    """
    Ensure that the results of the compute_theil_index function are consistent with online calculators,
    such as: http://www.poorcity.richcity.org/calculator/
    """
    decimals = 3

    tokens_per_entity = [(3.0, ), (2, ), (1, )]
    theil_t = compute_theil_index(tokens_per_entity, 6)
    assert round(theil_t, decimals) == 0.087

    tokens_per_entity = [(3, ), (2, ), (1, ), (1, ), (1, ), (1, )]
    theil_t = compute_theil_index(tokens_per_entity, 9)
    assert round(theil_t, decimals) == 0.115

    tokens_per_entity = [(432, ), (0, ), (0, ), (0, )]
    theil_t = compute_theil_index(tokens_per_entity, 432)
    assert round(theil_t, decimals) == 1.386

    tokens_per_entity = [(432, )]
    theil_t = compute_theil_index(tokens_per_entity, 432)
    assert round(theil_t, decimals) == 0

    tokens_per_entity = []
    theil_t = compute_theil_index(tokens_per_entity, 432)
    assert theil_t == 0
