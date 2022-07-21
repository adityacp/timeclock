from django.db import models
from django.contrib.auth.models import User


class Timeclock(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user"
    )
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    hours = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.clock_out:
            self.hours = (self.clock_out - self.clock_in).total_seconds() / 3600
        super(Timeclock, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return f"{self.user.username} clocked in at {self.clock_in} "\
        f"and clocked out at {self.clock_out}"
