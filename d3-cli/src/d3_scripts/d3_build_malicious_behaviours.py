import requests
import re
from uuid import UUID
import random


def generate_seeded_uuid(seed):
    rnd = random.Random()
    rnd.seed(seed)
    uuid = UUID(int=rnd.getrandbits(128), version=4)
    return uuid.hex


def get_malicious_behaviours():
    # online active malware urls - https://urlhaus.abuse.ch/api/
    request = "https://urlhaus.abuse.ch/downloads/csv_online/"
    response = requests.get(request)
    csv_data = response.text.split("\r\n")
    headers = [header.strip("#").strip() for header in csv_data[8].split(",")]
    data = [re.findall('"([^"]*)"', row) for row in csv_data[9:-1]]
    json_data = [{headers[i]: entry for (i, entry) in enumerate(row)} for row in data]
    behaviours = [
        {
            "malicious": True,
            "ruleName": f"{row['id']}-{row['threat']}",
            "id": generate_seeded_uuid((row["id"])),
            "rules": [
                {
                    "name": f"Traffic to {row['id']}-{row['threat']}",
                    "matches": {
                        "ip4": {
                            "destinationDnsName": {
                                "addr": row["url"],
                                "allowed": False,
                            }
                        }
                    }
                },
                {
                    "name": f"Traffic from {row['id']}-{row['threat']}",
                    "matches": {
                        "ip4": {
                            "sourceDnsName": row["url"]
                        }
                    }
                }
            ]
        }
        for row in json_data]
    return behaviours
