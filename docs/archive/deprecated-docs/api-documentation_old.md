# API Documentation

## Overview

This document provides details about the APIs available in the Alfred platform, including endpoints, request/response formats, and usage examples.

---

## Endpoints

### 1. Credit Allocation

**POST /api/v1/credits/allocate**

- **Description:** Allocates credits to a user or team.
- **Request Body:**
  ```json
  {
    "entity_id": "user_123",
    "amount": 1000,
    "level": "team"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Credits allocated successfully."
  }
  ```

### 2. Peer-to-Peer Transfer

**POST /api/v1/credits/transfer**

- **Description:** Transfers credits between users.
- **Request Body:**
  ```json
  {
    "from_user_id": "user_123",
    "to_user_id": "user_456",
    "amount": 500
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "message": "Transfer completed."
  }
  ```

---

## Usage Examples

### Allocating Credits

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "user_123", "amount": 1000, "level": "team"}' \
  https://alfred.ai/api/v1/credits/allocate
```

### Transferring Credits

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"from_user_id": "user_123", "to_user_id": "user_456", "amount": 500}' \
  https://alfred.ai/api/v1/credits/transfer
```
