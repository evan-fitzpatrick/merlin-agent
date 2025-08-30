import os
import requests
import time
from typing import List, Optional, Dict, Any


class OpenrouterWrapper:
	"""
	Lightweight chat wrapper for the OpenRouter API.

	- Stores chat history as a list of {"role": <system|user|assistant>, "content": str}
	- Sends requests to POST https://openrouter.ai/api/v1/chat/completions
	- Returns the assistant's text (choices[0].message.content)

	"""
	OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

	def __init__(
		self,
		model: Optional[str] = None,
		user_credentials: Optional[str] = None,
		system_prompt: Optional[str] = None,
		request_overrides: Optional[Dict[str, Any]] = None,
	) -> None:
		"""
		Args:
			model: Model id, e.g. "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", etc.
			user_credentials: Your OpenRouter API key (Bearer).
			system_prompt: Optional system message to seed the conversation.
			request_overrides: Optional dict of extra OpenRouter/OpenAI-compatible params
							   (e.g., {"temperature": 0.7, "max_tokens": 2048}).
		"""
		self.api_key = user_credentials
		if not self.api_key:
			raise ValueError("OpenRouter API key is required. Set user_credentials or OPENROUTER_API_KEY.")

		self.model = model
		
		self.history: List[Dict[str, str]] = []
		if system_prompt:
			self.history.append({"role": "system", "content": system_prompt})
		self.request_overrides = request_overrides or {}

		self.headers = {
			"Authorization": f"Bearer {self.api_key}",  
			"Content-Type": "application/json",
		}

	# Helper method - Convert the internal state information into the format for an API request
	def _payload(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
		body: Dict[str, Any] = {"model": self.model,"messages": messages,}
		if self.request_overrides:
			body.update(self.request_overrides)
		return body

	# Send a message to the model. Both user message and assistant response are stored to the chat history
	def send_message(self, user_message: str) -> str:
		self.history.append({"role": "user", "content": user_message})
		payload = self._payload(self.history)

		print(f'Sending message to {self.model}...')
		load_time = time.time()
		resp = requests.post(self.OPENROUTER_URL, headers=self.headers, json=payload, timeout=600)
		data = resp.json()
		print(f"Got response from Openrouter in {round((time.time() - load_time) * 100)}ms ({data['usage']})")

		assistant_text = data["choices"][0]["message"]["content"]

		self.history.append({"role": "assistant", "content": assistant_text})

		return assistant_text

	# Clear the message chat history
	def clear_history(self, keep_system: bool = True) -> None:
		if keep_system and self.history and self.history[0].get("role") == "system":
			system_msg = self.history[0]
			self.history = [system_msg]
		else:
			self.history = []


