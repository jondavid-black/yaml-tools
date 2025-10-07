import os
import tempfile
import shutil
import uuid
from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from git import Repo, GitCommandError
from pathlib import Path
import threading
from ruamel.yaml import YAML

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('YAML_TOOLS_SECRET_KEY', 'yamltools-secret')

# Session repo management
_session_repos = {}
_lock = threading.Lock()
def get_session_id():
	if 'session_id' not in session:
		session['session_id'] = str(uuid.uuid4())
	return session['session_id']

def get_repo_path():
	sid = get_session_id()
	with _lock:
		return _session_repos.get(sid)
def set_repo_path(path):
	sid = get_session_id()
	with _lock:
		_session_repos[sid] = path

def require_repo():
	repo_path = get_repo_path()
	if not repo_path or not os.path.exists(repo_path):
		return None, jsonify({'error': 'No repo cloned for session'}), 400
	return repo_path, None, None

# --- Repo Management ---
@app.route('/api/repo/clone', methods=['POST'])
def clone_repo():
	data = request.json
	git_url = data.get('git_url')
	if not git_url:
		return jsonify({'error': 'git_url required'}), 400
	temp_dir = tempfile.mkdtemp(prefix='yamltools_')
	try:
		Repo.clone_from(git_url, temp_dir)
		set_repo_path(temp_dir)
		return jsonify({'message': 'Cloned', 'session_id': get_session_id()})
	except Exception as e:
		shutil.rmtree(temp_dir, ignore_errors=True)
		return jsonify({'error': str(e)}), 500

@app.route('/api/repo/branches', methods=['GET'])
def list_branches():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	repo = Repo(repo_path)
	branches = [h.name for h in repo.heads]
	return jsonify({'branches': branches, 'current': repo.active_branch.name})

@app.route('/api/repo/branch/checkout', methods=['POST'])
def checkout_branch():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	data = request.json
	branch = data.get('branch')
	if not branch:
		return jsonify({'error': 'branch required'}), 400
	repo = Repo(repo_path)
	try:
		repo.git.checkout(branch)
		return jsonify({'message': f'Checked out {branch}'})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@app.route('/api/repo/branch/create', methods=['POST'])
def create_branch():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	data = request.json
	branch = data.get('branch')
	if not branch:
		return jsonify({'error': 'branch required'}), 400
	repo = Repo(repo_path)
	try:
		new_branch = repo.create_head(branch)
		new_branch.checkout()
		return jsonify({'message': f'Created and checked out {branch}'})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

# --- File System ---
def _find_yaml_files(repo_path):
	result = []
	for root, dirs, files in os.walk(repo_path):
		for f in files:
			if f.endswith(('.yasl', '.yml', '.yaml')):
				rel = os.path.relpath(os.path.join(root, f), repo_path)
				result.append(rel)
	return result

@app.route('/api/files', methods=['GET'])
def list_files():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	files = _find_yaml_files(repo_path)
	return jsonify({'files': files})
@app.route('/api/file', methods=['GET'])
def get_file():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	path = request.args.get('path')
	if not path:
		return jsonify({'error': 'path required'}), 400
	abs_path = os.path.abspath(os.path.join(repo_path, path))
	if not abs_path.startswith(repo_path):
		return jsonify({'error': 'Invalid path'}), 400
	if not os.path.exists(abs_path):
		return jsonify({'error': 'File not found'}), 404
	with open(abs_path, 'r', encoding='utf-8') as f:
		content = f.read()
	return jsonify({'content': content})

@app.route('/api/file', methods=['POST'])
def save_file():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	path = request.args.get('path')
	if not path:
		return jsonify({'error': 'path required'}), 400
	abs_path = os.path.abspath(os.path.join(repo_path, path))
	if not abs_path.startswith(repo_path):
		return jsonify({'error': 'Invalid path'}), 400
	data = request.json
	content = data.get('content')
	if content is None:
		return jsonify({'error': 'content required'}), 400
	os.makedirs(os.path.dirname(abs_path), exist_ok=True)
	with open(abs_path, 'w', encoding='utf-8') as f:
		f.write(content)
	return jsonify({'message': 'File saved'})

# --- Schema & Validation ---
@app.route('/api/yasl/validate', methods=['POST'])
def yasl_validate():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	data = request.json
	yaml_path = data.get('yaml_path')
	yasl_path = data.get('yasl_path')
	if not yaml_path or not yasl_path:
		return jsonify({'error': 'yaml_path and yasl_path required'}), 400
	abs_yaml = os.path.abspath(os.path.join(repo_path, yaml_path))
	abs_yasl = os.path.abspath(os.path.join(repo_path, yasl_path))
	if not (abs_yaml.startswith(repo_path) and abs_yasl.startswith(repo_path)):
		return jsonify({'error': 'Invalid path'}), 400
	# Dummy validation logic (replace with real YASL validation)
	try:
		yaml_loader = YAML(typ='safe')
		with open(abs_yaml, 'r', encoding='utf-8') as f:
			yaml_data = yaml_loader.load(f)
		with open(abs_yasl, 'r', encoding='utf-8') as f:
			yasl_schema = f.read()
		# TODO: Integrate real YASL validation
		errors = []
		# For now, just check YAML loads
	except Exception as e:
		return jsonify({'valid': False, 'errors': [str(e)]}), 200
	return jsonify({'valid': True, 'errors': []})

# --- Git Workflow ---
@app.route('/api/git/commit', methods=['POST'])
def git_commit():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	data = request.json
	message = data.get('message')
	if not message:
		return jsonify({'error': 'message required'}), 400
	repo = Repo(repo_path)
	repo.git.add(A=True)
	try:
		commit = repo.index.commit(message)
		return jsonify({'message': 'Committed', 'commit': commit.hexsha})
	except Exception as e:
	    return jsonify({'error': str(e)}), 500

@app.route('/api/git/push', methods=['POST'])
def git_push():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	repo = Repo(repo_path)
	try:
		origin = repo.remote(name='origin')
		push_info = origin.push()[0]
		return jsonify({'message': 'Pushed', 'summary': str(push_info.summary)})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

# --- PRs (GitHub/GitLab integration) ---
import requests

def _get_github_headers(token):
	return {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}

@app.route('/api/git/prs', methods=['GET'])
def list_prs():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	provider = request.args.get('provider', 'github')
	token = request.args.get('token')
	if not token:
		return jsonify({'error': 'token required'}), 400
	repo = Repo(repo_path)
	url = repo.remotes.origin.url
	if provider == 'github':
		# Parse owner/repo from url
		if url.startswith('git@'):
			_, path = url.split(':', 1)
		elif url.startswith('https://'):
			path = url.split('github.com/', 1)[-1]
		else:
			return jsonify({'error': 'Unsupported repo url'}), 400
		owner_repo = path.replace('.git', '').strip()
		api_url = f'https://api.github.com/repos/{owner_repo}/pulls'
		resp = requests.get(api_url, headers=_get_github_headers(token))
		if resp.status_code != 200:
			return jsonify({'error': resp.text}), resp.status_code
		return jsonify({'prs': resp.json()})
	return jsonify({'error': 'Only GitHub supported for now'}), 400

@app.route('/api/git/pr/create', methods=['POST'])
def create_pr():
	repo_path, err, code = require_repo()
	if err:
		return err, code
	data = request.json
	provider = data.get('provider', 'github')
	token = data.get('token')
	title = data.get('title')
	body = data.get('body', '')
	base = data.get('base', 'main')
	head = data.get('head')
	if not (token and title and head):
		return jsonify({'error': 'token, title, and head required'}), 400
	repo = Repo(repo_path)
	url = repo.remotes.origin.url
	if provider == 'github':
		if url.startswith('git@'):
			_, path = url.split(':', 1)
		elif url.startswith('https://'):
			path = url.split('github.com/', 1)[-1]
		else:
			return jsonify({'error': 'Unsupported repo url'}), 400
		owner_repo = path.replace('.git', '').strip()
		api_url = f'https://api.github.com/repos/{owner_repo}/pulls'
		payload = {'title': title, 'body': body, 'head': head, 'base': base}
		resp = requests.post(api_url, headers=_get_github_headers(token), json=payload)
		if resp.status_code not in (200, 201):
			return jsonify({'error': resp.text}), resp.status_code
		return jsonify({'pr': resp.json()})
	return jsonify({'error': 'Only GitHub supported for now'}), 400

# --- Main ---
if __name__ == '__main__':
	app.run(debug=True, port=5001)
