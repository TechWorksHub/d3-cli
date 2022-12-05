from .claim_graph import build_claim_graph
import networkx as nx

always_inherited_properties = ["vulnerabilities"]


def build_type_map(type_jsons):
    type_map = {claim["credentialSubject"]
                ["id"]: claim for claim in type_jsons}
    type_graph = build_claim_graph(type_map)
    sorted_nodes = list(nx.topological_sort(type_graph))
    for type_id in sorted_nodes:
        try:
            type_instance = type_map[type_id]
        except KeyError:
            raise KeyError(
                f"Parent type with id {type_id} of {list(type_graph.predecessors(type_id))} doesn't exist"
            )
        parents = type_instance["credentialSubject"].get("parents", [])
        type_vulnerabilities = type_instance["credentialSubject"].get(
            "vulnerabilities", []
        )
        inherited_properties = {"vulnerabilities": type_vulnerabilities}
        for index, parent in enumerate(parents):
            parent_id = parent["id"]
            parent_properties = parent.get("properties") if parent.get(
                "properties") is not None else []
            properties_to_inherit = set(
                always_inherited_properties + parent_properties
            )
            parentType = type_map[parent_id]
            try:
                type_instance["credentialSubject"]["parents"][index]["name"] = parentType["credentialSubject"]["name"]
            except KeyError:
                raise Exception(f"parent {parent_id} missing name")
            for property in properties_to_inherit:
                property_to_inherit = None
                try:
                    property_to_inherit = parentType["credentialSubject"][property]
                except KeyError:
                    raise KeyError(
                        f"Attempted to inherit missing property {property} from {parent_id} in {type_id}"
                    )
                if property_to_inherit is not None:
                    if property in inherited_properties:
                        if type(inherited_properties[property]) == list:
                            inherited_properties[property] + \
                                property_to_inherit
                        else:
                            raise KeyError(
                                f"""Duplicate inherited properties in type definition {type_id},
                            attempted to inherit property `{property}` from multiple parent types"""
                            )
                    else:
                        inherited_properties[property] = property_to_inherit
        inherited_properties["vulnerabilities"] = list(
            set(inherited_properties["vulnerabilities"])
        )
        type_map[type_id]["credentialSubject"] = {
            **type_instance["credentialSubject"],
            **inherited_properties,
        }
        children = list(type_graph.successors(type_id))
        children_array = []
        for child_id in children:
            try:
                child_data = {"id": child_id, "name": type_map[child_id]["credentialSubject"]["name"]}
                children_array.append(child_data)
            except KeyError:
                raise Exception(f"child {child_id} missing name")
        type_map[type_id]["credentialSubject"]["children"] = children_array
    return type_map
