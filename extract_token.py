import base64
import json
import os

cookie0 = "eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SWpnM01tUXdPVGsxTFdZek0yRXROR1ZtTUMxaFltVXpMVGd6TUdRMU1tWmtObVprTUNJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFlXd2lPaUpoWVd3eElpd2lZVzF5SWpwYmV5SnRaWFJvYjJRaU9pSnZZWFYwYUNJc0luUnBiV1Z6ZEdGdGNDSTZNVGMzT1RJd01qUTNNbjFkTENKaGNIQmZiV1YwWVdSaGRHRWlPbnNpY0hKdmRtbGtaWElpT2lKbmIyOW5iR1VpTENKd2NtOTJhV1JsY25NaU9sc2laMjl2WjJ4bElsMTlMQ0poZFdRaU9pSmhkWFJvWlc1MGFXTmhkR1ZrSWl3aVpXMWhhV3dpT2lKd1pXeHNiMjVwTG5KdlltVnlkRUJuYldGcGJDNWpiMjBpTENKbGVIQWlPakUzTnprek56UTBNVFVzSW1saGRDSTZNVGMzT1RNM01EZ3hOU3dpYVhOZllXNXZibmx0YjNWeklqcG1ZV3h6WlN3aWFYTnpJam9pYUhSMGNITTZMeTl0Wm0xd2VHcGxiV0ZqYzJobVkzQjZiM05zZFM1emRYQmhZbUZ6WlM1amJ5OWhkWFJvTDNZeElpd2ljR2h2Ym1VaU9pSWlMQ0p5YjJ4bElqb2lZWFYwYUdWdWRHbGpZWFJsWkNJc0luTmxjM05wYjI1ZmFXUWlPaUpqWXpBMlpqWXpZeTB6TmpOa0xUUmlZamd0WVRNNVpTMDJOek0yWlRjMk1EZzJZMkVpTENKemRXSWlPaUkzTVdVMU0ySmlNeTAwTldRd0xUUm1aREl0WWpoak1pMWxZams1TWpaaU1HSm1OMklpTENKMWMyVnlYMjFsZEdGa1lYUmhJanA3SW1WdFlXbHNJam9pY0dWc2JHOXVhUzV5YjJKbGNuUkFaMjFoYVd3dVkyOXRJaXdpWlcxaGFXeGZkbVZ5YVdacFpXUWlPblJ5ZFdVc0ltWjFiR3hmYm1GdFpTSTZJbEp2WW1WeWRDQlFaV3hzYjI1cElpd2lhWE56SWpvaWFIUjBjSE02THk5aFkyTnZkVzUwY3k1bmIyOW5iR1V1WTI5dElpd2libUZ0WlNJNklsSnZZbVZ5ZENCUVpXeHNiMjVwSWl3aWJtVmxaSE5mYjI1aWIyRnlaR2x1WnlJNlptRnNjMlVzSW01bGQxOTFjMlZ5SWpwMGNuVmxMQ0p3YUc5dVpWOTJaWEpwWm1sbFpDSTZabUZzYzJVc0luQnliM1pwWkdWeVgybGtJam9pTVRBMU56WTROVFU0TURjNU5qUTBOVE15TWpjMElpd2ljM1ZpSWpvaU1UQTFOelk0TlRVNE1EYzVOalEwTlRNeU1qYzBJbjBzSW5WelpYSmZjbTlzWlNJNmJuVnNiSDAudGpEWVB2Uzh1VWFMc3Njb0hja0NnQy14dHc3bFRqQkxQaUU3LWNwZGc3NXpOS2hMUEV1ODh3NzFKVWtXcFpfdDJoSmk0bHJMQ3ZFOHdyRFBsalBfZWciLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwiZXhwaXJlc19pbiI6MzYwMCwiZXhwaXJlc19hdCI6MTc3OTM3NDQxNSwicmVmcmVzaF90b2tlbiI6InE0cmR0bzd1cW1ibyIsInVzZXIiOnsiaWQiOiI3MWU1M2JiMy00NWQwLTRmZDItYjhjMi1lYjk5MjZiMGJmN2IiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJlbWFpbCI6InBlbGxvbmkucm9iZXJ0QGdtYWlsLmNvbSIsImVtYWlsX2NvbmZpcm1lZF9hdCI6IjIwMjYtMDUtMTlUMTQ6NTQ6MzIuMzc2MDMyWiIsInBob25lIjoiIiwiY29uZmlybWVkX2F0IjoiMjAyNi0wNS0xOVQxNDo1NDozMi4zNzYwMzJaIiwibGFzdF9zaWduX2luX2F0IjoiMjAyNi0wNS0xOVQxNDo1NDozMi40Njk3MjVaIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ29vZ2xlIiwicHJvdmlkZXJzIjpbImdvb2dsZSJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6InBlbGxvbmkucm9iZXJ0QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJmdWxsX25hbWUiOiJSb2JlcnQgUGVsbG9uaSIsImlzcyI6Imh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbSIsIm5hbWUiOiJSb2JlcnQgUGVsbG9uaSIsIm5lZWRzX29uYm9hcmRpbmciOmZhbHNlLCJuZXdfdXNlciI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJwcm92aWRlcl9pZCI6IjEwNTc2ODU1ODA3OTY0NDUzMjI3NCIsInN1YiI6IjEwNTc2ODU1ODA3OTY0NDUzMjI3NCJ9LCJpZGVudGl0aWVzIjpbeyJpZGVudGl0eV9pZCI6IjZjNWE1ODc5LTFmNTItNDc0MS05MWM1LTQxN2Q1ZTlmZjRiZiIsImlkIjoiMTA1NzY4NTU4MDc5NjQ0NTMyMjc0IiwidXNlcl9pZCI6IjcxZTUzYmIzLTQ1ZDAtNGZkMi1iOGMyLWViOTkyNmIwYmY3YiIsImlkZW50aXR5X2RhdGEiOnsiZW1haWwiOiJwZWxsb25pLnJvYmVydEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZnVsbF9uYW1lIjoiUm9iZXJ0IFBlbGxvbmkiLCJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYW1lIjoiUm9iZXJ0IFBlbGxvbmkiLCJuZWVkc19vbmJvYXJkaW5nIjp0cnVlLCJuZXdfdXNlciI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJwcm92aWRlcl9pZCI6IjEwNTc2ODU1ODA3OTY0NDUzMjI3NCIsInN1YiI6IjEwNTc2ODU1ODA3OTY0NDUzMjI3NCJ9LCJwcm92aWRlciI6Imdvb"
cookie1 = "2dsZSIsImxhc3Rfc2lnbl9pbl9hdCI6IjIwMjYtMDUtMTlUMTQ6NTQ6MzIuMzcyMTA4WiIsImNyZWF0ZWRfYXQiOiIyMDI2LTA1LTE5VDE0OjU0OjMyLjM3MjE0OVoiLCJ1cGRhdGVkX2F0IjoiMjAyNi0wNS0xOVQxNDo1NDozMi4zNzIxNDlaIiwiZW1haWwiOiJwZWxsb25pLnJvYmVydEBnbWFpbC5jb20ifV0sImNyZWF0ZWRfYXQiOiIyMDI2LTA1LTE5VDE0OjU0OjMyLjM2NzUzM1oiLCJ1cGRhdGVkX2F0IjoiMjAyNi0wNS0yMVQxMzo0MDoxMy44MjQ2NDNaIiwiaXNfYW5vbnltb3VzIjpmYWxzZX19"

b64_str = cookie0 + cookie1
# Fix padding
b64_str += "=" * ((4 - len(b64_str) % 4) % 4)

try:
    decoded_str = base64.urlsafe_b64decode(b64_str).decode('utf-8')
    data = json.loads(decoded_str)
    token = data.get("access_token")
    if token:
        env_file = "hymn_remaker/.env"
        if not os.path.exists(env_file):
            if os.path.exists("hymn_remaker/.env.example"):
                with open("hymn_remaker/.env.example", "r") as f:
                    content = f.read()
            else:
                content = "UDIO_OAUTH_TOKEN=\n"
        else:
            with open(env_file, "r") as f:
                content = f.read()
                
        if "UDIO_OAUTH_TOKEN" in content:
            # Replace existing or empty token
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("UDIO_OAUTH_TOKEN="):
                    new_lines.append(f"UDIO_OAUTH_TOKEN={token}")
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content += f"\nUDIO_OAUTH_TOKEN={token}\n"
            
        with open(env_file, "w") as f:
            f.write(content)
            
        print(f"Successfully extracted combined token and saved to {env_file}")
    else:
        print("Could not find access_token in decoded JSON.")
        
except Exception as e:
    print(f"Error decoding: {e}")
