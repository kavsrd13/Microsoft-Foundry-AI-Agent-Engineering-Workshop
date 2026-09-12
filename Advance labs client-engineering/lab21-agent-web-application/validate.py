"""Offline smoke tests use mocked Entra keys and mocked Azure services."""
import sys
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import os
import time
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
sys.path.insert(0, str(Path(__file__).parent / "src"))
import app as demo
from fastapi.testclient import TestClient
client = TestClient(demo.app)
os.environ['ENTRA_TENANT_ID'] = '00000000-0000-0000-0000-000000000010'
os.environ['ENTRA_API_CLIENT_ID'] = '00000000-0000-0000-0000-000000000020'
# Sign local JWTs and mock only key discovery; jwt.decode still verifies signatures/claims.
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
claims = {'oid':'00000000-0000-0000-0000-000000000001',
          'tid':os.environ['ENTRA_TENANT_ID'], 'aud':os.environ['ENTRA_API_CLIENT_ID'],
          'iss':f"https://login.microsoftonline.com/{os.environ['ENTRA_TENANT_ID']}/v2.0",
          'iat':int(time.time()), 'exp':int(time.time())+300, 'scp':'access_as_user'}
with patch.object(demo.jwt.PyJWKClient, 'get_signing_key_from_jwt', return_value=SimpleNamespace(key=key.public_key())):
    for changes, expected in [({'aud':'wrong'},401), ({'iss':'https://wrong.example'},401), ({'exp':1},401), ({'scp':'other'},401),
                              ({'tid':'wrong'},401), ({'groups':['bad-guid']},401),
                              ({'_claim_names':{'groups':'src1'}},403)]:
        token = jwt.encode(claims | changes, key, algorithm='RS256')
        result = client.post('/chat', headers={'Authorization':f'Bearer {token}'},json={'question':'hello'})
        assert result.status_code == expected, (changes, result.text)
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    forged = jwt.encode(claims, wrong_key, algorithm='RS256')
    assert client.post('/chat',headers={'Authorization':f'Bearer {forged}'},json={'question':'hello'}).status_code == 401
    token = jwt.encode(claims, key, algorithm='RS256')
    with patch.object(demo,'retrieve',return_value=[]), patch.object(demo,'answer',return_value=iter(['No evidence'])):
        assert client.post('/chat',headers={'Authorization':f'Bearer {token}'},json={'question':'hello'}).status_code == 200
assert client.post("/chat", json={"question":"hello"}).status_code == 401
assert client.post("/chat", headers={"X-MS-CLIENT-PRINCIPAL":"forged"}, json={"question":"hello"}).status_code == 401
user={"oid":"00000000-0000-0000-0000-000000000001","groups":[]}
assert "allowed_group_ids" not in demo.permission_filter(user)
assert user["oid"] in demo.permission_filter(user)
other={"oid":"00000000-0000-0000-0000-000000000002","groups":[]}
assert other["oid"] not in demo.permission_filter(user)
demo.app.dependency_overrides[demo.current_user] = lambda:user
with patch.object(demo, "retrieve", return_value=[{"id":"public-1","content":"test"}]) as search, patch.object(demo,"answer", return_value=iter(["Hello", " world"])):
    response=client.post("/chat",json={"question":"hello"})
    assert response.status_code == 200 and '"done": true' in response.text
    assert '"delta": "Hello"' in response.text
    assert search.call_args.args[1] == user
demo.app.dependency_overrides.clear()
print("PASS: signed JWT claim rejection and valid JWT; missing/forged auth denied; ACL construction; authenticated SSE with mocked retrieval/model. No live Azure proof.")
