# HSRAI REST API

The HSRAI API is a FastAPI application serving the deterministic reasoning pipeline over HTTP.

## Base URL

```
http://localhost:8000
```

Start the server:

```bash
python run_api.py
```

This runs Uvicorn on `0.0.0.0:8000`.

---

## Endpoints

### POST `/process`

Process a text input through the full HSRAI reasoning pipeline and return a signed output.

**Request Body** (`ProcessRequest`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | Yes | The input text to process |
| `request_id` | `string` | No | Optional identifier; auto-generated if omitted |

**Response Body** (`ProcessResponse`):

| Field | Type | Description |
|-------|------|-------------|
| `content` | `string` | Generated output (text, code, or action plan) |
| `format` | `string` | Output format: `"text"`, `"code"`, or `"action_plan"` |
| `trust_certificate_id` | `string \| null` | ID of the ECDSA-signed trust certificate |
| `metadata` | `object` | Processing metadata (request_id, processing_time, path_length, mu_stability) |

**Example**:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Analyze the risk of this financial transaction"}'
```

**Response**:

```json
{
  "content": "[goal]: Analyze the risk of this financi",
  "format": "text",
  "trust_certificate_id": "cert_a1b2c3d4",
  "metadata": {
    "request_id": "req_e5f6a7b8",
    "processing_time": 1750188000.123,
    "path_length": 1,
    "mu_stability": 1.0
  }
}
```

---

### GET `/health`

Check system health and status.

**Response Body** (`HealthResponse`):

| Field | Type | Description |
|-------|------|-------------|
| `status` | `string` | Always `"ok"` when the server is running |
| `version` | `string` | HSRAI version (`"1.0.0"`) |
| `test_count` | `integer` | Number of trust certificates generated since startup |

**Example**:

```bash
curl http://localhost:8000/health
```

**Response**:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "test_count": 3
}
```

---

### POST `/verify`

Verify the cryptographic validity of a trust certificate.

**Request Body** (`VerifyRequest`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | `string` | Yes | The content string that was signed |
| `certificate_id` | `string` | Yes | The certificate identifier |
| `signature` | `string` | Yes | Base64-encoded ECDSA signature |

**Response Body** (`VerifyResponse`):

| Field | Type | Description |
|-------|------|-------------|
| `valid` | `boolean` | `true` if the signature is valid, `false` otherwise |
| `message` | `string` | Human-readable verification result |

**Example**:

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "content": "[goal]: Analyze the risk",
    "certificate_id": "cert_a1b2c3d4",
    "signature": "MEUCIQD..."
  }'
```

**Response**:

```json
{
  "valid": true,
  "message": "Certificate is valid"
}
```

---

### GET `/graph/{request_id}`

Retrieve the intent graph built during a processing request.

> **Note**: This endpoint is a stub. Graph storage is not yet implemented. It returns an empty structure.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | `string` | The request ID returned by `/process` |

**Example**:

```bash
curl http://localhost:8000/graph/req_e5f6a7b8
```

**Response**:

```json
{
  "request_id": "req_e5f6a7b8",
  "nodes": [],
  "edges": [],
  "message": "Graph retrieval not yet implemented"
}
```

---

### POST `/plugins`

Register a plugin at runtime.

> **Note**: This endpoint is a stub. Plugin registration is not yet implemented.

**Example**:

```bash
curl -X POST http://localhost:8000/plugins \
  -H "Content-Type: application/json" \
  -d '{"name": "my_plugin", "type": "compression"}'
```

**Response**:

```json
{
  "status": "success",
  "message": "Plugin registration not yet implemented"
}
```

---

## Error Responses

All error responses follow this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `422` | Validation error (malformed request body) |
| `500` | Internal server error (processing failed, verification failed) |

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `422 Validation Error` | Missing required field or wrong type | Check request body schema |
| `500 Processing failed: Request timed out` | Pipeline exceeded `timeout_ms` (default 5000ms) | Increase `timeout_ms` in config or simplify input |
| `500 Processing failed: Input text cannot be empty` | Empty or whitespace-only `text` field | Provide non-empty input |
| `500 Verification failed: ...` | Invalid signature or malformed certificate data | Check certificate_id and signature |

---

## OpenAPI Documentation

FastAPI auto-generates interactive API documentation. Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
