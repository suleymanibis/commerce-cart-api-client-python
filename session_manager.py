import json

class SessionManager:
    def __init__(self):
        self.file = "sessions.json"

    def read_sessions(self) -> dict:
        try:
            with open(self.file, 'r') as f:
                sessions = json.loads(f.read())

            return sessions
        except FileNotFoundError as e:
            return {}

    def write_sessions(self, sessions:dict) -> dict:
        data = json.dumps(sessions, indent=4, ensure_ascii=False)

        with open(self.file, 'w') as f:
            f.write(data)

        return self.read_sessions()

    def clean_sessions(self):
        with open(self.file, 'w') as f:
            f.write("{}")

        return self.read_sessions()