"""
Unified AI model client for WBG-approved AI services.
All inference is routed through the WBG mAI Factory gateway.
Exports: ModelClient, PROVIDERS, BEST_MODELS, DEFAULT_PROVIDER, DEFAULT_MODEL, fetch_available_models

Interface:
    client.ask(system, user) → str
    client.stream(system, user) → generator of str chunks
    client.stream_with_history(system, messages) → generator of str chunks

Provider libraries are imported lazily so missing packages only raise errors
when that provider is actually used.
"""

# ---------------------------------------------------------------------------
# Provider catalogue — shown in the settings UI
# ---------------------------------------------------------------------------
PROVIDERS = {
    # ── World Bank Desktop (DesktopToken auth) — GPT via mAI Factory ────
    # For local demos on a WB office machine. Authenticates via itsai SDK.
    # Store the mAI Factory endpoint in WB_AZURE_ENDPOINT in your .env file.
    "WB Desktop (GPT)": {
        "best":       "gpt-5",
        "models":     ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini", "gpt-6-luna"],
        "env_key":    "WB_AZURE_ENDPOINT",
        "package":    "azure-openai",
        "docs_url":   "https://ai.worldbank.org/",
    },
    # ── World Bank Desktop (DesktopToken auth) — Claude via mAI Bedrock ─
    # Same DesktopToken auth as GPT, but routes to Bedrock Claude endpoint.
    "WB Desktop (Claude)": {
        "best":    "us.anthropic.claude-sonnet-4-6",
        "models":  [
            "us.anthropic.claude-sonnet-4-6",
            "us.anthropic.claude-haiku-4-5",
            "us.anthropic.claude-opus-4-5",
            "us.anthropic.claude-sonnet-5-5",
            "us.anthropic.claude-haiku-5-5",
        ],
        "env_key":  "WB_AZURE_ENDPOINT",
        "package":  "bedrock-claude",
        "docs_url": "https://ai.worldbank.org/",
    },
    # ── World Bank Posit Connect (OAuth via CONNECT_SERVER + CONNECT_API_KEY) ─
    # Auth: Posit Connect calls /__api__/v1/oauth/integrations/credentials with
    # the mAI Factory OAuth integration GUID to get an Azure Bearer token.
    # No manual secrets needed — Posit Connect injects CONNECT_SERVER + CONNECT_API_KEY.
    "WB Posit (GPT)": {
        "best":       "gpt-6-luna",
        "models":     ["gpt-6-luna", "gpt-5", "gpt-5-mini"],
        "env_key":    "WB_POSIT",
        "package":    "azure-openai",
    },
    "WB Posit (Claude)": {
        "best":    "us.anthropic.claude-sonnet-4-6",
        "models":  [
            "us.anthropic.claude-sonnet-4-6",
            "us.anthropic.claude-sonnet-5-5",
            "us.anthropic.claude-haiku-5-5",
        ],
        "env_key":  "WB_POSIT",
        "package":  "bedrock-claude",
    },
    # ── World Bank mAI Factory (primary for WB deployment) ──────────────
    # Single token from mAI Factory replaces all individual provider keys.
    # Routes to GPT models through the WB internal gateway.
    # Set MAI_FACTORY_TOKEN + MAI_FACTORY_BASE_URL in .env / Posit Connect.
    "WB mAI Factory (GPT)": {
        "best":    "gpt-4o",
        "models":  ["gpt-4o", "gpt-4o-mini", "gpt-6-luna"],
        "env_key": "MAI_FACTORY_TOKEN",
        "package": "openai",
        "docs_url": "https://ai.worldbank.org/platform/documentation",
        "base_url_env": "MAI_FACTORY_BASE_URL",
    },
    # NOTE: direct external AI provider paths (OpenAI API, Google Gemini) were
    # removed under OIS security review (ACN-2026-31023). All AI inference is
    # routed exclusively through the WBG-approved mAI Factory gateway. Do not
    # reintroduce a provider that calls an external AI service directly.
}

# Default provider: desktop → posit → mAI Factory token
import os as _os
_wb_azure  = _os.getenv("WB_AZURE_ENDPOINT", "")
_on_posit  = _os.getenv("WB_POSIT", "")          # set manually in Posit Connect Vars tab
_mai_token = _os.getenv("MAI_FACTORY_TOKEN", "")
if _wb_azure:
    DEFAULT_PROVIDER = "WB Desktop (GPT)"
    DEFAULT_MODEL    = "gpt-5"
elif _on_posit:
    DEFAULT_PROVIDER = "WB Posit (GPT)"
    DEFAULT_MODEL    = "gpt-6-luna"
elif _mai_token:
    DEFAULT_PROVIDER = "WB mAI Factory (GPT)"
    DEFAULT_MODEL    = "gpt-4o"
else:
    # Default to the Posit Connect OAuth path — the approved deployment route.
    DEFAULT_PROVIDER = "WB Posit (GPT)"
    DEFAULT_MODEL    = "gpt-5"

# Best models shown in the quick selector (one per meaningful provider)
BEST_MODELS = [
    ("WB Desktop (GPT)",     "gpt-5"),
    ("WB Desktop (Claude)",  "us.anthropic.claude-sonnet-4-6"),
    ("WB Posit (GPT)",       "gpt-6-luna"),
    ("WB Posit (Claude)",    "us.anthropic.claude-sonnet-4-6"),
    ("WB mAI Factory (GPT)", "gpt-4o"),
]


def fetch_available_models(provider: str, api_key: str) -> list:
    """
    Fetch the live model list from the provider API so new models
    New models appear automatically without code changes.
    Falls back to the hardcoded list in PROVIDERS on any error.
    """
    fallback = PROVIDERS.get(provider, {}).get("models", [])
    if not api_key:
        return fallback

    pinfo    = PROVIDERS.get(provider, {})
    base_url = _os.getenv(pinfo.get("base_url_env", ""), "").strip() or None

    try:
        # ── WB mAI Factory (GPT) ─────────────────────────────────────
        if pinfo.get("package") == "openai":
            import openai
            if base_url:
                # Azure-style endpoint (mAI Factory / Azure OpenAI)
                client = openai.AzureOpenAI(
                    api_key=api_key,
                    azure_endpoint=base_url,
                    api_version="2024-12-01-preview",
                )
            else:
                client = openai.OpenAI(api_key=api_key)
            data = client.models.list()
            ids  = sorted(
                [m.id for m in data.data
                 if m.id.startswith(("gpt-4", "gpt-3.5", "gpt-5", "o1", "o3", "o4"))],
                reverse=True,
            )
            return ids[:20] if ids else fallback

    except Exception:
        pass
    return fallback


def _is_reasoning_model(name: str) -> bool:
    """
    True for models that take max_completion_tokens rather than max_tokens.

    Matched by family rather than by an exact list, so a newly offered model
    in the same family does not silently fall back to the older parameter and
    get rejected by the gateway.
    """
    n = (name or "").lower()
    return n.startswith(("gpt-5", "gpt-6", "o1", "o3", "o4"))


def _log_event(event: str, severity: str = "INFO", **fields):
    """
    Structured event log, same format the application uses elsewhere
    (ACN-2026-31023, stories 186216 / 186217).

    Server-side only. Records which authentication step ran or failed, never a
    token, key, header or service response body. Variable names are recorded
    because they are deployment configuration, not user or secret material,
    and without them an authentication failure cannot be diagnosed from logs.
    """
    parts = " ".join(f"{k}={v}" for k, v in fields.items() if v not in (None, ""))
    print(f"ZGIA_EVENT severity={severity} event={event} {parts}".rstrip(), flush=True)


def _to_openai_content(messages: list) -> list:
    """
    Translate Anthropic-style content blocks into the OpenAI chat-completions
    schema.

    Attached images are built once, in Anthropic's shape, because the Bedrock
    Claude path consumes that shape directly:

        {"type": "image", "source": {"type": "base64",
                                     "media_type": "image/png", "data": "..."}}

    The OpenAI-compatible endpoints (mAI Factory, GPT-5) instead expect:

        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}

    Without this translation the image block is not understood, the model has
    nothing to look at, and it returns an empty answer — which the caller then
    renders as a report with no content.

    Text blocks and plain-string messages pass through unchanged.
    """
    converted = []
    for msg in messages:
        content = msg.get("content")
        if not isinstance(content, list):
            converted.append(msg)
            continue
        blocks = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "image":
                source = block.get("source") or {}
                mime = source.get("media_type") or "image/jpeg"
                data = source.get("data") or ""
                blocks.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{data}"},
                })
            else:
                blocks.append(block)
        converted.append({**msg, "content": blocks})
    return converted


class ModelClient:
    """
    Provider-agnostic AI client.  Instantiate with a provider name, model name,
    and API key — then call ask() / stream() / stream_with_history() exactly as
    you would any AI client.
    """

    def __init__(self, provider: str, model: str, api_key: str):
        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider '{provider}'. Choose from: {list(PROVIDERS)}")
        self.provider = provider
        # MAI_MODEL overrides the model chosen in the interface. A gateway may
        # only serve particular models, and the names differ between
        # environments, so the deployment can pin one without a code change.
        self.model    = _os.getenv("MAI_MODEL", "").strip() or model
        self.api_key  = api_key.strip()
        # Pick up optional base URL for mAI Factory / Azure routing
        pinfo = PROVIDERS[provider]
        base_url_env = pinfo.get("base_url_env", "")
        self.base_url = _os.getenv(base_url_env, "").strip() if base_url_env else ""

    def _is_openai(self):
        return PROVIDERS[self.provider].get("package") == "openai"

    def _is_azure_openai(self):
        return PROVIDERS[self.provider].get("package") == "azure-openai"

    def _is_bedrock_claude(self):
        return PROVIDERS[self.provider].get("package") == "bedrock-claude"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def ask(self, system: str, user: str, max_tokens: int = 2048) -> str:
        """Send a single-turn message and return the full response text."""
        if self._is_openai():
            return self._openai_ask(system, user, max_tokens)
        if self._is_azure_openai():
            return self._azure_openai_ask(system, user, max_tokens)
        if self._is_bedrock_claude():
            return self._bedrock_claude_ask(system, user, max_tokens)
        raise ValueError(f"Unsupported provider: {self.provider}")

    def stream(self, system: str, user: str, max_tokens: int = 2048):
        """Stream response as text chunks (compatible with st.write_stream)."""
        if self._is_openai():
            yield from self._openai_stream(system, user, max_tokens)
        elif self._is_azure_openai():
            yield from self._azure_openai_stream(system, user, max_tokens)
        elif self._is_bedrock_claude():
            yield from self._bedrock_claude_stream(system, user, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def stream_with_history(self, system: str, messages: list, max_tokens: int = 2048):
        """Multi-turn streaming chat. messages is a list of {role, content} dicts."""
        if self._is_openai():
            yield from self._openai_stream_history(system, messages, max_tokens)
        elif self._is_azure_openai():
            yield from self._azure_openai_stream_history(system, messages, max_tokens)
        elif self._is_bedrock_claude():
            yield from self._bedrock_claude_stream_history(system, messages, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    # ------------------------------------------------------------------
    # WB Desktop (DesktopToken auth) — shared token helper
    # ------------------------------------------------------------------

    def _get_desktop_token(self) -> str:
        """Get access token via itsai DesktopToken for mAI Factory calls."""
        try:
            from itsai.platform.authentication import DesktopToken
            token_class = DesktopToken()
            _log_event("auth_ok", "INFO", method="desktop_token")
            return token_class.token_provider(env="DEV")
        except Exception as e:
            # The originating exception may carry the authorization service's
            # response body, so only its type is reported and no detail from it
            # is embedded (ACN-2026-31023, stories 186199 / 186216).
            raise RuntimeError(
                f"Desktop authentication failed ({type(e).__name__})."
            ) from None

    def _get_posit_oauth_token(self) -> str:
        """Get Azure AD token via Posit Connect OAuth token exchange (Python Shiny pattern)."""
        import requests as _req
        connect_server   = _os.getenv("CONNECT_SERVER", "").rstrip("/")
        connect_api_key  = _os.getenv("CONNECT_API_KEY", "")
        # Connect supplies the content session token either as a file or as an
        # environment variable, depending on its configuration. The file is
        # checked first; reading only the variable misses the file case.
        session_token = ""
        _token_file = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN_FILE", "")
        if _token_file and _os.path.exists(_token_file):
            try:
                with open(_token_file) as _tf:
                    session_token = _tf.read().strip()
            except Exception:
                session_token = ""
        if not session_token:
            session_token = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")
        # The OAuth integration this content is associated with. The exchange
        # is rejected if this does not match the integration attached in Posit
        # Connect, so it is configurable: set MAI_OAUTH_GUID in the content's
        # environment variables to point at a different integration without a
        # code change. The value is an integration identifier, not a secret.
        oauth_guid       = _os.getenv("MAI_OAUTH_GUID", "").strip() \
                           or "20c434c5-78f1-431f-a286-76980748bc93"

        if not connect_server or not connect_api_key or not session_token:
            # Which variables are absent is deployment configuration, not
            # something a user is told (ACN-2026-31023, story 186199) — but it
            # is recorded server-side, or the failure cannot be diagnosed.
            missing = [name for name, value in (
                ("CONNECT_SERVER", connect_server),
                ("CONNECT_API_KEY", connect_api_key),
                ("CONNECT_CONTENT_SESSION_TOKEN", session_token),
            ) if not value]
            _log_event("auth_failed", "ERROR",
                       method="posit_oauth", reason="missing_configuration",
                       missing=",".join(missing))
            raise RuntimeError("Authentication is not configured for this deployment.")

        url  = f"{connect_server}/__api__/v1/oauth/integrations/credentials"
        base = {
            "grant_type":         "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:posit:connect:content-session-token",
            "subject_token":      session_token,
        }

        # Connect already knows which integration this content is associated
        # with, so the exchange is attempted without naming one first. Sending
        # an audience Connect does not expect is rejected as a malformed
        # request (HTTP 400) rather than as a refused credential. If that
        # attempt fails and an integration identifier is configured, it is
        # tried again naming it, so either form works.
        attempts = [("without_audience", dict(base))]
        if oauth_guid:
            attempts.append(("with_audience", {**base, "audience": oauth_guid}))

        resp = None
        for label, payload in attempts:
            resp = _req.post(
                url,
                headers={
                    "Authorization": f"Key {connect_api_key}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=payload,
                timeout=30,
            )
            if resp.ok:
                break
            # Response body deliberately excluded — it may echo request material.
            # Only the status code is recorded (ACN-2026-31023, stories
            # 186199/186216). The integration identifier is recorded because a
            # mismatch with the integration attached in Connect is the usual
            # cause, and it cannot be diagnosed without knowing which one was
            # requested. It identifies an integration and is not a credential.
            _log_event("auth_failed", "ERROR", method="posit_oauth",
                       reason="exchange_rejected", attempt=label,
                       status=resp.status_code,
                       audience=oauth_guid if label == "with_audience" else None)

        if resp is None or not resp.ok:
            raise RuntimeError(
                f"Authentication with the AI service failed (HTTP {resp.status_code})."
            )
        token = resp.json().get("access_token", "")
        if not token:
            _log_event("auth_failed", "ERROR", method="posit_oauth",
                       reason="no_access_token_returned")
            # Response content deliberately excluded (ACN-2026-31023).
            raise RuntimeError("Authentication with the AI service did not return a credential.")
        _log_event("auth_ok", "INFO", method="posit_oauth")
        return token

    def _get_auth_token(self) -> str:
        """Get bearer token — Posit Connect: OAuth token exchange. WB Desktop: DesktopToken."""
        if self.provider in ("WB Posit (Claude)", "WB Posit (GPT)"):
            # OAuth token exchange is the preferred path and is tried first.
            # If it fails, a configured static token is used rather than the
            # request failing outright: attaching an integration must not
            # disable a credential that was previously working.
            session_token = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")
            if session_token:
                try:
                    return self._get_posit_oauth_token()
                except Exception:
                    if not _os.getenv("MAI_FACTORY_TOKEN", ""):
                        raise
                    _log_event("auth_fallback", "WARN", method="static_token",
                               reason="oauth_exchange_failed")
            # Fall back to manually refreshed token
            token = _os.getenv("MAI_FACTORY_TOKEN", "")
            if token:
                # Static credential path. Recorded so that which method is in
                # use can be established from logs rather than assumed.
                _log_event("auth_ok", "WARN", method="static_token")
                return token
            _log_event("auth_failed", "ERROR", method="none",
                       reason="no_authentication_method_available")
            raise RuntimeError("Authentication is not configured for this deployment.")
        return self._get_desktop_token()

    # ------------------------------------------------------------------
    # WB Desktop (GPT via mAI Factory) — DesktopToken + AzureOpenAI
    # ------------------------------------------------------------------

    def _azure_openai_client(self):
        # Migrated from AzureOpenAI (conversationalai/v2/, Azure-specific SDK
        # client) to the plain OpenAI client against the new maifactory/openai
        # endpoint, per the mAI Factory migration notice (legacy conversationalai
        # endpoints deprecated 2026-08-31, disabled 2026-09-30).
        from openai import OpenAI
        if self.provider == "WB Posit (GPT)":
            token = self._get_auth_token()
        else:
            try:
                from itsai.platform.authentication import DesktopToken
            except ImportError:
                raise ImportError("Install: pip install itsai-platform")
            token_class = DesktopToken()
            token = token_class.token_provider(env="DEV")
        extra_headers = {}
        if self.provider == "WB Posit (GPT)":
            # The gateway requires the calling team's name. It must match the
            # name registered with mAI Factory, so MAI_TEAM_NAME overrides the
            # built-in value without a code change. It is not a credential.
            team_name = _os.getenv("MAI_TEAM_NAME", "").strip() or "posit-zambia"
            extra_headers = {"x-source-type": "interactive", "x-team-name": team_name}
        # The gateway a deployment talks to must match the environment its
        # OAuth integration belongs to: a token issued for one environment is
        # rejected by another's gateway. MAI_BASE_URL overrides the built-in
        # value so the deployment can be pointed at the right gateway without
        # a code change. The URL is not a credential.
        base_url = _os.getenv("MAI_BASE_URL", "").strip().rstrip("/")
        # Trailing slash, matching the reference implementation other mAI
        # Factory apps on this platform use.
        base_url += "/"
        _log_event("ai_endpoint_selected", "INFO", base_url=base_url,
                   team=extra_headers.get("x-team-name"), model=self.model)
        return OpenAI(
            base_url=base_url,
            api_key=token,
            default_headers=extra_headers,
        )

    def _azure_openai_ask(self, system, user, max_tokens):
        client = self._azure_openai_client()
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        if _is_reasoning_model(self.model):
            kwargs["max_completion_tokens"] = max_tokens
            kwargs["reasoning_effort"] = "low"
        else:
            kwargs["max_tokens"] = max_tokens
        resp = client.chat.completions.create(**kwargs)
        if not resp.choices:
            return ""
        return resp.choices[0].message.content or ""

    def _azure_openai_stream(self, system, user, max_tokens):
        yield self._azure_openai_ask(system, user, max_tokens)

    def _azure_openai_stream_history(self, system, messages, max_tokens):
        client = self._azure_openai_client()
        full_messages = [{"role": "system", "content": system}] + _to_openai_content(messages)
        kwargs = dict(model=self.model, messages=full_messages)
        if _is_reasoning_model(self.model):
            kwargs["max_completion_tokens"] = max_tokens
            kwargs["reasoning_effort"] = "low"
        else:
            kwargs["max_tokens"] = max_tokens
        resp = client.chat.completions.create(**kwargs)
        if resp.choices:
            yield resp.choices[0].message.content or ""

    # ------------------------------------------------------------------
    # WB Desktop (Claude via mAI Factory Bedrock) — DesktopToken + requests
    # ------------------------------------------------------------------

    def _bedrock_claude_ask(self, system, user, max_tokens):
        import requests
        token = self._get_auth_token()
        bedrock_base = _os.getenv("MAI_BEDROCK_BASE_URL", "").strip().rstrip("/") + "/"
        url = f"{bedrock_base}{self.model}/converse"
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": [{"type": "text", "text": user}]}],
        }
        if system:
            payload["system"] = [{"type": "text", "text": system}]
        resp = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = (data.get("output", {}).get("message", {}).get("content") or data.get("content") or [{}])
        return content[0].get("text", "")

    def _bedrock_claude_stream(self, system, user, max_tokens):
        yield self._bedrock_claude_ask(system, user, max_tokens)

    def _bedrock_claude_stream_history(self, system, messages, max_tokens):
        import requests
        token = self._get_auth_token()
        bedrock_base = _os.getenv("MAI_BEDROCK_BASE_URL", "").strip().rstrip("/") + "/"
        url = f"{bedrock_base}{self.model}/converse"
        bedrock_messages = []
        for m in messages:
            role = m["role"]
            content = m["content"]
            if isinstance(content, str):
                bedrock_messages.append({"role": role, "content": [{"type": "text", "text": content}]})
            else:
                bedrock_messages.append({"role": role, "content": content})
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": bedrock_messages,
        }
        if system:
            payload["system"] = [{"type": "text", "text": system}]
        resp = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = (data.get("output", {}).get("message", {}).get("content") or data.get("content") or [{}])
        yield content[0].get("text", "")

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------

    def _openai_client(self):
        try:
            import openai
        except ImportError:
            raise ImportError("Install the 'openai' package: pip install openai")
        return openai.OpenAI(api_key=self.api_key)

    def _openai_ask(self, system, user, max_tokens):
        client = self._openai_client()
        resp = client.chat.completions.create(
            model=self.model, max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return resp.choices[0].message.content or ""

    def _openai_stream(self, system, user, max_tokens):
        client = self._openai_client()
        stream = client.chat.completions.create(
            model=self.model, max_tokens=max_tokens, stream=True,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _openai_stream_history(self, system, messages, max_tokens):
        client = self._openai_client()
        # Prepend system message
        full_messages = [{"role": "system", "content": system}] + _to_openai_content(messages)
        stream = client.chat.completions.create(
            model=self.model, max_tokens=max_tokens, stream=True,
            messages=full_messages,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
