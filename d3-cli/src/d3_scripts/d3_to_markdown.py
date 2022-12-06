import pandas as pd
import json
from datetime import date
from urllib.parse import urlparse

today = date.today()


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
            rulesArray.append(
                f"**{rule.get('ruleName', 'Missing ruleName')}**")
            if len(dns_rules) > 0:
                rulesArray.append(f"**{'&emsp;domain name'}**")
                rulesArray += ["&emsp;&emsp;" + x for x in dns_rules]
            if len(ip_rules) > 0:
                rulesArray.append(f"**{'&emsp;ip address'}**")
                rulesArray += ["&emsp;&emsp;" + x for x in ip_rules]

    mdContent = pd.DataFrame(data=pd.Series(rulesArray, dtype=str).transpose(), columns=[
        "rules"]).to_markdown(index=False)
    output_file = output_path / f"{id}.md"
    with open(output_file, "w") as f:
        print(mdContent, file=f)
    return output_file


def type_to_markdown(filepath, output_path, behaviour_path, web_address):
    """
    Convert a type file to markdown representation of type.

    Args:
        filepath: Path to the type file
        output_path: Path to the directory in which to write output file
        behaviour_path: Path to the directory in which behaviour markdown files are

    Returns:
        path to markdown file
    """
    web_address_path = urlparse(web_address).path
    if len(web_address_path) < 1 or web_address_path[-1] != "/":
        web_address_path += "/"
    with open(filepath) as data_file:
        claim_data = json.load(data_file)
    df = pd.json_normalize(claim_data)
    df.drop("type", axis=1, inplace=True)
    properties = ["id", "manufacturer", "manufacturerUri",
                  "tags", "name", "behaviour.id", "cpe", "parents", "children"]
    claim_properties = _retrieve_properties(df, properties)
    properties.remove("behaviour.id")
    properties.remove("tags")
    properties.append("github")
    id = claim_properties["id"]
    name = claim_properties["name"]
    if name is None:
        name = ""
    claim_properties["github"] = (
        "[search](https://github.com/TechWorksHub/ManySecured-D3DB/search?q=" +
        f"+id%3A+%22{id.replace(' ', '+')}%22" +
        f"name%3A+%22{name.replace(' ', '+')}%22" +
        ")"
    )

    behaviour_markdown = None
    if claim_properties['behaviour.id'] is not None:
        behaviour_file = output_file = behaviour_path / \
            f"{claim_properties['behaviour.id']}.md"
        with open(behaviour_file, 'r') as file:
            behaviour_markdown = file.read()

    cve_url = None
    if claim_properties["cpe"] is not None:
        cve_url = ("https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&isCpeNameSearch" +
                   f"=true&seach_type=all&query={claim_properties['cpe']}")
        claim_properties["cpe"] = f"[{claim_properties['cpe']}]({cve_url})"

    parents = claim_properties.get("parents", [])
    if parents is None:
        parents = []
    children = claim_properties.get("children", [])
    if children is None:
        children = []

    graph_parents = ""
    if len(parents) > 0:
        parents_md_content = []
        for parent in parents:
            parents_md_content.append(
                f"[{parent['name']}]({web_address_path}type/{parent['id']})")
        claim_properties["parents"] = ", ".join(parents_md_content)
        parent_names = [f'"{parent["name"]}"' for parent in parents]
        graph_parents = f"{'{'}{' ;'.join(parent_names)}{'}'} -> "

    graph_children = ""
    if len(children) > 0:
        children_md_content = []
        for child in children:
            children_md_content.append(
                f"[{child['name']}]({web_address_path}type/{child['id']})")
        claim_properties["children"] = ", ".join(children_md_content)
        child_names = [f'"{child["name"]}"' for child in children]
        graph_children = f"-> {'{'}{' ; '.join(child_names)}{'}'}"
    else:
        claim_properties["children"] = ""
    rows = []
    for property in properties:
        rows.append([property, claim_properties[property]])
    mdHeader = f"""Title: {claim_properties["name"]}
date: {today.strftime("%Y-%m-%d")}
Category: Type
Slug: {claim_properties["id"]}
"""
    if claim_properties["tags"] is not None:
        mdHeader += f"Tags: {claim_properties['tags']}"
    mdTypeContent = pd.DataFrame(data=rows, columns=[
        "field", "property"]).to_markdown(index=False)
    output_file = output_path / f"{id}.md"

    graph_string = f'{graph_parents} "{claim_properties["name"]}" {graph_children}'

    md_digraph = f"""
..graphviz dot
digraph G {'{'}
  graph [rankdir = TB];
  {graph_string}
{'}'}
    """

    mdContent = mdHeader + "\n## Type\n" + mdTypeContent
    if behaviour_markdown:
        mdContent += "\n\n" + md_digraph + "\n\n" + \
            "## Behaviour\n" + behaviour_markdown

    with open(output_file, "w") as f:
        print(mdContent, file=f)

    return output_file
