from django.db import models

class LaptopBatteryRecord(models.Model):
    device_id = models.CharField(max_length=50, unique=True)
    brand = models.CharField(max_length=50)
    model_year = models.IntegerField()
    os = models.CharField(max_length=50)
    usage_type = models.CharField(max_length=50)
    daily_usage_hours = models.IntegerField()
    charging_cycles = models.IntegerField()
    avg_charge_limit_percent = models.IntegerField()
    battery_health_percent = models.IntegerField()
    battery_age_months = models.IntegerField()
    overheating_issues = models.CharField(max_length=10)
    performance_rating = models.IntegerField()
    
    predicted_status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.brand} ({self.battery_health_percent}%)"