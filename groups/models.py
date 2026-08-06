from django.db import models
import uuid

class GroupDays(models.TextChoices):
    ODD_DAYS = 'ODD', 'Toq kunlar'
    EVEN_DAYS = 'EVEN', 'Juft kunlar'
    EVERY_DAY = 'ALL', 'Har kuni'

class GroupStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Faol'
    COMPLETED = 'COMPLETED', 'Tugallangan'
    RECENTLY = 'RECENTLY', 'Kutilmoqda..'

class Group(models.Model):
    name = models.CharField(max_length=255)
    date_start = models.DateField()
    date_end = models.DateField()
    price = models.IntegerField()
    days = models.CharField(max_length=10, choices=GroupDays.choices)
    time_start = models.TimeField()
    time_end = models.TimeField()
    status = models.CharField(max_length=15, choices=GroupStatus.choices, default=GroupStatus.ACTIVE)
    room = models.UUIDField(default=uuid.uuid4, editable=False)
    max_student = models.IntegerField(default=20)
    teacher = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='groups'
    )
    students = models.ManyToManyField(
        'students.Student', 
        related_name='enrolled_groups', 
        blank=True
    )

    class Meta:
        db_table = 'groups'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name