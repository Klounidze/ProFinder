# providers/services.py

import requests
import time
from django.conf import settings


class GeocodingService:
    """Сервис для работы с геокодингом через Nominatim (OpenStreetMap)"""

    @staticmethod
    def get_coordinates(address):
        """
        Получение координат по адресу через Nominatim API (OpenStreetMap)
        Бесплатно, без API-ключа
        """
        if not address:
            return None, None

        try:
            # Nominatim API (бесплатный, требует User-Agent)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }

            headers = {
                'User-Agent': 'ProFinder/1.0 (https://pfinder.site)'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data and len(data) > 0:
                    lat = float(data[0].get('lat', 0))
                    lon = float(data[0].get('lon', 0))

                    # Получаем полный адрес
                    address_full = data[0].get('display_name', address)

                    return lat, lon, address_full

            return None, None, None

        except requests.exceptions.Timeout:
            print(f"⏰ Таймаут геокодинга для адреса: {address}")
            return None, None, None
        except Exception as e:
            print(f"❌ Ошибка геокодинга: {e}")
            return None, None, None

    @staticmethod
    def reverse_geocode(lat, lon):
        """
        Получение адреса по координатам через Nominatim API
        """
        if not lat or not lon:
            return None

        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }

            headers = {
                'User-Agent': 'ProFinder/1.0 (https://pfinder.site)'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data and 'display_name' in data:
                    return data['display_name']

            return None

        except Exception as e:
            print(f"❌ Ошибка обратного геокодинга: {e}")
            return None

    @staticmethod
    def geocode_bulk(addresses):
        """
        Массовое геокодирование адресов (с задержкой для соблюдения лимитов)
        """
        results = {}

        for address in addresses:
            if not address:
                continue

            lat, lon, full = GeocodingService.get_coordinates(address)

            if lat and lon:
                results[address] = {
                    'latitude': lat,
                    'longitude': lon,
                    'address_full': full or address
                }

            # Задержка для соблюдения лимитов Nominatim (1 запрос в секунду)
            time.sleep(1)

        return results