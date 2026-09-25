import json
import os
import threading
import urllib.error
import urllib.request

from features import Features

class JarvisCore:

    def __init__(self,hud):

        self.hud = hud
        self.f = Features(hud)
        self.request_id = 0

    def process(self,command):
        command = command.strip()
        if not command:
            return "Tell me what you need."

        self.hud.set_activity(command)
        self.request_id += 1
        request_id = self.request_id
        normalized = command.lower()

        if normalized in {"jarvis", "hey jarvis", "ok jarvis"}:
            response = "Yes, I am listening. What do you need?"
            self.hud.log(response)
            return response

        if "cpu" in normalized:
            return self.f.cpu()

        elif "ram" in normalized or "memory" in normalized:
            return self.f.ram()

        elif "disk" in normalized or "storage" in normalized:
            return self.f.disk()

        elif "youtube" in normalized:
            return self.f.youtube()

        elif "google" in normalized:
            return self.f.google()

        elif "github" in normalized:
            return self.f.github()

        elif "gmail" in normalized or "email" in normalized:
            return self.f.gmail()

        elif "time" in normalized or "date" in normalized:
            return self.f.time()

        elif "random number" in normalized:
            return self.f.random_number()

        elif "coin" in normalized:
            return self.f.coin()

        elif "password" in normalized:
            return self.f.password()

        elif "files" in normalized or "folder" in normalized:
            return self.f.list_files()

        elif "create file" in normalized:
            return self.f.create_file()

        elif "read file" in normalized:
            return self.f.read_file()

        elif "screenshot" in normalized:
            return self.f.screenshot()

        elif "system info" in normalized or "computer info" in normalized:
            return self.f.system_info()

        elif normalized.startswith("open "):
            return self.f.open_path(command[5:])

        elif normalized.startswith("wiki "):
            return self.f.wiki(command[5:])

        if not os.getenv("OPENAI_API_KEY"):
            response = "I do not have an AI provider key yet. Add OPENAI_API_KEY to enable real-time AI responses."
            self.hud.log(response)
            return response
        self.hud.ai_response.emit("JARVIS is thinking...", False)
        threading.Thread(target=self._stream_ai, args=(command, request_id), daemon=True).start()
        return None

    def _ask_ai(self, command):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        payload = json.dumps({
            "model": os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": "You are JARVIS, a concise desktop voice assistant. Never claim to have performed a device action unless the local task engine confirmed it."},
                {"role": "user", "content": command},
            ],
            "temperature": 0.3,
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as result:
                data = json.loads(result.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as error:
                details = error.read().decode("utf-8", errors="replace")
                if error.code == 401:
                    message = "AI authentication failed. Check that this is an active OpenAI API key, then restart JARVIS."
                elif error.code == 429 and "insufficient_quota" in details:
                    message = "OpenAI authenticated successfully, but this account has no API credits. Add billing or credits at platform.openai.com, then restart JARVIS."
                elif error.code == 429:
                    message = "OpenAI is rate-limiting requests. Wait a moment and try again."
                elif error.code == 404:
                    message = "The selected AI model is unavailable for this key. Set JARVIS_MODEL to a model enabled for your account."
                else:
                    message = f"The AI service returned HTTP {error.code}."
                return message
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as error:
            return f"The AI service is unavailable: {error}"

    def _stream_ai(self, command, request_id):
        api_key = os.getenv("OPENAI_API_KEY")
        payload = json.dumps({
            "model": os.getenv("JARVIS_MODEL", "gpt-4o-mini"),
            "stream": True,
            "messages": [
                {"role": "system", "content": "You are JARVIS, a concise desktop voice assistant. Never claim to have performed a device action unless the local task engine confirmed it."},
                {"role": "user", "content": command},
            ],
            "temperature": 0.3,
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        answer = ""
        try:
            with urllib.request.urlopen(request, timeout=60) as result:
                for raw_line in result:
                    line = raw_line.decode("utf-8").strip()
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    token = json.loads(data).get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if token:
                        answer += token
                        if request_id == self.request_id:
                            self.hud.ai_response.emit(answer, False)
            if request_id == self.request_id:
                self.hud.ai_response.emit(answer or "The AI returned an empty response.", True)
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")
            if error.code == 401:
                message = "AI authentication failed. Check that this is an active OpenAI API key, then restart JARVIS."
            elif error.code == 429 and "insufficient_quota" in details:
                message = "OpenAI authenticated successfully, but this account has no API credits. Add billing or credits at platform.openai.com, then restart JARVIS."
            elif error.code == 429:
                message = "OpenAI is rate-limiting requests. Wait a moment and try again."
            elif error.code == 404:
                message = "The selected AI model is unavailable for this key. Set JARVIS_MODEL to a model enabled for your account."
            else:
                message = f"The AI service returned HTTP {error.code}."
            if request_id == self.request_id:
                self.hud.ai_response.emit(message, True)
        except (urllib.error.URLError, json.JSONDecodeError, KeyError) as error:
            if request_id == self.request_id:
                self.hud.ai_response.emit(f"The AI service is unavailable: {error}", True)