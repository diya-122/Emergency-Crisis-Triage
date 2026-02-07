# API Usage Guide

## Emergency Crisis Triage System - API Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently no authentication required for development. For production, implement JWT-based authentication.

## Endpoints

### 1. Process Emergency Message

**POST** `/triage`

Process an unstructured emergency message and perform complete triage.

**Request Body:**
```json
{
  "message": "Help! Building collapse at 123 Main St. Multiple people trapped.",
  "source": "sms",
  "phone_number": "+1-555-0001",
  "timestamp": "2026-02-07T10:30:00Z",
  "metadata": {}
}
```

**Response:**
```json
{
  "request_id": "uuid-here",
  "status": "processed",
  "extracted_info": {
    "needs": [
      {
        "need_type": "rescue",
        "quantity": null,
        "description": "Building collapse requires rescue team",
        "confidence": 0.95
      }
    ],
    "location": {
      "raw_text": "123 Main St",
      "address": "123 Main Street, City, State",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "confidence": 0.85,
      "is_geocoded": true
    },
    "people_affected": null,
    "vulnerable_populations": [],
    "urgency_factors": {
      "medical_risk_score": 0.8,
      "medical_risk_explanation": "Building collapse suggests potential injuries",
      "vulnerable_pop_score": 0.0,
      "vulnerable_pop_explanation": "No specific vulnerable populations mentioned",
      "time_sensitivity_score": 0.9,
      "time_sensitivity_explanation": "Urgent language and trapped people indicate immediate danger",
      "message_confidence_score": 0.85,
      "message_confidence_explanation": "Message is clear and specific with location",
      "severity_score": 0.95,
      "severity_explanation": "Building collapse is inherently high severity"
    },
    "urgency_level": "critical",
    "urgency_score": 0.83,
    "overall_explanation": "This is a CRITICAL situation due to structural collapse with people trapped...",
    "extraction_confidence": 0.85
  },
  "matched_resources": [
    {
      "resource_id": "rescue-001",
      "resource_name": "Fire Department Rescue Squad Alpha",
      "resource_type": "rescue_team",
      "match_score": 0.92,
      "distance_km": 2.5,
      "estimated_arrival_minutes": 18,
      "overall_explanation": "This is an excellent match...",
      "trade_offs": [],
      "confidence_level": 0.88
    }
  ],
  "processing_time_seconds": 3.45,
  "requires_confirmation": true,
  "warnings": [
    "CRITICAL: Life-threatening situation. Immediate response required."
  ]
}
```

### 2. Confirm Dispatch

**POST** `/confirm`

Confirm dispatcher decision and dispatch resource.

**Request Body:**
```json
{
  "request_id": "uuid-here",
  "confirmed": true,
  "selected_resource_id": "rescue-001",
  "dispatcher_notes": "Confirmed. Rescue squad dispatched.",
  "dispatcher_id": "dispatcher-001",
  "override_reason": null
}
```

**Response:**
```json
{
  "status": "confirmed",
  "request_id": "uuid-here",
  "dispatched": true
}
```

### 3. Get Requests

**GET** `/requests?status=pending&limit=50&skip=0`

List emergency requests with optional filtering.

**Query Parameters:**
- `status` (optional): Filter by status (pending, processing, dispatched, completed, cancelled)
- `limit` (optional): Maximum results (default: 50)
- `skip` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "request_id": "uuid-here",
    "original_message": "Help! ...",
    "source": "sms",
    "urgency_level": "critical",
    "status": "pending",
    "received_at": "2026-02-07T10:30:00Z",
    ...
  }
]
```

### 4. Get Request Details

**GET** `/requests/{request_id}`

Get detailed information about a specific request.

**Response:** Full EmergencyRequest object with all details.

### 5. List Resources

**GET** `/resources?status=active&resource_type=ambulance`

List available resources.

**Query Parameters:**
- `status` (optional): Filter by status (active, inactive, deployed)
- `resource_type` (optional): Filter by type

**Response:**
```json
[
  {
    "resource_id": "ambulance-001",
    "resource_type": "ambulance",
    "name": "City Hospital Ambulance Unit A",
    "location": {
      "address": "123 Hospital Drive",
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    "capacity": 4,
    "current_availability": 4,
    "capabilities": ["medical_aid", "rescue"],
    "status": "active",
    ...
  }
]
```

### 6. Create Resource

**POST** `/resources`

Create a new resource in the system.

**Request Body:**
```json
{
  "resource_id": "ambulance-003",
  "resource_type": "ambulance",
  "name": "Emergency Ambulance Unit C",
  "description": "Advanced life support ambulance",
  "location": {
    "address": "789 Medical Center",
    "latitude": 40.7580,
    "longitude": -73.9855,
    "region": "Uptown"
  },
  "capacity": 2,
  "current_availability": 2,
  "capabilities": ["medical_aid"],
  "status": "active",
  "contact_info": {
    "phone": "+1-555-0103"
  },
  "estimated_response_time_minutes": 20
}
```

### 7. Update Resource

**PUT** `/resources/{resource_id}`

Update resource information.

**Request Body:**
```json
{
  "current_availability": 3,
  "status": "active"
}
```

### 8. Dashboard Statistics

**GET** `/dashboard/stats`

Get real-time dashboard statistics.

**Response:**
```json
{
  "total_requests": 150,
  "pending_requests": 8,
  "processing_requests": 3,
  "completed_requests": 125,
  "average_triage_time_seconds": 4.2,
  "critical_requests": 2,
  "high_urgency_requests": 5,
  "resources_available": 12,
  "resources_deployed": 3
}
```

### 9. Health Check

**GET** `/health`

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-07T10:30:00Z"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Example: Complete Workflow

```bash
# 1. Process emergency message
curl -X POST http://localhost:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Medical emergency at Oak Street shelter. Woman in labor.",
    "source": "sms",
    "timestamp": "2026-02-07T10:30:00Z"
  }'

# Save the request_id from response

# 2. Get request details
curl http://localhost:8000/api/v1/requests/{request_id}

# 3. Confirm dispatch
curl -X POST http://localhost:8000/api/v1/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "{request_id}",
    "confirmed": true,
    "selected_resource_id": "ambulance-001",
    "dispatcher_id": "dispatcher-001",
    "dispatcher_notes": "Ambulance dispatched"
  }'

# 4. Check dashboard stats
curl http://localhost:8000/api/v1/dashboard/stats
```

## Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- View all endpoints
- Try API calls directly
- See request/response schemas
- Download OpenAPI specification
