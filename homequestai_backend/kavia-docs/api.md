# HomeQuestAI Backend API Documentation

This document provides up-to-date, detailed documentation of all API endpoints implemented in the `homequestai_backend` FastAPI, including route paths, input/output schemas, methods, tags, summaries, and authentication details.

_Last updated: Automatically generated from code in `src/api/main.py`_

---

## Overview

- **Base URL**: `/`
- **Framework**: FastAPI v0.115.x
- **Response formats**: JSON (all endpoints)
- **Authentication**: _NOTE: The current code does **not** implement real authentication or token security; all endpoints are accessible without authentication unless otherwise specified explicitly in code._

---

## 🚦 Health Endpoints

### `GET /`
**Summary:** Basic health check  
**Returns:**  
```json
{"status": "Healthy"}
```

### `GET /health/db`
**Summary:** Database health check  
**Returns:**  
- `{ "db_connection": "ok" }` if DB is reachable  
- HTTP `503` with info if not

---

## 👤 Users & Profiles

### `POST /users/register`
**Summary:** Register a new user  
**Request body:**  
```json
{
  "email": "user@example.com",
  "phone": "optional string",
  "password": "string",
  "name": "string"
}
```
**Returns (UserOut):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "optional string",
  "name": "string"
}
```
**Auth:** None (no real password hashing, open)

---

### `GET /users/{user_id}`
**Summary:** Get user details by ID  
**Returns (UserOut):** As above  
**Errors:**  
- `404` if user not found

---

### `POST /users/{user_id}/profile`
**Summary:** Create or update user profile  
**Request body:**  
```json
{
  "budget": 100000,
  "preferred_location": "Chennai",
  "filters": "filter_string"
}
```
**Returns (ProfileOut):**
```json
{
  "id": 11,
  "user_id": 1,
  "budget": 100000,
  "preferred_location": "Chennai",
  "filters": "filter_string"
}
```

---

### `GET /users/{user_id}/profile`
**Summary:** Get user profile  
**Returns (ProfileOut):** As above  
**Errors:**  
- `404` if not found

---

## 🏠 Properties

### `POST /properties/`
**Summary:** Create a property listing  
**Query parameter:** `listed_by` (int, user ID, required)  
**Request body:**  
```json
{
  "title": "string",
  "description": "string",
  "location": "string",
  "price": 20000.0,
  "property_type": "rental",
  "amenities": "comma separated"
}
```
**Returns (PropertyOut):**
```json
{
  "id": 5,
  "title": "string",
  "description": "string",
  "location": "string",
  "price": 20000.0,
  "property_type": "rental",
  "amenities": "string",
  "listed_by": 1,
  "created_at": "2024-07-01T18:00:00Z"
}
```
---

### `GET /properties/`
**Summary:** Search property listings with filters  
**Query parameters:** 
- `location: string` (optional)
- `property_type: string` (optional)
- `min_price: float` (optional)
- `max_price: float` (optional)
- `amenities: string` (optional)

**Returns:** List of `PropertyOut` objects (see above)

---

### `GET /properties/{property_id}`
**Summary:** Get details for one property  
**Returns (PropertyOut):** See above  
**Errors:**  
- `404` if not found

---

## 🖼 Media for Properties

### `GET /properties/{property_id}/media`
**Summary:** Get all media for a property  
**Returns:** List of  
```json
{
  "id": 7,
  "url": "media_url",
  "media_type": "photo|video|affiliate"
}
```

### `POST /properties/{property_id}/media`
**Summary:** Add media (image/video/link) to a property  
**Query parameters:**
- `url: string` (required)
- `media_type: string` (optional, default = photo)

**Returns:** MediaOut (see above)

---

## 📅 Viewing / Scheduling

### `POST /schedule/{user_id}/viewing`
**Summary:** Schedule a viewing for a property  
**Request body:**
```json
{
  "property_id": 5,
  "scheduled_at": "2024-07-10T10:00:00"
}
```
**Returns (ViewingOut):**
```json
{
  "id": 3,
  "user_id": 1,
  "property_id": 5,
  "scheduled_at": "2024-07-10T10:00:00",
  "created_at": "2024-07-01T18:05:00"
}
```
---

### `GET /schedule/{user_id}/viewings`
**Summary:** Get all scheduled viewings by a user  
**Returns:** List of ViewingOut (see above)

---

## 💬 Chat (WebSocket and SMS Stub)

### `WebSocket /ws/chat/{user_id}`
**Description:** In-app chat (dummy, no persistence, no SMS)
- Connect and send/receive JSON objects such as:
    ```json
    {"message": "Hello!", "to": 2}
    ```
- Server responds with:
    ```json
    {"from": user_id, "echoed_message": "Hello!"}
    ```
- **No authentication** currently

#### Usage Guide Endpoint
**GET /docs/websocket**:  
Returns a JSON object describing usage and hints for WS connections.

---

### `POST /chat/sms`
**Summary:** Send SMS (stub, not real integration)  
**Query parameters:**
- `phone_number: string` (required)
- `message: string` (required)
**Returns:**  
```json
{
  "status": "stub",
  "detail": "Would send to <phone_number>: <message>"
}
```

---

## 🤖 AI / Market Insights

### `GET /ai/recommendations`
**Summary:** Get AI-driven property recommendations (stub)  
**Query parameters:**  
- `user_id: int` (required)
**Returns:**
```json
{
  "user_id": 1,
  "recommendations": ["Property-101", "Property-202"]
}
```

### `GET /market/insights`
**Summary:** Get market insights (stub)  
**Returns:** Object with market trends and stats  
---

## 🏞 Virtual Tours

### `GET /virtualtour/{property_id}`
**Summary:** Get property tour media (only videos returned in stub)  
**Returns:** List of MediaOut

### `GET /virtualtour/{property_id}/ar`
**Summary:** Get AR preview for property  
**Returns:**  
```json
{
  "ar_preview": "https://ar-stub.homequestai.com/property/<property_id>"
}
```

---

## 📝 Reviews and Moderation

### `POST /reviews/{user_id}`
**Summary:** Create new review (defaults to unapproved)  
**Request body:**
```json
{
  "property_id": 5,
  "review_text": "Nice place",
  "rating": 4
}
```
**Returns (ReviewOut):**
```json
{
  "id": 7,
  "user_id": 1,
  "property_id": 5,
  "review_text": "Nice place",
  "rating": 4,
  "created_at": "2024-07-01T19:00:00",
  "approved": false
}
```

---

### `GET /reviews/property/{property_id}`
**Summary:** Get approved reviews for a property  
**Returns:** List of ReviewOut

### `GET /reviews/pending`
**Summary:** Get reviews awaiting moderation (admin use)  
**Returns:** List of ReviewOut (pending approval)

### `POST /reviews/{review_id}/approve`
**Summary:** Approve or reject (delete) a review  
**Query parameters:**
- `approve: bool` (default: true)
**Returns:**  
- On approve: ReviewOut (with approved=true)
- On reject: HTTP 204, review deleted

---

## ⚠️ Authentication

**IMPORTANT:**  
At present, there is _no_ authentication or authorization enforced in code for any endpoints, even those dealing with sensitive user or listing data. Integrate authentication (e.g., Firebase, OAuth) before production deployment.

---

## Data Models — Reference

### UserCreate
- email: string (EmailStr)
- phone: string (optional)
- password: string
- name: string

### UserOut
- id: int
- email: string
- phone: string (optional)
- name: string

### ProfileCreate/ProfileOut
- budget: int (optional)
- preferred_location: string (optional)
- filters: string (optional)

### PropertyCreate/PropertyOut
- title: string
- description: string (optional)
- location: string
- price: float
- property_type: string (rental/purchase)
- amenities: string (optional)
- (out): id, listed_by, created_at

### MediaOut
- id: int
- url: string
- media_type: string

### ReviewCreate/ReviewOut
- property_id: int
- review_text: string
- rating: int
- (out): id, user_id, created_at, approved

### ViewingCreate/ViewingOut
- property_id: int
- scheduled_at: datetime
- (out): id, user_id, property_id, created_at

---

## API Tag Summary

| Tag           | Description                                  |
| ------------- | ---------------------------------------------|
| Health        | API health, DB connectivity                  |
| Users         | User registration, login, profiles           |
| Properties    | Property listings CRUD                       |
| Media         | Media (photos, videos, links)                |
| Reviews       | Create, moderate property reviews            |
| Scheduling    | Schedule/track property viewings             |
| Chat          | WebSocket, Twilio SMS chat                   |
| AI            | AI recommendations, market insights          |
| VirtualTours  | 360°/AR/VR tours                             |

---

## WebSocket Example

```
ws://<host>/ws/chat/{user_id}
# send:
{"message": "Hello", "to": 2}
# response:
{"from": 1, "echoed_message": "Hello"}
```

---

# (Auto-generated documentation for current FastAPI backend.)

