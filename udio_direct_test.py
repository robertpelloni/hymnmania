import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UdioStandalone")

COOKIE_PARTS = [
    "x-anon-id=dc6ab5c0-c052-4054-b85f-81fa0ee86386; _ga=GA1.1.1649039608.1779202454; CookieScriptConsent=%7B%22googleconsentmap%22%3A%7B%22ad_storage%22%3A%22targeting%22%2C%22analytics_storage%22%3A%22performance%22%2C%22ad_user_data%22%3A%22targeting%22%2C%22ad_personalization%22%3A%22targeting%22%2C%22functionality_storage%22%3A%22functionality%22%2C%22personalization_storage%22%3A%22functionality%22%2C%22security_storage%22%3A%22functionality%22%7D%2C%22bannershown%22%3A1%2C%22action%22%3A%22accept%22%2C%22consenttime%22%3A1722613384%2C%22categories%22%3A%22%5B%5C%22unclassified%5C%22%2C%5C%22targeting%5C%22%2C%5C%22performance%5C%22%2C%5C%22functionality%5C%22%5D%22%2C%22key%22%3A%22151bff27-dc69-4bec-8fe6-ac2b0b6252c8%22%7D; __stripe_mid=6b41f204-702d-4304-8f8d-9c7880f2199028aa2d; _tt_enable_cookie=1; _ttp=01KS0BPG9CP10VDYHB5K10N0SZ_.tt.1; intercom-device-id-b4rmcl6x=de5114c4-e581-43cf-adda-56de12525146; gbStickyBuckets__id||71e53bb3-45d0-4fd2-b8c2-eb9926b0bf7b={%22attributeName%22:%22id%22%2C%22attributeValue%22:%2271e53bb3-45d0-4fd2-b8c2-eb9926b0bf7b%22%2C%22assignments%22:{%22ab-test-announcement-or-basic-banner__0%22:%220%22}}; feather__session=e30%3D.38aV%2Bd%2BBke6Qu8ZFP1FoWGlJC1V8ZPA6xOSDnJ3BW0I; _gcl_au=1.1.1474565953.1779202463.2031232978.1779308903.1779308903; sidebar:state=true; gbStickyBuckets__id||dc6ab5c0-c052-4054-b85f-81fa0ee86386={%22attributeName%22:%22id%22%2C%22attributeValue%22:%22dc6ab5c0-c052-4054-b85f-81fa0ee86386%22%2C%22assignments%22:{%22ab-test-announcement-or-basic-banner__0%22:%220%22}}; sb-ssr-production-auth-token.1=DozMi4zNzIxMDhaIiwiY3JlYXRlZF9hdCI6IjIwMjYtMDUtMTlUMTQ6NTQ6MzIuMzc2MTA4WiIsImNyZWF0ZWRfYXQiOiIyMDI2LTA1LTE5VDE0OjU0OjMyLjM3MjE0OVoiLCJ1cGRhdGVkX2F0IjoiMjAyNi0wNS0yMVQxNToxOToxMC40MzI0MDJaIiwiZW1haWwiOiJwZWxsb25pLnJvYmVydEBnbWFpbC5jb20ifV0sImNyZWF0ZWRfYXQiOiIyMDI2LTA1LTE5VDE0OjU0OjMyLjM2NzUzM1oiLCJ1cGRhdGVkX2F0IjoiMjAyNi0wNS0yMVQxNjozNDo1MC44MTEzNDJaIiwiaXNfYW5vbnltb3VzIjpmYWxzZX19; sb-ssr-production-auth-token.0=base64-",
    "eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SWpnM01tUXdPVGsxTFdZek0yRXROR1ZtTUMxaFltVXpMVGd6TUdRMU1tWmtObVprTUNJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFlXd2lPaUpoWVd3eElpd2lZVzF5SWpwYmV5SnRaWFJvYjJRaU9pSnZZWFYwYUNJc0luUnBiV1Z6ZEdGdGNDSTZNVGMzT1RJd01qUTNNbjFkTENKaGNIQmZiV1YwWVdSaGRHRWlPbnNpY0hKdmRtbGtaWElpT2lKbmIyOW5iR1VpTENKd2NtOTJhV1JsY25NaU9sc2laMjl2WjJ4bElsMTlMQ0poZFdRaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVpXMWhhV3dpT2lKd1pXeHNiMjVwTG5KdlltVnlkRUJuYldGcGJDNWpiMjBpTENKbGVIQWlPakUzTnprek9EUTRPVEFzSW1saGRDSTZNVGMzT1RNNE1USTVNQ3dpYVhOZllXNXZibmx0YjNWeklqcG1ZV3h6WlN3aWFYTnpJam9pYUhRMHNCSE02THk5dFptMXdlR3BsYldGamMyaG1ZM0I2YjN0c2RTNXpkeEJoWW1GelpTNWpieTloZFhSb0wzWXhJaXdpY0dodmJtVWlPaUlzSUNKeWIyeGxJam9pWVhWMGFHVWRkbGpjWFJsWkNJc0luTmxjM05wYjI1ZmFXUWlPaUl3TnpNM01Ea3dZUzAzWkRSaUxUUTRZekV0T1RZeVppMHpaR1V6T0RObU5UUTBOVGtpTENKemRXSWlPaUkzTVdVMU0ySmlNeTAwTldRd0xUUm1aREl0WWpoak1pMWxZams1TWpaaU1HSm1OMklpTENKMWMyVnlYMjFsZEdGa1lYUmhJanA3SW1WdFlXbHNJam9pY0dWc2JHOXVhUzV5YjJKbGNuUkFaMjFoYVd3dVkyOXRJaXdpWlcxaGFXeGZkbVZ5YVdacFpXUWlPblJ5ZFdVc0ltWjFiR3hmYm1GdFpTSTZJbEp2WW1WeWRDQlFaV3hzYjI1cElpd2lhWE56SWpvaWFIUjBjSE02THk5aFkyTnZkVzUwY3k1bmIyOW5iR1V1WTI5dElpd2libUZ0WlNJNklsSnZZbVZ5ZENCUVpXeHNiMjVwSWl3aWJtVmxaSE5mYjI1aWIyRnlaR2x1WnlJNlptRnNjMlVzSW01bGQxOTFjMlZ5SWpwMGNuVmxMQ0p3YUc5dVpWOTJaWEpwWm1sbFpDSTZabUZzYzJVc0luQnliM1pwWkdFeVgybGtJam9pTVRBMU56WTROVFU0TURjNU5qUTBOVE15TWpjMElpd2ljM1ZpSWpvaU1UQTFOelk0TlRVNE1EYzVOalEwTlRNeU1qYzBJbjBzSW5WelpYSmZjbTlzWlNJNmJuVnNiSDAuVk42OFlxVW1LZGJsNVFrbDhlSkY4M2NubWZmNlRNclZJcF9xT0JKQ3JkeG1LWkg4Rjh2VGxneFZodjFQSXF3Z3VfNkhhZEpPb1lpMG5XdW1yUHJWVnci"
]

COOKIE = "".join(COOKIE_PARTS)

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Cookie": COOKIE,
    "Origin": "https://www.udio.com",
    "Referer": "https://www.udio.com/create",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}

data = {
    "prompt": "Hymn remake, Lo-fi, chill, instrumental",
    "lyrics_type": "generate",
    "model_type": "udio-v1.5",
    "config": {
        "mode": "regular"
    },
    "samplerOptions": {
        "seed": -1,
        "bypass_prompt_optimization": False
    },
    "is_instrumental": True
}

logger.info("Submitting direct generation request...")
url = "https://www.udio.com/api/generate-proxy"
response = requests.post(url, json=data, headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
