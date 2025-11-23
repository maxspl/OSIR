from osir_client.api.osir_api_client import OSIRAPIClient

client = OSIRAPIClient("http://127.0.0.1:8502")

client._check_version()