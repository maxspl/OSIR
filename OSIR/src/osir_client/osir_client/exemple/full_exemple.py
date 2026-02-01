from osir_client.api.osir_api_client import OsirApiClient

api_url = "http://127.0.0.1:8502"

osir_client = OsirApiClient(api_url=api_url)

case = osir_client.cases.create("FULL_EXEMPLE_CASE")

handler = case.modules.run("bodyfile.yml")

# WAIT FOR THE PROCESSING TO BE DONE

handler.status(wait_end=True)

# Print Task

first_task = handler.task.list().select(0)

first_task.status()

first_task.log()
