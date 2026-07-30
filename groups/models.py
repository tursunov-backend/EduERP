from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    duration_months = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class Group(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='groups')
    max_students = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupStudent(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('frozen', 'Frozen'),
        ('dropped', 'Dropped'),
        ('graduated', 'Graduated'),
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='enrollments')
    joined_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        unique_together = ('group', 'student')

    def __str__(self):
        return f"{self.student} -> {self.group}"