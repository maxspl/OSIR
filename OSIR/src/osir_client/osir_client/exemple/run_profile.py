from osir_client.api.osir_api_client import OsirApiClient

api_url = "http://127.0.0.1:8502"

osir_client = OsirApiClient(api_url=api_url)

case = osir_client.cases.create("RUN_MODULE_CASE")

# Upload a file


handler = case.profiles.run("PROFILENAME")
