from math import log


def compute_tau(balance_distribution, threshold):
    """
    Calculates the tau index of a distribution of balances
    :param balance_distribution: a *sorted* list of integers, each corresponding to the balance of an entity,
        sorted in descending order
    :param threshold: float, the parameter of the tau index, i.e. the threshold for the market share 
        that is captured by the index
    :returns: tuple of (int, float) where the first element is the tau index and the second is the 
        percentage of the total market share that is captured by the tau index
    """
    tau_index, tau_market_share = 0, 0
    circulation = sum(balance_distribution)

    for balance in balance_distribution:
        if tau_market_share >= threshold:
            break
        market_share = balance / circulation
        tau_index += 1
        tau_market_share += market_share
    return tau_index, tau_market_share


def compute_gini(balance_distribution):
    """
    Calculates the Gini coefficient of a distribution of balances
    :param balance_distribution: a *sorted* list of integers, each corresponding to the balance of an entity,
        sorted in descending order
    :returns: float between 0 and 1 that represents the Gini coefficient of the given distribution
    """
    parsed_balances = 0
    circulation = sum(balance_distribution)
    population = len(balance_distribution)
    gini = 1
    for balance in balance_distribution:
        richer_population_percentage = parsed_balances / population
        market_share = balance / circulation
        gini -= market_share * ((1 / population) + (2 * richer_population_percentage))
        parsed_balances += 1

    return gini


def compute_hhi(balance_distribution):
    """
    Calculates the Herfindahl-Hirschman index (HHI) of a distribution of balances
    :param balance_distribution: a list of integers, each corresponding to the balance of an entity
    :returns: float between 0 and 10,000 that represents the HHI of the given distribution
    """
    circulation = sum(balance_distribution)
    hhi = 0
    for balance in balance_distribution:
        market_share = balance / circulation * 100
        hhi += market_share**2

    return hhi


def compute_shannon_entropy(balance_distribution):
    """
    Calculates the Shannon entropy of a distribution of balances
    :param balance_distribution: a list of integers, each corresponding to the balance of an entity
    :returns: float between 0 and 1 that represents the Shannon entropy of the given distribution
    """
    circulation = sum(balance_distribution)
    entropy = 0
    for balance in balance_distribution:
        market_share = balance / circulation
        if market_share > 0:
            entropy -= market_share * log(market_share, 2)

    return entropy


def compute_total_entities(balance_distribution):
    """
    Calculates the total number of entities in a distribution of balances
    :param balance_distribution: a list of integers, each corresponding to the balance of an entity
    :returns: int that represents the total number of entities in the given distribution
    """
    return len(balance_distribution)
