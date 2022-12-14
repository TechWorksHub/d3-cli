import networkx as nx
from .check_behaviours_resolve import BehaviourMap, BehaviourJson
from iteration_utilities import unique_everseen
from typing import List, Dict


def _get_item(collection: List[Dict], key: str, target: str or int or float):
    """
    Get item in collection (array of dictionaries) by key and target value, if a match exists.

    E.g. _get_item([{"name": "Bob"}, {"name": "Alice"}, {"name": "Carl"}, {"name": "Dobby"}], "name", "Alice")
    will return the {"name": "Alice"} dictionary. If no matches exist, function will return None.

    Args:
        collection: Array of dictionaries
        key: Key in dictionary to match against
        target: Target value to match against

    Returns:
        Matching Dictionary
    """
    return next((item for item in collection if item.get(key, None) == target), None)


def resolve_behaviour_rules(
    claim: BehaviourJson, claim_map: BehaviourMap, claim_graph: nx.DiGraph
) -> List[Dict]:
    """
    Resolve rules which apply for behaviour claim from parent behaviour inheritance.

    Args:
        claim: The D3 behaviour claim to resolve behaviour for
        claim_map: Map of D3 claim GUID to D3 behaviour claim json
        claim_graph: Claim inheritance graph that shows this claim's parents

    Returns:
        The rules which apply to the behaviour claim.

    """
    aggregated_rules = []
    rules = claim["credentialSubject"].get("rules", [])
    aggregated_rules += rules
    id = claim["credentialSubject"]["id"]
    parents = nx.ancestors(claim_graph, id)
    for parent_id in parents:
        try:
            parent_claim = claim_map[parent_id]
        except KeyError:
            raise KeyError(
                f"Parent behaviour id {parent_id} of {id} doesn't exist")
        parent_rules = parent_claim["credentialSubject"].get("rules", [])
        for rule in parent_rules:
            if _get_item(aggregated_rules, "ruleName", rule["ruleName"]):
                rule["ruleName"] = f"{parent_claim['credentialSubject']['ruleName']}/{rule['ruleName']}"
            aggregated_rules.append(rule)
    unique_aggregated_rules = list(
        unique_everseen(aggregated_rules)
    )  # De-duplicate any duplicate rules
    return unique_aggregated_rules
