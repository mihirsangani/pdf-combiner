# API Documentation

Complete API reference for FileForge platform.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

Most endpoints require authentication using JWT tokens.

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Authentication Endpoints

### Register User

```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "username": "johndoe",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-08T12:00:00Z"
}
```

### Login

```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Refresh Token

```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Get Current User

```http
GET /auth/me
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "user",
  "is_active": true
}
```

### Create Guest Token

```http
POST /auth/guest-token
```

**Response:** `200 OK`
```json
{
  "guest_token": "guest_abc123...",
  "expires_in": 86400
}
```

## File Upload

### Upload Files

```http
POST /tools/upload
Content-Type: multipart/form-data
```

**Form Data:**
- `files`: File[] (multiple files)
- `guest_token`: string (optional)

**Response:** `200 OK`
```json
{
  "success": true,
  "file_ids": ["file-id-1", "file-id-2"],
  "count": 2
}
```

## PDF Tools

### Merge PDFs

```http
POST /tools/pdf/merge
```

**Request Body:**
```json
{
  "files": ["file-id-1", "file-id-2"],
  "output_filename": "merged.pdf",
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "job_id": "job-abc123",
  "tool_name": "pdf_merge",
  "status": "pending",
  "progress": 0,
  "created_at": "2024-01-08T12:00:00Z",
  "expires_at": "2024-01-09T12:00:00Z"
}
```

### Split PDF

```http
POST /tools/pdf/split
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "split_type": "pages",
  "pages": [0, 2, 4],
  "guest_token": "guest_abc..."
}
```

Or for ranges:
```json
{
  "file_id": "file-id-1",
  "split_type": "ranges",
  "ranges": [[0, 5], [6, 10]],
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

### Compress PDF

```http
POST /tools/pdf/compress
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "compression_level": "medium",
  "guest_token": "guest_abc..."
}
```

Compression levels: `low`, `medium`, `high`

**Response:** `200 OK` (Job object)

## Conversion Tools

### PDF to Word

```http
POST /tools/convert/pdf-to-word
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

### Word to PDF

```http
POST /tools/convert/word-to-pdf
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

### PDF to Images

```http
POST /tools/convert/pdf-to-image
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "output_format": "png",
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

### Images to PDF

```http
POST /tools/convert/image-to-pdf
```

**Request Body:**
```json
{
  "files": ["img-id-1", "img-id-2"],
  "output_filename": "images.pdf",
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

### Convert Image Format

```http
POST /tools/image/convert
```

**Request Body:**
```json
{
  "file_id": "file-id-1",
  "output_format": "webp",
  "quality": 90,
  "width": 800,
  "height": 600,
  "maintain_aspect_ratio": true,
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK` (Job object)

## Job Management

### Get Job Status

```http
GET /jobs/{job_id}?guest_token=guest_abc...
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "job_id": "job-abc123",
  "tool_name": "pdf_merge",
  "status": "completed",
  "progress": 100,
  "output_file_id": 123,
  "created_at": "2024-01-08T12:00:00Z",
  "processing_time_seconds": 2.5
}
```

### Get Simplified Job Status

```http
GET /jobs/{job_id}/status?guest_token=guest_abc...
```

**Response:** `200 OK`
```json
{
  "job_id": "job-abc123",
  "status": "completed",
  "progress": 100,
  "result_url": "/api/v1/files/123/download",
  "error_message": null
}
```

### Cancel Job

```http
POST /jobs/{job_id}/cancel
```

**Request Body:**
```json
{
  "guest_token": "guest_abc..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Job cancelled successfully"
}
```

### Get Job History

```http
GET /jobs/history?page=1&page_size=20&guest_token=guest_abc...
```

**Response:** `200 OK`
```json
{
  "jobs": [...],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

## File Management

### Get File Info

```http
GET /files/{file_id}?guest_token=guest_abc...
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "file_id": "file-abc123",
  "original_filename": "document.pdf",
  "file_size": 1024000,
  "file_type": "pdf",
  "mime_type": "application/pdf",
  "created_at": "2024-01-08T12:00:00Z",
  "expires_at": "2024-01-09T12:00:00Z",
  "download_count": 3
}
```

### Download File

```http
GET /files/{file_id}/download?guest_token=guest_abc...
```

**Response:** `200 OK`
Binary file download with appropriate headers.

### Delete File

```http
DELETE /files/{file_id}?guest_token=guest_abc...
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

## User Management

### Get Dashboard

```http
GET /users/dashboard
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "user": {...},
  "total_jobs": 150,
  "completed_jobs": 145,
  "failed_jobs": 5,
  "total_files_processed": 150,
  "storage_used_mb": 1250.5,
  "recent_jobs": [...]
}
```

### Update Profile

```http
PUT /users/profile
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Name",
  "password": "NewPassword123"
}
```

**Response:** `200 OK` (User object)

### Delete Account

```http
DELETE /users/account
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

## Error Responses

All endpoints may return error responses in this format:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

### Common Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

- **General API**: 60 requests per minute
- **File Upload**: 5 requests per minute
- **Downloads**: 20 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
```

## Pagination

List endpoints support pagination:

```
?page=1&page_size=20
```

Response includes:
- `total`: Total number of items
- `page`: Current page number
- `page_size`: Items per page
- `has_more`: Whether more pages exist

## Interactive API Documentation

Visit `/docs` for Swagger UI interactive documentation.
Visit `/redoc` for ReDoc documentation.

---

For more information, see the [Architecture Documentation](ARCHITECTURE.md).
