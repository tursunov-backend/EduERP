from django.db import models


class Attendance(models.Model):
    date = models.DateTimeField()

    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    students = models.ManyToManyField(
        "students.Student",
        through="AttendanceRecord",
        related_name="attendances"
    )

    def __str__(self):
        return f"{self.group} - {self.date}"


class AttendanceRecord(models.Model):
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name="records"
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )
    status = models.BooleanField()

    class Meta:
        unique_together = ("attendance", "student")

    def __str__(self):
        return f"{self.student} - {self.attendance} - {self.status}"