import requests
from typing import TYPE_CHECKING, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, PrivateAttr, field_validator

from osir_lib.logger import AppLogger
from osir_client.api.osir_api_response import OsirApiResponse
from osir_lib.logger.logger import CustomLogger

logger: CustomLogger = AppLogger(__name__).get_logger()

CLIENT_VERSION = "1.0"

if TYPE_CHECKING:
    from osir_client.api.osir_api_case import OsirApiCase


class OsirApiClient(BaseModel):
    # Données publiques validées
    api_url: str

    # Attributs privés (non inclus dans model_dump)
    _cases: Optional["OsirApiCase"] = PrivateAttr(default=None)
    _session: requests.Session = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """S'exécute après la validation Pydantic"""
        # Nettoyage de l'URL
        self.api_url = self.api_url.rstrip("/")
        from osir_client.api.osir_api_case import OsirApiCase
        self._cases = OsirApiCase(api_client=self)
        # Initialisation des composants internes
        self._session = requests.Session()
        # Optionnel: Check de version automatique
        self._check_version()

    @property
    def cases(self) -> "OsirApiCase":
        """Access the cases API helper: client.cases"""
        return self._cases

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            # Utilisation de la session pour de meilleures performances
            resp = self._session.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error_handler(e)
            raise

    def get(self, endpoint: str, params: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: Optional[dict] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, json=payload)

    def is_active(self) -> bool:
        try:
            return self.get(f"/api/active")
        except:
            return False

    def _check_version(self):
        try:
            raw_response = self.get('api/version')
            api_call = OsirApiResponse(raw_response)

            # Extraction propre des versions
            v_client = CLIENT_VERSION.split('.')
            v_server = [
                str(api_call.response.get('api_major')),
                str(api_call.response.get('api_minor'))
            ]

            if v_server == v_client:
                logger.info('API Client is compatible with FastAPI server')
            else:
                logger.warning(f'Version mismatch: Client {CLIENT_VERSION} / Server {".".join(v_server)}')

        except Exception as e:
            logger.error_handler(e)
