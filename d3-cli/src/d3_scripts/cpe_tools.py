import typing
import requests
import warnings


def get_cpe(claim) -> typing.Optional[str]:
    """
    Finds the CPE in a D3 type claim

    Args:
        claim: The loaded YAML data of a D3 Claim

    Returns:
        The CPE found in the YAML file (if it exists)
    """
    return claim.get("credentialSubject", {}).get("cpe", None)


def check_cpes_resolve(cpes) -> None:
    """
    Checks if the CPE resolves to an item in the NIST national vulnerability database
    """
    for cpe in cpes:
        try:
            uri = "https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=" + cpe
            # timeout of 10 seconds is pretty slow, but so are some people's servers
            response = requests.head(uri, timeout=10)
            # throws an error if HTTP Code >= 400
            response.raise_for_status()
        except Exception as error:
            warnings.warn(f"CPE {cpe} cannot be resolved: {error}")
