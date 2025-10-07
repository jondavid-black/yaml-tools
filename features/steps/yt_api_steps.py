import subprocess
import time
import re
import socket
from behave import given, when, then

server_process = None

def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        try:
            sock.connect((host, port))
            return True
        except Exception:
            return False

@given('the YAML-TOOLS API server is running using the "yt-serve" command')
def step_start_server(context):
    global server_process
    context.server_url = "http://localhost:5000"
    if not is_port_open("localhost", 5000):
        server_process = subprocess.Popen(["uv", "run", "yt-serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the server to start
        time.sleep(2)

@when('I run "curl http://localhost:5000/api/version"')
def step_curl_version(context):
    result = subprocess.run(["curl", f"{context.server_url}/api/version"], capture_output=True, text=True)
    context.curl_output = result.stdout

@then('the response should contain a "version" field matching the pattern "\\d+\\.\\d+\\.\\d+"')
def step_check_version_field(context):
    import json
    data = json.loads(context.curl_output)
    assert "version" in data
    assert re.match(r"^\d+\.\d+\.\d+$", data["version"])

# Optionally, stop the server after all scenarios

def after_all(context):
    global server_process
    if server_process:
        server_process.terminate()
        server_process.wait()
