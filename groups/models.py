from django.db import models
from django.core.validators import MinValueValidator

class GroupDays(models.TextChoices):
    ODD_DAYS = 'ODD', 'Toq kunlar'
    EVEN_DAYS = 'EVEN', 'Juft kunlar'
    EVERY_DAY = 'ALL', 'Har kuni'

class GroupStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Faol'
    COMPLETED = 'COMPLETED', 'Tugallangan'
    RECENTLY = 'RECENTLY', 'Kutilmoqda..'

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    date_start = models.DateField()
    date_end = models.DateField()
    price = models.IntegerField(validators=[MinValueValidator(0)])
    days = models.CharField(max_length=10, choices=GroupDays.choices)
    time_start = models.TimeField()
    time_end = models.TimeField()
    status = models.CharField(max_length=15, choices=GroupStatus.choices, default=GroupStatus.ACTIVE)
    room = models.CharField(max_length=100)
    max_student = models.IntegerField(default=20, validators=[MinValueValidator(1)])
    teacher = models.ForeignKey(
        'teachers.Teacher', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='groups'
    )
    students = models.ManyToManyField(
        'students.Student', 
        related_name='enrolled__groups', 
        blank=True
    )

    class Meta:
        db_table = 'groups'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.name