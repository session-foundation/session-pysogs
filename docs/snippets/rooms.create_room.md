# Example:

```http
POST /rooms HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "sudoku",
  "name": "Sudoku Solvers",
  "description": "All the best sodoku discussion!"
}
```

```json
{
  "active_users": 0,
  "active_users_cutoff": 604800,
  "admin": true,
  "admins": [
    "050123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  ],
  "created": 1645556525.154345,
  "default_accessible": true,
  "default_read": true,
  "default_upload": true,
  "default_write": true,
  "description": "All the best sodoku discussion!",
  "global_admin": true,
  "global_moderator": true,
  "info_updates": 0,
  "message_sequence": 0,
  "moderator": true,
  "moderators": [],
  "name": "Sudoku Solvers",
  "read": true,
  "token": "sudoku",
  "upload": true,
  "write": true
}
```

(The response is the new room as the requesting user sees it, and so includes the
moderator/admin fields; a room created by a *hidden* global admin also has that admin listed under
`hidden_admins` rather than `admins`.)
