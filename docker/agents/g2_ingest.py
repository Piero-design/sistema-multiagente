"""Integration tooling: uploads a PDF to Group 2's own RAG ingestion form (RAG_ISO27701 workflow), unchanged.
Run inside the agent-g2 container:  python3 /opt/g2_ingest.py /tmp/norma.pdf"""
import sys
import uuid
import http.client
import hashlib

form_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "g2-form-" + "G2c005db02ae9b21"))
path = sys.argv[1]
data = open(path, "rb").read()
b = "----g2ingest" + hashlib.md5(data[:1000]).hexdigest()
body = (f'--{b}\r\nContent-Disposition: form-data; name="norma"; filename="norma.pdf"\r\n'
        f'Content-Type: application/pdf\r\n\r\n').encode() + data + f"\r\n--{b}--\r\n".encode()
c = http.client.HTTPConnection("127.0.0.1", 5678, timeout=1800)
c.request("POST", f"/form/{form_id}", body, {"Content-Type": f"multipart/form-data; boundary={b}"})
r = c.getresponse()
print(r.status, r.read()[:300])
