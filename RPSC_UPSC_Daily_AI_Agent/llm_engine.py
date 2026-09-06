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
        self.is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        self.ollama_url = "http://localhost:11434"
        self.preferred_engine = "gemini" if self.is_github_actions else "ollama"

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if not self.api_key:
                        self.api_key = cfg.get("gemini_api_key", "")
                    if not self.is_github_actions and "preferred_engine" in cfg:
                        self.preferred_engine = cfg.get("preferred_engine", "ollama")
                    self.ollama_url = cfg.get("ollama_url", "http://localhost:11434")
            except Exception as e:
                print(f"Warning loading config: {e}")

    def call_gemini(self, prompt, system_instruction=None):
        """Call Gemini API via google-genai SDK with automatic retry & clear quota messaging."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured! Please set it in config.json or environment.")

        client = genai.Client(api_key=self.api_key)
        model = 'gemini-3.6-flash'
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        'temperature': 0.3,
                        'system_instruction': system_instruction
                    } if system_instruction else {'temperature': 0.3}
                )
                return response.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    if attempt < max_retries - 1:
                        print(f"Gemini API rate limit on {model} (429 RateLimit). Waiting 10s before retry (Attempt {attempt+1}/{max_retries})...")
                        time.sleep(10)
                    else:
                        print("⚠️ Gemini API Free Tier Daily Quota (20 requests/day) reached for today due to multiple test runs. Quota resets daily at midnight.")
                        raise RuntimeError("Gemini API daily free-tier quota reached (20 requests/day). It will automatically reset tomorrow for daily runs.") from e
                elif "503" in err_str or "UNAVAILABLE" in err_str:
                    if attempt < max_retries - 1:
                        print(f"Gemini API 503 server demand spike on {model}. Retrying in 5s (Attempt {attempt+1}/{max_retries})...")
                        time.sleep(5)
                    else:
                        raise e
                else:
                    if attempt < max_retries - 1:
                        print(f"Gemini API error ({e}). Retrying in 3s...")
                        time.sleep(3)
                    else:
                        raise e

    def call_ollama(self, prompt, system_instruction=None, model="llama3"):
        """Call Ollama local LLM with forced JSON formatting and extended context window."""
        if ollama is None:
            raise RuntimeError("Ollama Python package is not installed.")
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        print(f"🦙 Generating analysis via local Ollama ({model})... Please wait...")
        res = ollama.generate(
            model=model,
            prompt=full_prompt,
            format="json",
            options={"num_ctx": 16384, "temperature": 0.3}
        )
        return res.get('response', '')

    def generate_analysis(self, prompt, system_instruction=None, engine=None):
        """Unified method to call chosen AI engine with automatic fallback."""
        target_engine = engine if engine else self.preferred_engine

        # On Cloud GitHub Actions VM, force Gemini API
        if self.is_github_actions:
            print("☁️ [Cloud Execution Mode: GitHub Actions VM] Using Gemini 2.5 Flash API...")
            return self.call_gemini(prompt, system_instruction)

        if target_engine == "ollama":
            print("🦙 [Local Mode] Attempting local Ollama (llama3) LLM execution...")
            try:
                result = self.call_ollama(prompt, system_instruction)
                print("✅ [Local Mode] Local Ollama execution finished successfully!")
                return result
            except Exception as e:
                print(f"⚠️ Ollama error ({e}). Falling back to Gemini API...")
                return self.call_gemini(prompt, system_instruction)
        else:
            print("✨ [Local Mode] Using Gemini API...")
            try:
                return self.call_gemini(prompt, system_instruction)
            except Exception as e:
                print(f"⚠️ Gemini API error ({e}). Trying local Ollama fallback...")
                return self.call_ollama(prompt, system_instruction)

if __name__ == '__main__':
    engine = LLMEngine()
    print(f"LLMEngine initialized. Preferred: {engine.preferred_engine}, API Key Configured: {bool(engine.api_key)}")
