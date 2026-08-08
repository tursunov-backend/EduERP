# Permission Usage

Custom permission classes are located in:

```text
apps/common/permissions.py
```

Available permissions:

- `IsSuperUser`
- `IsAdmin`
- `IsTeacher`
- `IsStudent`

---

## Example: Superuser Only

```python
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsSuperUser


class CreateAdminView(CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsSuperUser,
    ]
```

---

## Example: Admin or Superuser

```python
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsAdmin


class CreateTeacherView(CreateAPIView):
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]
```

---

## Example: Teacher or Superuser

```python
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsTeacher


class TeacherDashboardView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsTeacher,
    ]
```

---

## Example: Student or Superuser

```python
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsStudent


class StudentDashboardView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsStudent,
    ]
```

---

## Combining Permissions

Permissions can be combined as needed.

```python
permission_classes = [
    IsAuthenticated,
    IsAdmin,
]
```

Authentication is checked first, then the custom role permission.

---

## Permission Logic

### IsSuperUser

```text
Superuser
```

### IsAdmin

```text
Superuser
OR
Admin
```

### IsTeacher

```text
Superuser
OR
Teacher
```

### IsStudent

```text
Superuser
OR
Student
```