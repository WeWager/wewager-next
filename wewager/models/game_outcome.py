from django.db import models


class GameOutcome(models.Model):
    external_uid = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=64)
    bet_type = models.CharField(max_length=32)
    bet_price = models.CharField(max_length=5)
    update_dt = models.DateTimeField(auto_now_add=True)
    hit = models.BooleanField(null=True)

    def __str__(self):
        return f"[{self.id}] ({self.bet_type}) {self.description} {self.bet_price}"