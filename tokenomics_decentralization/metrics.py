from math import log


def compute_tau(entries, circulation, threshold):
    """
    Calculates the tau index of a distribution of balances
    :param entries: list of tuples (address, balance), sorted by balance in descending order, where
    address is a string and balance is a numeric type (int or float)
    :param circulation: int, the total amount of tokens in circulation
    :param threshold: float, the parameter of the tau index, i.e. the threshold for the market share
    that is captured by the index
    :returns: list of length two, where the first element is the tau index (int) and the second is the
    percentage of the total market share that is captured by the tau index (float)
    """
    results = [0, 0]

    for entry in entries:
        market_share = int(entry[1]) / circulation
        if results[1] >= threshold:
            break
        results[0] += 1
        results[1] += market_share

    return results


def compute_gini(entries, circulation):
    """
    Calculates the Gini coefficient of a distribution of balances
    :param entries: list of tuples (address, balance), sorted by balance in descending order, where
    address is a string and balance is a numeric type (int or float)
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 1 that represents the Gini coefficient of the given distribution
    """
    parsed_entries = 0
    population = len(entries)
    gini = 1
    for entry in entries:
        richer_population_percentage = parsed_entries / population
        market_share = int(entry[1]) / circulation
        gini -= market_share * ((1 / population) + (2 * richer_population_percentage))
        parsed_entries += 1

    return gini


def compute_hhi(entries, circulation):
    """
    Calculates the Herfindahl-Hirschman index (HHI) of a distribution of balances
    :param entries: list of tuples (address, balance), sorted by balance in descending order, where
    address is a string and balance is a numeric type (int or float)
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 10,000 that represents the HHI of the given distribution
    """
    hhi = 0
    for entry in entries:
        market_share = int(entry[1]) / circulation * 100
        hhi += market_share**2

    return hhi


def compute_shannon_entropy(entries, circulation):
    """
    Calculates the Shannon entropy of a distribution of balances
    :param entries: list of tuples (address, balance), sorted by balance in descending order, where
    address is a string and balance is a numeric type (int or float)
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 1 that represents the Shannon entropy of the given distribution
    """
    entropy = 0
    for entry in entries:
        market_share = int(entry[1]) / circulation
        if market_share > 0:
            entropy -= market_share * log(market_share, 2)

    return entropy


def compute_total_entities(entries, circulation):
    """
    Calculates the total number of entities in a distribution of balances
    :param entries: list of tuples (address, balance), sorted by balance in descending order, where
    address is a string and balance is a numeric type (int or float)
    :param circulation: int, the total amount of tokens in circulation
    :returns: int that represents the total number of entities in the given distribution
    """
    return len(entries)
