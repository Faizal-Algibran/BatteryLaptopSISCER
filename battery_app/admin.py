from django.contrib import admin
from .models import LaptopBatteryRecord

@admin.register(LaptopBatteryRecord)
class LaptopBatteryRecordAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'brand', 'battery_health_percent', 'predicted_status', 'created_at')