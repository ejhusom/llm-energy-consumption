#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Client for LLM APIs.

This module provides a client for calling the LLM APIs, focusing on simplicity and flexibility.
It allows users to interact with the API to send requests and receive responses.

Author:
    Erik Johannes Husom

Created:
    2024-02-01

"""
import json
import requests

from config import config

class LLMAPIClient:
    """A client for interacting with LLM (Large Language Model) APIs such as Ollama.
    
    Attributes:
        api_url (str): The URL of the API endpoint.
        model_name (str): Default model name to use for requests.
        role (str): Default role to use in the message payload.
    """

    def __init__(
        self,
        llm_service,
        api_url,
        model_name,
        role="user",
    ):
        """Initialize the API client with a specific API URL, model name, and role."""

        self.llm_service = llm_service
        self.api_url = api_url
        self.model_name = model_name
        self.role = role

    def call_api(self, prompt, role=None, stream=False):
        """Send a request to the API with the given prompt, model name, and role.
        
        Args:
            prompt (str): The prompt to be sent to the API.
            model_name (str, optional): The model name to use for this request. Defaults to None.
            role (str, optional): The role to use for this message. Defaults to None.
            stream (bool, optional): Whether to stream the response. Defaults to False.
        
        Returns:
            tuple: A tuple containing the API response and extracted metadata as a dictionary.
        """

        if role is None:
            role = self.role

        data = {
            "model": self.model_name, 
            "messages": [{"role": role, "content": prompt}],
            "stream": stream
        }

        try:
            response = requests.post(self.api_url, json=data)
            response.raise_for_status()  # Raises HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

        response_json = json.loads(response.text)

        if self.llm_service == "ollama":
            data = {
                "model_name": self.model_name,
                "created_at": response_json.get("created_at"),
                "total_duration": response_json.get("total_duration"),
                "load_duration": response_json.get("load_duration"),
                "prompt_token_length": response_json.get("prompt_eval_count"),
                "prompt_duration": response_json.get("prompt_eval_duration"),
                "response_token_length": response_json.get("eval_count"),
                "response_duration": response_json.get("eval_duration"),
                "prompt": prompt,
                "response": response_json.get("message").get("content"),
            }
        elif self.llm_service in config.OPENAI_API_COMPATIBLE_SERVICES:
            # client = OpenAI(
            #     base_url=self.api_url,
            #     api_key = "sk-no-key-required"
            # )
            # completion = client.chat.completions.create(
            #     model=self.model_name,
            #     messages=[
            #         {"role": role, "content": prompt}
            #     ]
            # )
            # print(completion.choices[0].message)
            data = {
                "model_name": self.model_name,
                "created_at": response_json.get("created"),
                "total_duration": None,
                "load_duration": None,
                "prompt_token_length": response_json.get("usage").get("prompt_tokens"),
                "prompt_duration": None,
                "response_token_length": response_json.get("usage").get("completion_tokens"),
                "response_duration": None,
                "prompt": prompt,
                "response": response_json.get("choices")[0].get("message").get("content"),
            }

        return data
