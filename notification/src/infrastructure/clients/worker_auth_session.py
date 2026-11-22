import json
import os
from pathlib import Path
import tempfile

import httpx


class WorkerAuthenticationError(RuntimeError):
    pass


class WorkerAuthSession:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        session_file: Path,
    ) -> None:
        self._client = http_client
        self._session_file = session_file
        self._refresh_token: str | None = None
        self._access_token: str | None = None

    async def _post(
        self,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        try:
            response = await self._client.post(path, **kwargs)
        except httpx.RequestError:
            raise WorkerAuthenticationError(
                "Authentication API unavailable"
            ) from None

        if not response.is_success:
            raise WorkerAuthenticationError(
                f"Authentication request failed: "
                f"{path}, HTTP {response.status_code}"
            )

        return response

    @staticmethod
    def _read_access_token(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            raise WorkerAuthenticationError(
                "Invalid authentication response"
            ) from None

        token = (
            payload.get("access_token")
            if isinstance(payload, dict)
            else None
        )

        if not isinstance(token, str) or not token.strip():
            raise WorkerAuthenticationError(
                "Authentication response missing access token"
            )

        return token

    def _cookie_headers(self) -> dict[str, str]:
        if self._refresh_token is None:
            raise WorkerAuthenticationError(
                "Worker session has not started"
            )

        return {
            "Cookie": f"refresh_token={self._refresh_token}",
        }

    def _save(self) -> None:
        self._session_file.parent.mkdir(
            parents=True,
            exist_ok=True,
            mode=0o700,
        )

        fd, temporary = tempfile.mkstemp(
            dir=self._session_file.parent,
            prefix=".worker-session-",
        )

        try:
            with os.fdopen(fd, "w") as file:
                json.dump(
                    {"refresh_token": self._refresh_token},
                    file,
                )
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary, self._session_file)

        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    async def start(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        if self._refresh_token is not None:
            raise WorkerAuthenticationError(
                "Worker session already started"
            )

        if self._session_file.exists():
            try:
                payload = json.loads(
                    self._session_file.read_text()
                )
                refresh_token = payload["refresh_token"]

                if (
                    not isinstance(refresh_token, str)
                    or not refresh_token.strip()
                    or any(
                        char in refresh_token
                        for char in "\r\n;"
                    )
                ):
                    raise ValueError("Invalid refresh token")

                self._refresh_token = refresh_token

            except (ValueError, KeyError, TypeError):
                raise WorkerAuthenticationError(
                    "Invalid worker session file"
                ) from None

            await self.refresh()
            return

        if not email or not password:
            raise WorkerAuthenticationError(
                "Worker email and password are required "
                "for first login"
            )

        response = await self._post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        self._access_token = self._read_access_token(response)
        self._refresh_token = response.cookies.get(
            "refresh_token"
        )

        if not self._refresh_token:
            raise WorkerAuthenticationError(
                "Login response missing refresh cookie"
            )

        try:
            self._save()
        except OSError:
            await self.logout()
            raise

    async def refresh(self) -> str:
        response = await self._post(
            "/api/v1/auth/refresh",
            headers=self._cookie_headers(),
        )

        self._access_token = self._read_access_token(response)
        return self._access_token

    async def logout(self) -> None:
        access_token = await self.refresh()

        headers = self._cookie_headers()
        headers["Authorization"] = f"Bearer {access_token}"

        await self._post(
            "/api/v1/auth/logout",
            headers=headers,
        )

        self._session_file.unlink(missing_ok=True)
        self._refresh_token = None
        self._access_token = None
        self._client.cookies.clear()
