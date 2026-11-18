"""Tests run by Jenkins after train.py. They fail the build if the model is broken."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)
CONFIG = json.loads(Path('config.json').read_text())


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_metrics_fields():
    r = client.get('/metrics')
    assert r.status_code == 200
    m = r.json()
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in m
    assert m['student_id'] == CONFIG['student_id']
    assert 0.5 <= m['accuracy'] <= 1.0
    assert m['training_rows'] >= 100


def test_predict():
    record = {name: 0.1 for name in CONFIG['features']}
    r = client.post('/predict', json={'records': [record, record]})
    assert r.status_code == 200
    body = r.json()
    assert len(body['predictions']) == 2
    assert all(p in (0, 1) for p in body['predictions'])
