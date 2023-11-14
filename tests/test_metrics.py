from tokenomics_decentralization.metrics import compute_gini, compute_hhi, compute_shannon_entropy, \
    compute_tau, compute_total_entities


def test_tau_50():
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=6, threshold=0.5)
    assert tau_index == 1
    assert tau_market_share == 0.5

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=9, threshold=0.5)
    assert tau_index == 2
    assert round(tau_market_share, 2) == 0.56

    tokens_per_entity = [('a', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=1, threshold=0.5)
    assert tau_index == 1
    assert tau_market_share == 1


def test_tau_33():
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=6, threshold=0.33)
    assert tau_index == 1
    assert tau_market_share == 0.5

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=9, threshold=0.33)
    assert tau_index == 1
    assert round(tau_market_share, 2) == 0.33

    tokens_per_entity = [('a', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=1, threshold=0.33)
    assert tau_index == 1
    assert tau_market_share == 1


def test_tau_66():
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=6, threshold=0.66)
    assert tau_index == 2
    assert round(tau_market_share, 2) == 0.83

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=9, threshold=0.66)
    assert tau_index == 3
    assert round(tau_market_share, 2) == 0.67

    tokens_per_entity = [('a', 1)]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, circulation=1, threshold=0.66)
    assert tau_index == 1
    assert tau_market_share == 1


def test_gini():
    """
    Ensure that the results of the compute_gini function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    gini = compute_gini(tokens_per_entity, circulation=6)
    assert round(gini, 5) == 0.22222

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    gini = compute_gini(tokens_per_entity, circulation=9)
    assert round(gini, 5) == 0.24074

    tokens_per_entity = [('a', 1)]
    gini = compute_gini(tokens_per_entity, circulation=1)
    assert gini == 0

    tokens_per_entity = [('a', 1), ('b', 1), ('c', 1)]
    gini = compute_gini(tokens_per_entity, circulation=3)
    assert round(gini, 5) == 0  # Note that this test case fails if we don't round, because of floating point errors


def test_hhi():
    """
    Ensure that the results of the compute_hhi function are consistent with online calculators,
    such as https://www.unclaw.com/chin/teaching/antitrust/herfindahl.htm
    """
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    hhi = compute_hhi(tokens_per_entity, circulation=6)
    assert round(hhi) == 3889

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    hhi = compute_hhi(tokens_per_entity, circulation=9)
    assert round(hhi) == 2099

    tokens_per_entity = [('a', 1)]
    hhi = compute_hhi(tokens_per_entity, circulation=1)
    assert round(hhi) == 10000

    tokens_per_entity = [('a', 1), ('b', 1), ('c', 1)]
    hhi = compute_hhi(tokens_per_entity, circulation=3)
    assert round(hhi) == 3333


def test_shannon_entropy():
    """
    Ensure that the results of the compute_shannon_entropy function are consistent with online calculators,
    such as: https://www.omnicalculator.com/statistics/shannon-entropy
    """
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=6)
    assert round(entropy, 3) == 1.459

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=9)
    assert round(entropy, 3) == 2.419

    tokens_per_entity = [('a', 1)]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=1)
    assert entropy == 0

    tokens_per_entity = [('a', 1), ('b', 1), ('c', 1)]
    entropy = compute_shannon_entropy(tokens_per_entity, circulation=3)
    assert round(entropy, 3) == 1.585
    

def test_total_entities():
    tokens_per_entity = [('a', 3.0), ('b', 2), ('c', 1)]
    total_entities = compute_total_entities(tokens_per_entity, circulation=6)
    assert total_entities == 3

    tokens_per_entity = [('a', 3), ('b', 2), ('c', 1), ('d', 1), ('e', 1), ('f', 1)]
    total_entities = compute_total_entities(tokens_per_entity, circulation=9)
    assert total_entities == 6

    tokens_per_entity = [('a', 1)]
    total_entities = compute_total_entities(tokens_per_entity, circulation=1)
    assert total_entities == 1
