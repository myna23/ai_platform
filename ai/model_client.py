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
        "models":     ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
        "env_key":    "WB_AZURE_ENDPOINT",
        "package":    "azure-openai",
        "docs_url":   "https://ai.worldbank.org/",
        "mai_base":   "https://azapimdev.worldbank.org/maifactory/openai",
    },
    # ── World Bank Desktop (DesktopToken auth) — Claude via mAI Bedrock ─
    # Same DesktopToken auth as GPT, but routes to Bedrock Claude endpoint.
    "WB Desktop (Claude)": {
        "best":    "us.anthropic.claude-sonnet-4-6",
        "models":  [
            "us.anthropic.claude-sonnet-4-6",
            "us.anthropic.claude-haiku-4-5",
            "us.anthropic.claude-opus-4-5",
        ],
        "env_key":  "WB_AZURE_ENDPOINT",
        "package":  "bedrock-claude",
        "docs_url": "https://ai.worldbank.org/",
        "bedrock_base": "https://azapimdev.worldbank.org/conversationalai/bedrock/model/",
    },
    # ── World Bank Posit Connect (OAuth via CONNECT_SERVER + CONNECT_API_KEY) ─
    # Auth: Posit Connect calls /__api__/v1/oauth/integrations/credentials with
    # the mAI Factory OAuth integration GUID to get an Azure Bearer token.
    # No manual secrets needed — Posit Connect injects CONNECT_SERVER + CONNECT_API_KEY.
    "WB Posit (GPT)": {
        "best":       "gpt-5",
        "models":     ["gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini"],
        "env_key":    "WB_POSIT",
        "package":    "azure-openai",
        "mai_base":   "https://azapimdev.worldbank.org/maifactory/openai",
    },
    "WB Posit (Claude)": {
        "best":    "us.anthropic.claude-sonnet-4-6",
        "models":  [
            "us.anthropic.claude-sonnet-4-6",
            "us.anthropic.claude-haiku-4-5",
        ],
        "env_key":  "WB_POSIT",
        "package":  "bedrock-claude",
        "bedrock_base": "https://azapimdev.worldbank.org/conversationalai/bedrock/model/",
    },
    # ── World Bank mAI Factory (primary for WB deployment) ──────────────
    # Single token from mAI Factory replaces all individual provider keys.
    # Routes to GPT models through the WB internal gateway.
    # Set MAI_FACTORY_TOKEN + MAI_FACTORY_BASE_URL in .env / Posit Connect.
    "WB mAI Factory (GPT)": {
        "best":    "gpt-4o",
        "models":  ["gpt-4o", "gpt-4o-mini"],
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
    ("WB Posit (GPT)",       "gpt-4o"),
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
        self.model    = model
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
            return token_class.token_provider(env="DEV")
        except Exception as e:
            raise RuntimeError(f"DesktopToken auth failed: {e}. Ensure itsai SDK is installed and you are on a WB machine.")

    def _get_posit_oauth_token(self) -> str:
        """Get Azure AD token via Posit Connect OAuth token exchange (Python Shiny pattern)."""
        import requests as _req
        connect_server   = _os.getenv("CONNECT_SERVER", "").rstrip("/")
        connect_api_key  = _os.getenv("CONNECT_API_KEY", "")
        session_token    = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")
        oauth_guid       = "20c434c5-78f1-431f-a286-76980748bc93"

        if not connect_server or not connect_api_key or not session_token:
            missing = [v for v, k in [
                ("CONNECT_SERVER", connect_server),
                ("CONNECT_API_KEY", connect_api_key),
                ("CONNECT_CONTENT_SESSION_TOKEN", session_token),
            ] if not k]
            raise RuntimeError(f"Missing env vars for Posit OAuth: {', '.join(missing)}")

        url  = f"{connect_server}/__api__/v1/oauth/integrations/credentials"
        resp = _req.post(
            url,
            headers={
                "Authorization": f"Key {connect_api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type":        "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:posit:connect:content-session-token",
                "subject_token":     session_token,
                "audience":          oauth_guid,
            },
            timeout=30,
        )
        if not resp.ok:
            # Response body deliberately excluded — it may echo request material.
            # Only the status code is recorded (ACN-2026-31023, stories 186199/186216).
            raise RuntimeError(f"Posit OAuth token exchange failed (HTTP {resp.status_code})")
        token = resp.json().get("access_token", "")
        if not token:
            # Response content deliberately excluded (ACN-2026-31023).
            raise RuntimeError("Posit OAuth token exchange returned no access_token")
        return token

    def _get_auth_token(self) -> str:
        """Get bearer token — Posit Connect: OAuth token exchange. WB Desktop: DesktopToken."""
        if self.provider in ("WB Posit (Claude)", "WB Posit (GPT)"):
            # Try OAuth token exchange first (requires CONNECT_CONTENT_SESSION_TOKEN)
            session_token = _os.getenv("CONNECT_CONTENT_SESSION_TOKEN", "")
            if session_token:
                return self._get_posit_oauth_token()
            # Fall back to manually refreshed token
            token = _os.getenv("MAI_FACTORY_TOKEN", "")
            if token:
                return token
            raise RuntimeError(
                "No auth available on Posit Connect. Either CONNECT_CONTENT_SESSION_TOKEN "
                "must be set (automatic) or run refresh_mai_token.py on your WB desktop."
            )
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
        pinfo = PROVIDERS[self.provider]
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
            extra_headers = {"x-source-type": "interactive", "x-team-name": "posit-zambia"}
        return OpenAI(
            base_url=pinfo.get("mai_base", self.api_key),
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
        if self.model in ("gpt-5", "gpt-5-mini"):
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
        full_messages = [{"role": "system", "content": system}] + messages
        kwargs = dict(model=self.model, messages=full_messages)
        if self.model in ("gpt-5", "gpt-5-mini"):
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
        pinfo = PROVIDERS[self.provider]
        url = f"{pinfo['bedrock_base']}{self.model}/converse"
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
        pinfo = PROVIDERS[self.provider]
        url = f"{pinfo['bedrock_base']}{self.model}/converse"
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
        full_messages = [{"role": "system", "content": system}] + messages
        stream = client.chat.completions.create(
            model=self.model, max_tokens=max_tokens, stream=True,
            messages=full_messages,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
