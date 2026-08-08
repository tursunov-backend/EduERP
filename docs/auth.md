# Authentication Module

## Run Project

### 1. Build and Run Docker

```bash
docker compose up --build
```

### 2. Stop Containers

```bash
docker compose down
```

### 3. Stop and Remove Volumes

```bash
docker compose down -v
```

### 4. Create Superuser

```bash
docker compose exec app python manage.py createsuperuser
```

### 5. Run Migrations

```bash
docker compose exec app python manage.py makemigrations
docker compose exec app python manage.py migrate
```

### 6. Open Django Shell

```bash
docker compose exec app python manage.py shell
```

---

# Authentication Features

- JWT Authentication
- Refresh Token
- Token Blacklist
- Logout
- Current User (`/me`)
- Change Password
- Role-Based Access Control (RBAC)

---

# Permissions

## Superuser

Superuser has full access to the entire system.

Permissions:

- Create Admin
- Create Teacher
- Create Student
- Access all endpoints
- Manage all users

---

## Admin

Admin permissions:

- Create Teacher
- Create Student
- Access admin endpoints
- Cannot create another Admin
- Cannot access Superuser-only endpoints

---

## Teacher

Teacher permissions:

- Access teacher endpoints
- Manage only teacher-related resources

---

## Student

Student permissions:

- Access student endpoints
- Manage only student-related resources

---

# Permission Matrix

| Action | Student | Teacher | Admin | Superuser |
|---------|:------:|:------:|:-----:|:---------:|
| Login | ✅ | ✅ | ✅ | ✅ |
| Logout | ✅ | ✅ | ✅ | ✅ |
| Refresh Token | ✅ | ✅ | ✅ | ✅ |
| Me | ✅ | ✅ | ✅ | ✅ |
| Change Password | ✅ | ✅ | ✅ | ✅ |
| Create Student | ❌ | ❌ | ✅ | ✅ |
| Create Teacher | ❌ | ❌ | ✅ | ✅ |
| Create Admin | ❌ | ❌ | ❌ | ✅ |

---

# Authentication Flow

```text
Login
    │
    ▼
Access Token + Refresh Token
    │
    ├────────────► Protected APIs
    │
    ▼
Refresh Token
    │
    ▼
New Access Token
    │
    ▼
Logout / Change Password
    │
    ▼
Refresh Token Blacklisted
```

---

# Notes

- JWT is used for authentication.
- Refresh Tokens are blacklisted on logout.
- All Refresh Tokens are blacklisted after a password change.
- Password validation uses Django's built-in password validators.
- Role-based permissions are implemented using custom DRF permission classes.
- Superuser bypasses all role restrictions.