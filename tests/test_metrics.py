from tokenomics_decentralization.metrics import compute_gini, compute_hhi, compute_shannon_entropy, \
    compute_tau, compute_total_entities


def test_tau_50():
    tokens_per_entity = [3, 2, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.5)
    assert tau_index == 1
    assert tau_market_share == 0.5

    tokens_per_entity = [3, 2, 1, 1, 1, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.5)
    assert tau_index == 2
    assert round(tau_market_share, 2) == 0.56

    tokens_per_entity = [1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.5)
    assert tau_index == 1
    assert tau_market_share == 1


def test_tau_33():
    tokens_per_entity = [3, 2, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.33)
    assert tau_index == 1
    assert tau_market_share == 0.5

    tokens_per_entity = [3, 2, 1, 1, 1, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.33)
    assert tau_index == 1
    assert round(tau_market_share, 2) == 0.33

    tokens_per_entity = [1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.33)
    assert tau_index == 1
    assert tau_market_share == 1


def test_tau_66():
    tokens_per_entity = [3, 2, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.66)
    assert tau_index == 2
    assert round(tau_market_share, 2) == 0.83

    tokens_per_entity = [3, 2, 1, 1, 1, 1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.66)
    assert tau_index == 3
    assert round(tau_market_share, 2) == 0.67

    tokens_per_entity = [1]
    tau_index, tau_market_share = compute_tau(tokens_per_entity, threshold=0.66)
    assert tau_index == 1
    assert tau_market_share == 1


def test_gini():
    """
    Ensure that the results of the compute_gini function are consistent with online calculators,
    such as https://goodcalculators.com/gini-coefficient-calculator/ (5 decimal accuracy)
    """
    balance_distribution = [3, 2, 1]
    gini = compute_gini(balance_distribution)
    assert round(gini, 5) == 0.22222

    balance_distribution = [3, 2, 1, 1, 1, 1]
    gini = compute_gini(balance_distribution)
    assert round(gini, 5) == 0.24074

    balance_distribution = [1]
    gini = compute_gini(balance_distribution)
    assert gini == 0

    balance_distribution = [1, 1, 1]
    gini = compute_gini(balance_distribution)
    assert round(gini, 5) == 0  # Note that this test case fails if we don't round, because of floating point errors


def test_hhi():
    """
    Ensure that the results of the compute_hhi function are consistent with online calculators,
    such as https://www.unclaw.com/chin/teaching/antitrust/herfindahl.htm
    """
    balance_distribution = [3, 2, 1]
    hhi = compute_hhi(balance_distribution)
    assert round(hhi) == 3889

    balance_distribution = [3, 2, 1, 1, 1, 1]
    hhi = compute_hhi(balance_distribution)
    assert round(hhi) == 2099

    balance_distribution = [1]
    hhi = compute_hhi(balance_distribution)
    assert round(hhi) == 10000

    balance_distribution = [1, 1, 1]
    hhi = compute_hhi(balance_distribution)
    assert round(hhi) == 3333


def test_shannon_entropy():
    """
    Ensure that the results of the compute_shannon_entropy function are consistent with online calculators,
    such as: https://www.omnicalculator.com/statistics/shannon-entropy
    """
    balance_distribution = [3, 2, 1]
    entropy = compute_shannon_entropy(balance_distribution)
    assert round(entropy, 3) == 1.459

    balance_distribution = [3, 2, 1, 1, 1, 1]
    entropy = compute_shannon_entropy(balance_distribution)
    assert round(entropy, 3) == 2.419

    balance_distribution = [1]
    entropy = compute_shannon_entropy(balance_distribution)
    assert entropy == 0

    balance_distribution = [1, 1, 1]
    entropy = compute_shannon_entropy(balance_distribution)
    assert round(entropy, 3) == 1.585
    

def test_total_entities():
    balance_distribution = [3, 2, 1]
    total_entities = compute_total_entities(balance_distribution)
    assert total_entities == 3

    balance_distribution = [3, 2, 1, 1, 1, 1]
    total_entities = compute_total_entities(balance_distribution)
    assert total_entities == 6

    balance_distribution = [1]
    total_entities = compute_total_entities(balance_distribution)
    assert total_entities == 1
