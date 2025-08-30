import os
import requests
from typing import List, Optional, Dict, Any


class OpenrouterWrapper:
    """
    Lightweight chat wrapper for the OpenRouter API.

    - Stores chat history as a list of {"role": <system|user|assistant>, "content": str}
    - Sends requests to POST https://openrouter.ai/api/v1/chat/completions
    - Returns the assistant's text (choices[0].message.content)

    Env vars (optional; constructor args take precedence):
        OPENROUTER_API_KEY
        OPENROUTER_MODEL
        OPENROUTER_HTTP_REFERER
        OPENROUTER_X_TITLE
    """
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        model: Optional[str] = None,
        user_credentials: Optional[str] = None,
        system_prompt: Optional[str] = None,
        http_referer: Optional[str] = None,
        x_title: Optional[str] = None,
        request_overrides: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Args:
            model: Model id, e.g. "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", etc.
            user_credentials: Your OpenRouter API key (Bearer).
            system_prompt: Optional system message to seed the conversation.
            http_referer: Optional attribution header (app/site URL).
            x_title: Optional attribution header (human-readable app name).
            request_overrides: Optional dict of extra OpenRouter/OpenAI-compatible params
                               (e.g., {"temperature": 0.7, "max_tokens": 2048}).
        """
        # Credentials and model: prefer constructor args, else environment
        self.api_key = user_credentials or os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set user_credentials or OPENROUTER_API_KEY.")

        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

        # Optional attribution headers
        self.http_referer = http_referer or os.getenv("OPENROUTER_HTTP_REFERER")
        self.x_title = x_title or os.getenv("OPENROUTER_X_TITLE")

        # Store model/creds/attribution back to env (as requested)
        os.environ["OPENROUTER_API_KEY"] = self.api_key
        os.environ["OPENROUTER_MODEL"] = self.model
        if self.http_referer:
            os.environ["OPENROUTER_HTTP_REFERER"] = self.http_referer
        if self.x_title:
            os.environ["OPENROUTER_X_TITLE"] = self.x_title

        # Initialize in-memory chat history (and mirror in env if system prompt provided)
        self.history: List[Dict[str, str]] = []
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

        # Allow caller to set default sampling/provider params for every request
        self.request_overrides = request_overrides or {}

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # required
            "Content-Type": "application/json",
        }
        # Optional attribution (recommended by OpenRouter)
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        if self.x_title:
            headers["X-Title"] = self.x_title
        return headers

    def _payload(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Compose a valid OpenRouter chat completion request body.
        """
        body: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        # Merge any caller-provided overrides (temperature, max_tokens, etc.)
        if self.request_overrides:
            body.update(self.request_overrides)
        return body

    def send_message(self, user_message: str) -> str:
        """
        Add a user message, call OpenRouter, append the assistant reply, and return it.
        """
        # 1) Append user message to history
        self.history.append({"role": "user", "content": user_message})

        # 2) Build request
        payload = self._payload(self.history)

        # 3) Call OpenRouter
        resp = requests.post(self.OPENROUTER_URL, headers=self._headers(), json=payload, timeout=600)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Attach response text to aid debugging
            raise RuntimeError(f"OpenRouter API error {resp.status_code}: {resp.text}") from e

        data = resp.json()

        # 4) Extract assistant content per OpenAI-compatible schema
        try:
            assistant_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected OpenRouter response format: {data}") from e

        # 5) Append assistant reply to history and return it
        self.history.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    def clear_history(self, keep_system: bool = True) -> None:
        """
        Clears chat history. If keep_system=True, preserve the first system message (if any).
        """
        if keep_system and self.history and self.history[0].get("role") == "system":
            system_msg = self.history[0]
            self.history = [system_msg]
        else:
            self.history = []

    # Optional convenience:
    def set_system_prompt(self, system_prompt: str, reset_history: bool = False) -> None:
        """
        Updates the system prompt. If reset_history is True, wipes prior messages.
        """
        if reset_history:
            self.history = [{"role": "system", "content": system_prompt}]
        else:
            # Replace existing first system or insert at the start
            if self.history and self.history[0].get("role") == "system":
                self.history[0]["content"] = system_prompt
            else:
                self.history.insert(0, {"role": "system", "content": system_prompt})


if __name__ == "__main__":
	wrapper = OpenrouterWrapper(
    model="deepseek/deepseek-chat-v3.1:free",
    user_credentials="put it here",
    system_prompt="You are a concise assistant."
)

reply = wrapper.send_message("Give me three bullet points about the Eiffel Tower.")
print(reply)
reply = wrapper.send_message("Can you give me 3 more facts?")
print(reply)

# When needed
print(wrapper.history)

#wrapper.clear_history()  # or wrapper.clear_history(keep_system=True)
