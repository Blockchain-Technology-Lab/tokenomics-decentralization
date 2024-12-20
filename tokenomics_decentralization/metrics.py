from math import log


def compute_tau(entries, circulation, threshold):
    """
    Calculates the tau index of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :param threshold: float, the parameter of the tau index, i.e. the threshold for the market share
    that is captured by the index
    :returns: an integer of the tau index
    """
    count, share = 0, 0
    for entry in entries:
        market_share = entry / circulation
        if share >= threshold:
            break
        count += 1
        share += market_share

    return count


def compute_gini(entries, circulation):
    """
    Calculates the Gini coefficient of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 1 that represents the Gini coefficient of the given distribution
    """
    parsed_entries = 0
    population = len(entries)
    gini = 1
    for entry in entries:
        richer_population_percentage = parsed_entries / population
        market_share = entry / circulation
        gini -= market_share * ((1 / population) + (2 * richer_population_percentage))
        parsed_entries += 1

    return gini


def compute_hhi(entries, circulation):
    """
    Calculates the Herfindahl-Hirschman index (HHI) of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 10,000 that represents the HHI of the given distribution
    """
    hhi = 0
    for entry in entries:
        market_share = entry / circulation * 100
        hhi += market_share**2

    return hhi


def compute_shannon_entropy(entries, circulation):
    """
    Calculates the Shannon entropy of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: float between 0 and 1 that represents the Shannon entropy of the given distribution
    """
    entropy = 0
    for entry in entries:
        market_share = entry / circulation
        if market_share > 0:
            entropy -= market_share * log(market_share, 2)

    return entropy


def compute_total_entities(entries, circulation):
    """
    Calculates the total number of entities in a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: int that represents the total number of entities in the given distribution
    """
    return len(entries)


def compute_max_power_ratio(entries, circulation):
    """
    Calculates the maximum power ratio of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: float that represents the maximum power ratio among all token holders
    """
    max_balance = entries[0]
    return max_balance / circulation if circulation > 0 else 0


def compute_theil_index(entries, circulation):
    """
    Calculates the Theil-T index of a distribution of balances
    :param entries: list of integers sorted in descending order
    :param circulation: int, the total amount of tokens in circulation
    :returns: float that represents the Thiel index of the given distribution
    """
    N = len(entries)
    if N == 0:
        return 0
    mu = circulation / N
    theil = 0
    for entry in entries:
        x = entry / mu
        if x > 0:
            theil += x * log(x)
    theil /= N
    return theil
