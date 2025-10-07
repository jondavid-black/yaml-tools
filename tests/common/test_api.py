import os
import sys
import pytest
import re
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/")))

from common.api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_clone_repo_missing_url(client):
    resp = client.post('/api/repo/clone', json={})
    assert resp.status_code == 400
    assert 'git_url required' in resp.get_data(as_text=True)

def test_clone_repo_invalid_url(client):
    resp = client.post('/api/repo/clone', json={'git_url': 'invalid_url'})
    assert resp.status_code in (400, 500)

def test_list_branches_no_repo(client):
    resp = client.get('/api/repo/branches')
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_checkout_branch_no_repo(client):
    resp = client.post('/api/repo/branch/checkout', json={'branch': 'main'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_create_branch_no_repo(client):
    resp = client.post('/api/repo/branch/create', json={'branch': 'feature'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_list_files_no_repo(client):
    resp = client.get('/api/files')
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_get_file_no_repo(client):
    resp = client.get('/api/file?path=foo.yaml')
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_save_file_no_repo(client):
    resp = client.post('/api/file?path=foo.yaml', json={'content': 'bar'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_yasl_validate_no_repo(client):
    resp = client.post('/api/yasl/validate', json={'yaml_path': 'foo.yaml', 'yasl_path': 'foo.yasl'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_git_commit_no_repo(client):
    resp = client.post('/api/git/commit', json={'message': 'msg'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_git_push_no_repo(client):
    resp = client.post('/api/git/push')
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_list_prs_no_repo(client):
    resp = client.get('/api/git/prs?token=abc')
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)

def test_create_pr_no_repo(client):
    resp = client.post('/api/git/pr/create', json={'token': 'abc', 'title': 't', 'head': 'h'})
    assert resp.status_code == 400
    assert 'No repo cloned' in resp.get_data(as_text=True)


def mock_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    # Create a fake .git directory to simulate a repo
    (repo_dir / ".git").mkdir()
    return str(repo_dir)

@mock.patch("common.api.get_repo_path")
def test_list_files_with_yaml_files(mock_get_repo_path, client, tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "foo.yaml").write_text("foo: bar")
    (repo_dir / "bar.yasl").write_text("schema: true")
    (repo_dir / ".git").mkdir()
    mock_get_repo_path.return_value = str(repo_dir)
    resp = client.get("/api/files")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "foo.yaml" in data["files"]
    assert "bar.yasl" in data["files"]

@mock.patch("common.api.get_repo_path")
def test_get_file_success(mock_get_repo_path, client, tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "foo.yaml").write_text("foo: bar")
    (repo_dir / ".git").mkdir()
    mock_get_repo_path.return_value = str(repo_dir)
    resp = client.get("/api/file?path=foo.yaml")
    assert resp.status_code == 200
    assert "foo: bar" in resp.get_json()["content"]

@mock.patch("common.api.get_repo_path")
def test_save_file_success(mock_get_repo_path, client, tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    mock_get_repo_path.return_value = str(repo_dir)
    resp = client.post("/api/file?path=foo.yaml", json={"content": "foo: bar"})
    assert resp.status_code == 200
    assert (repo_dir / "foo.yaml").read_text() == "foo: bar"

@mock.patch("common.api.get_repo_path")
def test_yasl_validate_success(mock_get_repo_path, client, tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "foo.yaml").write_text("foo: bar")
    (repo_dir / "foo.yasl").write_text("schema: true")
    (repo_dir / ".git").mkdir()
    mock_get_repo_path.return_value = str(repo_dir)
    resp = client.post("/api/yasl/validate", json={"yaml_path": "foo.yaml", "yasl_path": "foo.yasl"})
    assert resp.status_code == 200
    assert resp.get_json()["valid"] is True
    assert resp.get_json()["errors"] == []

# --- Success tests for repo management endpoints ---
@mock.patch("common.api.get_session_id", return_value="test-session")
@mock.patch("common.api.set_repo_path")
@mock.patch("git.Repo.clone_from")
def test_clone_repo_success(mock_clone_from, mock_set_repo_path, mock_get_session_id, client):
    git_url = "https://github.com/example/repo.git"
    resp = client.post('/api/repo/clone', json={'git_url': git_url})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Cloned"
    assert data["session_id"] == "test-session"
    mock_clone_from.assert_called_once_with(git_url, mock.ANY)
    mock_set_repo_path.assert_called_once()

@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_list_branches_success(mock_exists, mock_get_repo_path, mock_repo_cls, client):
    mock_repo = mock.Mock()
    mock_head_main = mock.Mock()
    mock_head_main.name = "main"
    mock_head_dev = mock.Mock()
    mock_head_dev.name = "dev"
    mock_repo.heads = [mock_head_main, mock_head_dev]
    mock_repo.active_branch.name = "main"
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    resp = client.get('/api/repo/branches')
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data["branches"]) == {"main", "dev"}
    assert data["current"] == "main"

@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_checkout_branch_success(mock_exists, mock_get_repo_path, mock_repo_cls, client):
    mock_repo = mock.Mock()
    mock_repo.git.checkout.return_value = None
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    resp = client.post('/api/repo/branch/checkout', json={'branch': 'dev'})
    assert resp.status_code == 200
    assert 'Checked out dev' in resp.get_json()['message']
    mock_repo.git.checkout.assert_called_once_with('dev')

@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_create_branch_success(mock_exists, mock_get_repo_path, mock_repo_cls, client):
    mock_repo = mock.Mock()
    mock_branch = mock.Mock()
    mock_repo.create_head.return_value = mock_branch
    mock_branch.checkout.return_value = None
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    resp = client.post('/api/repo/branch/create', json={'branch': 'feature'})
    assert resp.status_code == 200
    assert 'Created and checked out feature' in resp.get_json()['message']
    mock_repo.create_head.assert_called_once_with('feature')
    mock_branch.checkout.assert_called_once()

@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_git_commit_success(mock_exists, mock_get_repo_path, mock_repo_cls, client):
    mock_repo = mock.Mock()
    mock_commit = mock.Mock()
    mock_commit.hexsha = "abc123"
    mock_repo.index.commit.return_value = mock_commit
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    resp = client.post('/api/git/commit', json={'message': 'test commit'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Committed"
    assert data["commit"] == "abc123"
    mock_repo.git.add.assert_called_once_with(A=True)
    mock_repo.index.commit.assert_called_once_with('test commit')

@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_git_push_success(mock_exists, mock_get_repo_path, mock_repo_cls, client):
    mock_repo = mock.Mock()
    mock_origin = mock.Mock()
    mock_push_info = mock.Mock()
    mock_push_info.summary = "Pushed to origin/main"
    mock_origin.push.return_value = [mock_push_info]
    mock_repo.remote.return_value = mock_origin
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    resp = client.post('/api/git/push')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Pushed"
    assert data["summary"] == "Pushed to origin/main"
    mock_repo.remote.assert_called_once_with(name='origin')
    mock_origin.push.assert_called_once()

@mock.patch("common.api.requests.get")
@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_list_prs_success(mock_exists, mock_get_repo_path, mock_repo_cls, mock_requests_get, client):
    mock_repo = mock.Mock()
    mock_repo.remotes.origin.url = "https://github.com/example/repo.git"
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "title": "Test PR"}]
    mock_requests_get.return_value = mock_response
    resp = client.get('/api/git/prs?token=abc')
    assert resp.status_code == 200
    data = resp.get_json()
    assert "prs" in data
    assert data["prs"][0]["title"] == "Test PR"
    mock_requests_get.assert_called_once()

@mock.patch("common.api.requests.post")
@mock.patch("common.api.Repo")
@mock.patch("common.api.get_repo_path")
@mock.patch("os.path.exists", return_value=True)
def test_create_pr_success(mock_exists, mock_get_repo_path, mock_repo_cls, mock_requests_post, client):
    mock_repo = mock.Mock()
    mock_repo.remotes.origin.url = "https://github.com/example/repo.git"
    mock_repo_cls.return_value = mock_repo
    mock_get_repo_path.return_value = "/fake/repo"
    mock_response = mock.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 1, "title": "Test PR"}
    mock_requests_post.return_value = mock_response
    payload = {
        "provider": "github",
        "token": "abc",
        "title": "Test PR",
        "head": "feature-branch",
        "base": "main",
        "body": "PR body"
    }
    resp = client.post('/api/git/pr/create', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "pr" in data
    assert data["pr"]["title"] == "Test PR"
    mock_requests_post.assert_called_once()

@mock.patch("common.api.yaml_tools_version", return_value="0.3.3")
def test_version_api(mock_version, client):
    resp = client.get('/api/version')
    assert resp.status_code == 200
    data = resp.get_json()
    # Check for semantic versioning: major.minor.patch
    assert re.match(r"^\d+\.\d+\.\d+$", data["version"])
    mock_version.assert_called_once()
