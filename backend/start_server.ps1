$env:SECRET_KEY = 'test-secret-key'
$env:DATABASE_URL = 'sqlite:///./test_diag.db'
uvicorn main:app --host 127.0.0.1 --port 8000
