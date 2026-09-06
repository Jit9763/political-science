import os
import json
import time
import requests
from dotenv import load_dotenv
from google import genai
try:
    import ollama
except ImportError:
    ollama = None

load_dotenv()

class LLMEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.preferred_engine = "gemini"
        self.ollama_url = "http://localhost:11434"

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if not self.api_key:
                        self.api_key = cfg.get("gemini_api_key", "")
                    self.preferred_engine = cfg.get("preferred_engine", "gemini")
                    self.ollama_url = cfg.get("ollama_url", "http://localhost:11434")
            except Exception as e:
                print(f"Warning loading config: {e}")

    def call_gemini(self, prompt, system_instruction=None):
        """Call Gemini API via google-genai SDK."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured! Please set it in config.json or environment.")

        client = genai.Client(api_key=self.api_key)
        max_retries = 3
        retry_delay = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config={
                        'temperature': 0.3,
                        'system_instruction': system_instruction
                    } if system_instruction else {'temperature': 0.3}
                )
                return response.text
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Gemini API attempt {attempt+1} failed with error ({e}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise e

    def call_ollama(self, prompt, system_instruction=None, model="llama3"):
        """Call Ollama local LLM."""
        if ollama is None:
            raise RuntimeError("Ollama Python package is not installed.")
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        res = ollama.generate(model=model, prompt=full_prompt)
        return res.get('response', '')

    def generate_analysis(self, prompt, system_instruction=None, engine=None):
        """Unified method to call chosen AI engine with automatic fallback."""
        target_engine = engine if engine else self.preferred_engine

        if target_engine == "gemini":
            try:
                return self.call_gemini(prompt, system_instruction)
            except Exception as e:
                print(f"Gemini API error ({e}). Trying Ollama fallback...")
                try:
                    return self.call_ollama(prompt, system_instruction)
                except Exception as oe:
                    print(f"Ollama fallback error ({oe}).")
                    raise e
        else:
            try:
                return self.call_ollama(prompt, system_instruction)
            except Exception as e:
                print(f"Ollama error ({e}). Trying Gemini API fallback...")
                return self.call_gemini(prompt, system_instruction)

if __name__ == '__main__':
    engine = LLMEngine()
    print(f"LLMEngine initialized. Preferred: {engine.preferred_engine}, API Key Configured: {bool(engine.api_key)}")
