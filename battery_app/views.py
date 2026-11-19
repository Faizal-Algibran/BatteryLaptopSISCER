import json
import os
import time
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count
from google import genai
from .models import LaptopBatteryRecord
from .utils import train_and_predict

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def dashboard_view(request):
    records = LaptopBatteryRecord.objects.all().order_by('-created_at')
    
    # Statistik Utama (KPI)
    total_devices = records.count()
    prima_count = records.filter(predicted_status='PRIMA').count()
    ganti_count = records.filter(predicted_status='PERLU_GANTI').count()
    avg_health = records.aggregate(Avg('battery_health_percent'))['battery_health_percent__avg']
    avg_health = round(avg_health, 1) if avg_health else 0

    # Data untuk Grafik Rata-rata Kesehatan per Brand (Chart.js)
    brand_stats = (
        records.values('brand')
        .annotate(avg_hp=Avg('battery_health_percent'), count=Count('id'))
        .order_by('-avg_hp')
    )
    brand_labels = [item['brand'] for item in brand_stats]
    brand_health_data = [round(item['avg_hp'], 1) for item in brand_stats]

    context = {
        'records': records,
        'total_devices': total_devices,
        'prima_count': prima_count,
        'ganti_count': ganti_count,
        'avg_health': avg_health,
        'brand_labels_json': json.dumps(brand_labels),
        'brand_health_json': json.dumps(brand_health_data),
    }
    return render(request, 'battery_app/dashboard.html', context)

def add_record_view(request):
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        brand = request.POST.get('brand')
        model_year = int(request.POST.get('model_year'))
        os_name = request.POST.get('os')
        usage_type = request.POST.get('usage_type')
        daily_usage_hours = int(request.POST.get('daily_usage_hours'))
        charging_cycles = int(request.POST.get('charging_cycles'))
        avg_charge_limit_percent = int(request.POST.get('avg_charge_limit_percent'))
        battery_health_percent = int(request.POST.get('battery_health_percent'))
        battery_age_months = int(request.POST.get('battery_age_months'))
        overheating_issues = request.POST.get('overheating_issues')
        performance_rating = int(request.POST.get('performance_rating'))
        
        features = [charging_cycles, battery_age_months, daily_usage_hours, avg_charge_limit_percent]
        predicted_status = train_and_predict(features)
        
        LaptopBatteryRecord.objects.create(
            device_id=device_id, brand=brand, model_year=model_year, os=os_name,
            usage_type=usage_type, daily_usage_hours=daily_usage_hours,
            charging_cycles=charging_cycles, avg_charge_limit_percent=avg_charge_limit_percent,
            battery_health_percent=battery_health_percent, battery_age_months=battery_age_months,
            overheating_issues=overheating_issues, performance_rating=performance_rating,
            predicted_status=predicted_status
        )
        return redirect('dashboard')
        
    return render(request, 'battery_app/add_form.html')

@require_POST
def delete_record_view(request, pk):
    record = get_object_or_404(LaptopBatteryRecord, pk=pk)
    record.delete()
    return redirect('dashboard')

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'reply': 'Silakan ketik pertanyaan seputar laptop terlebih dahulu.'})

            if GEMINI_API_KEY:
                client = genai.Client(api_key=GEMINI_API_KEY)
                prompt = (
                    "Kamu adalah konsultan teknis laptop dan manajemen baterai bernama 'VoltBot'. "
                    "Berikan jawaban yang terstruktur, profesional, ringkas (maksimal 3 paragraf atau poin-poin singkat), "
                    "dan praktis dalam bahasa Indonesia.\n\n"
                    f"Pertanyaan pengguna: {user_message}"
                )
                
                # Mekanisme Auto-Retry 2x jika server 503 High Demand
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.5-flash-lite',
                            contents=prompt,
                        )
                        return JsonResponse({'reply': response.text})
                    except Exception as api_err:
                        if '503' in str(api_err) and attempt == 0:
                            time.sleep(2)
                            continue
                        raise api_err
            else:
                return JsonResponse({'reply': 'API Key belum dikonfigurasi pada server.'})

        except Exception as e:
            err_msg = str(e)
            if '503' in err_msg:
                return JsonResponse({
                    'reply': 'Server AI Google sedang padat sementara (503). Silakan tunggu 5-10 detik lalu klik kirim ulang.'
                })
            return JsonResponse({'reply': f'Kendala koneksi AI: {err_msg}'}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)