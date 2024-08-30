import subprocess
import time

FLASK_APP_FILENAME = "app.py"
FLASK_PORT = 1337

flask_process = subprocess.Popen(["flask", "run", "--port", str(FLASK_PORT)])
time.sleep(3)

serveo_process = subprocess.Popen(["ssh", "-R", "80:127.0.0.1:1337", "serveo.net"])

try:
    input("Press Enter to stop the services and exit...")
finally:
    flask_process.terminate()
    serveo_process.terminate()
