import urllib
from typing import Any, Dict, List, Optional, Tuple

from sendhub.api_requestor import APIRequestor
from sendhub.constants import API_BASE
from sendhub.sendhub_error import InvalidRequestError
from sendhub.sendhub_object import SendHubObject

_OBJ_ID_NONE = "obj_id must not be None"


class APIResource(SendHubObject):
    """class for APIResource"""

    @staticmethod
    def get_base_url() -> str:
        """Returns the base URL for API Resource"""
        return API_BASE

    def get_object(self, obj_id: Any) -> "APIResource":
        """To get an object"""
        if obj_id is None:
            raise ValueError(_OBJ_ID_NONE)
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        response = requestor.request(meth="get", url=url)
        self.refresh_from(response)
        self._id = obj_id
        return self

    def get_list(self, **params: Any) -> List[SendHubObject]:
        """To get the list"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        response = requestor.request(meth="get", url=self.class_url(), params=params)
        return [SendHubObject.construct_from(i) for i in response]

    def create_object(self, **params: Any) -> "APIResource":
        """Creates an object for APIResource"""
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.class_url()
        response = requestor.request(meth="post", url=url, params=params)
        self.refresh_from(response)
        return self

    def update_object(self, obj_id: Any, **params: Any) -> "APIResource":
        """Updates an object"""
        if obj_id is None:
            raise ValueError(_OBJ_ID_NONE)
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        response = requestor.request(meth="put", url=url, params=params)
        self.refresh_from(response)
        self._id = obj_id
        return self

    def instance_url(self, _id: Optional[Any] = None) -> str:
        """To get the instance url"""
        _id = self.get("id") if _id is None else _id
        if not _id:
            raise InvalidRequestError(
                f"Could not determine which URL to request: {type(self).__name__} instance has invalid ID: {_id}",
                "id",
            )
        _id = APIRequestor.utf8(_id)
        base = self.class_url()
        extn = urllib.parse.quote_plus(str(_id))
        return f"{base}/{extn}"

    @classmethod
    def class_name(cls) -> str:
        """Forms URL for the class for API Resource"""
        if cls == APIResource:
            raise NotImplementedError("APIResource is an abstract class.")
        return f"{urllib.parse.quote_plus(cls.__name__.lower())}"

    def get_cached(
        self,
        obj_id: Any,
        etag: Optional[str] = None,
    ) -> Tuple[Any, Optional[str], bool]:
        """Cache-aware GET for a single resource.

        Sends ``If-None-Match: <etag>`` when *etag* is provided.  Returns a
        3-tuple ``(payload, new_etag, not_modified)``.

        * ``payload`` – parsed response body, or ``None`` when the server
          returned ``304 Not Modified``.
        * ``new_etag`` – value of the ``ETag`` response header, or ``None``
          if the server did not send one.
        * ``not_modified`` – ``True`` when the server replied with ``304``;
          the caller's previously-cached copy is still valid.
        """
        if obj_id is None:
            raise ValueError(_OBJ_ID_NONE)
        extra_headers: Dict[str, str] = {}
        if etag:
            extra_headers["If-None-Match"] = etag
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        url = self.instance_url(str(obj_id))
        payload, rcode, resp_headers = requestor.request(
            meth="get",
            url=url,
            extra_headers=extra_headers or None,
            return_metadata=True,
        )
        new_etag: Optional[str] = resp_headers.get("ETag") or resp_headers.get("etag")
        not_modified = rcode == 304
        if not not_modified and payload is not None:
            self.refresh_from(payload)
            self._id = obj_id
        return payload, new_etag, not_modified

    def get_list_cached(
        self,
        etag: Optional[str] = None,
        **params: Any,
    ) -> Tuple[Optional[List[SendHubObject]], Optional[str], bool]:
        """Cache-aware list GET.

        Sends ``If-None-Match: <etag>`` when *etag* is provided.  Returns a
        3-tuple ``(items, new_etag, not_modified)``.

        * ``items`` – list of :class:`SendHubObject` instances, or ``None``
          on ``304 Not Modified``.
        * ``new_etag`` – value of the ``ETag`` response header, or ``None``.
        * ``not_modified`` – ``True`` when the server replied with ``304``.
        """
        extra_headers: Dict[str, str] = {}
        if etag:
            extra_headers["If-None-Match"] = etag
        requestor = APIRequestor()
        requestor.api_base = self.get_base_url()
        payload, rcode, resp_headers = requestor.request(
            meth="get",
            url=self.class_url(),
            params=params or None,
            extra_headers=extra_headers or None,
            return_metadata=True,
        )
        new_etag: Optional[str] = resp_headers.get("ETag") or resp_headers.get("etag")
        not_modified = rcode == 304
        if not not_modified and payload is not None:
            return [SendHubObject.construct_from(i) for i in payload], new_etag, not_modified
        return None, new_etag, not_modified

    @classmethod
    def class_url(cls) -> str:
        """Returns URL for the class for API Resource"""
        return f"/v1/{cls.class_name()}s"
