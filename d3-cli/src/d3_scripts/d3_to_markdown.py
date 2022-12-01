import pandas as pd
import json
from pathlib import Path


def _format_rule(rule, depth):
    return f'{"&emsp;" * depth}{"Disallow" if rule.get("allowed", True) == False else "Allow"} {rule["addr"]}'


def _getRules(rule: dict):
    """
    Get hierarchical child rules as a list with indentation indicating hierarchy

    Args:
        rule: The rule to extract rules from. Takes the form
        {
            allowed: boolean,
            addr: string,
            children: [array]
        }
    Returns:
        Array of rules as strings indented with depth
    """
    rulesArray = []

    def processChildRules(subRule, depth=0):
        rulesArray.append(_format_rule(subRule, depth))
        if 'children' in subRule:
            for child in subRule['children']:
                processChildRules(child, depth + 1)
        else:
            return
    processChildRules(rule)
    return rulesArray


def _retrieve_properties(dataFrame, properties):
    """
    Retrieve properties from a dictionary

    Args:
        dataFrame: The data frame to retrieve properties from
        properties: The properties to retrieve
    Returns:
        The properties in a dictionary
    """
    properties_values = {}
    for property in properties:
        property_value = dataFrame.get(
            f"credentialSubject.{property}", [None])[0]
        properties_values[property] = property_value
    return properties_values


def behaviour_to_markdown(filepath, output_path):
    """
    Convert a behaviour file to markdown representation of behaviour rules

    Args:
        filepath: Path to the behaviour file
        output_path: Path to the directory in which to write output file

    Returns:
        path to markdown file
    """
    with open(filepath) as data_file:
        claim_data = json.load(data_file)
    df = pd.json_normalize(claim_data)
    df.drop("type", axis=1, inplace=True)
    id = df["credentialSubject.id"][0]
    rules = df["credentialSubject.rules"][0]

    rulesArray = []
    for rule in rules:
        matches = rule["matches"]
        ip4RuleComponent = matches["ip4"]
        dns_dests = ip4RuleComponent.get("destinationDnsname", None)
        if dns_dests is not None:
            dns_rules = _getRules(dns_dests)
        else:
            dns_rules = []
        ip_dests = ip4RuleComponent.get("destinationIp4", None)
        if ip_dests is not None:
            ip_rules = _getRules(ip_dests)
        else:
            ip_rules = []

        if len(ip_rules) > 0 or len(dns_rules) > 0:
            rulesArray.append(f"**{rule['ruleName']}**")
            if len(dns_rules) > 0:
                rulesArray.append(f"**{'&emsp;domain name'}**")
                rulesArray += ["&emsp;&emsp;" + x for x in dns_rules]
            if len(ip_rules) > 0:
                rulesArray.append(f"**{'&emsp;ip address'}**")
                rulesArray += ["&emsp;&emsp;" + x for x in ip_rules]

    mdContent = pd.DataFrame(data=pd.Series(rulesArray).transpose(), columns=[
        "rules"]).to_markdown(index=False)
    output_file = output_path / f"{id}.md"
    print(f"Writing markdown file to {output_file}")
    with open(output_file, "w") as f:
        print(mdContent, file=f)
    return output_file


def type_to_markdown(filepath, output_path):
    """
    Convert a type file to markdown representation of type.

    Args:
        filepath: Path to the type file
        output_path: Path to the directory in which to write output file

    Returns:
        path to markdown file
    """
    with open(filepath) as data_file:
        claim_data = json.load(data_file)
    df = pd.json_normalize(claim_data)
    df.drop("type", axis=1, inplace=True)
    properties = ["id", "manufacturer", "manufacturerUri",
                  "tags", "name", "behaviour.id", "cpe", "parents", "children"]
    claim_properties = _retrieve_properties(df, properties)
    properties.remove("behaviour.id")
    id = claim_properties["id"]

    print(claim_properties)

    behaviour_file = output_file = output_path / f"{claim_properties['behaviour.id']}.md"
    with open(behaviour_file, 'r') as file:
        behaviour_markdown = file.read()

    cve_url = None
    if claim_properties["cpe"] is not None:
        cve_url = f"https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&isCpeNameSearch=true&seach_type=all&query={claim_properties['cpe']}"
        claim_properties["cpe"] = f"[{claim_properties['cpe']}]({cve_url})"

    if claim_properties["parents"] is not None:
        parents_md_content = []
        for parent in claim_properties["parents"]:
            parents_md_content.append(
                f"[{parent['id']}](/{parent['id']}.html)")
        claim_properties["parents"] = ", ".join(parents_md_content)

    if claim_properties["children"] is not None and claim_properties["children"] is not []:
        children_md_content = []
        for child in claim_properties["children"]:
            children_md_content.append(f"[{child['id']}](/{child['id']}.html)")
        claim_properties["children"] = ", ".join(children_md_content)

    rows = []
    for property in properties:
        rows.append([property, claim_properties[property]])
    mdHeader = f"""Title: {claim_properties["name"]}
date: 2022-12-01
Category: Type
Tags: {claim_properties["tags"]}
Slug: {claim_properties["id"]}

"""
    mdContent = pd.DataFrame(data=rows, columns=[
        "field", "property"]).to_markdown(index=False)
    output_file = output_path / f"{id}.md"
    print(f"Writing markdown file to {output_file}")
    with open(output_file, "w") as f:
        print(mdHeader + mdContent + "\n\n" + behaviour_markdown, file=f)

    return output_file


if __name__ == "__main__":

    output_path = Path(".")

    # file = "/home/ash/Downloads/example-build/Ekviz/Cp1-4MP/cp1-4mp.behaviour.d3.json"
    file = "/home/ash/Downloads/example-build/Amazon/Echo-dot/behaviours/echo-dot.behaviour.d3.json"
    file = "/home/ash/Downloads/example-build/Amazon/Echo/echo.behaviour.d3.json"
    behaviour_to_markdown(file, output_path)

    # filepath = "/home/ash/Downloads/example-build/Ekviz/Cp1-4MP/cp1-4mp.type.d3.json"
    # filepath = "/home/ash/Downloads/example-build/Amazon/Echo-dot/echo-dot.type.d3.json"
    filepath = "/home/ash/Downloads/example-build/Amazon/Echo/echo.type.d3.json"

    type_to_markdown(filepath, output_path)
