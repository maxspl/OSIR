from osir_client.api.osir_api_client import OsirApiClient

# L'instanciation valide l'URL
osir_cli = OsirApiClient(api_url="http://127.0.0.1:8502")

osir_cli.cases.get("test_1").modules.run("bodyfile.yml").status(wait_end=True)

# # L'accès aux cases reste identique
# print(client.osir_case.list().info())
# client.osir_case.get(name="test_1")
# # client = OsirApiClient("")

# client.osir_case.create("test_2").apply_module('evtx')
