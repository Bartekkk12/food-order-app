import os
import requests
from django.conf import settings
from datetime import timedelta


class GoogleMapsService:
    """Service for interacting with Google Maps API"""
    
    BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        
        if not self.api_key:
            print("[WARNING] Google Maps API key not configured. Distance calculation will be simulated.")
    
    def calculate_distance(self, origin, destination):

        # If API key is not configured, return simulated data
        if not self.api_key:
            return self._simulate_distance(origin, destination)
        
        try:
            params = {
                'origins': origin,
                'destinations': destination,
                'key': self.api_key,
                'units': 'metric',
                'mode': 'driving',
                'language': 'pl'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"[ERROR] Google Maps API error: {data['status']}")
                return self._simulate_distance(origin, destination)
            
            # Extract distance and duration from response
            element = data['rows'][0]['elements'][0]
            
            if element['status'] != 'OK':
                print(f"[ERROR] Route calculation failed: {element['status']}")
                return self._simulate_distance(origin, destination)
            
            distance_meters = element['distance']['value']
            duration_seconds = element['duration']['value']
            
            return {
                'distance_km': round(distance_meters / 1000, 2),
                'duration_seconds': duration_seconds,
                'status': 'success'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Google Maps API request failed: {e}")
            return self._simulate_distance(origin, destination)
        except (KeyError, IndexError) as e:
            print(f"[ERROR] Failed to parse Google Maps response: {e}")
            return self._simulate_distance(origin, destination)
    
    def _simulate_distance(self, origin, destination):
        """
        Simulate distance calculation when API is not available
        Returns realistic-looking values based on hash of addresses
        """
        # Use hash to get consistent but varied results
        hash_value = hash(f"{origin}{destination}")
        distance_km = abs(hash_value % 20) + 2  # 2-22 km
        
        # Assume average speed of 30 km/h in city
        duration_seconds = int((distance_km / 30) * 3600)
        
        print(f"[SIMULATED] Distance: {distance_km} km, Duration: {duration_seconds}s")
        
        return {
            'distance_km': round(distance_km, 2),
            'duration_seconds': duration_seconds,
            'status': 'simulated'
        }
    
    def format_duration(self, seconds):
        """Convert seconds to readable format"""
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} min"
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours}h {remaining_minutes}min"
