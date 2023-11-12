# db/models.py
from django.db import models

class Deal(models.Model):
    class Meta:
        verbose_name = "Сделка (битрикс)"
        verbose_name_plural = "Сделки (битрикс)"

    client_name   = models.CharField(max_length=255)
    case_number   = models.CharField(max_length=255, blank=True, null=True)
    state         = models.CharField(max_length=255, default="Первая оплата")
    lawyer        = models.CharField(max_length=255, blank=True, null=True)
    fin_manager   = models.CharField(max_length=255, blank=True, null=True)
    clerk         = models.CharField(max_length=255)
    trade_manager = models.CharField(max_length=255)
    is_belled     = models.BooleanField(default=False)
    last_update   = models.DateTimeField(null=True, blank=True) # формируются после парсинга (не из битрикс) 

    def __str__(self) -> str:
        return self.client_name
    

    def get_deals_by_lawyer(self, lawyer: str):
        asset = self.objects.filter(lawyer=lawyer)
        if not asset:
            return self.objects.create(lawyer=lawyer)
        else:
            return asset.first()
