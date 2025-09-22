import { touristAPI, geofenceAPI } from './api';
import toast from 'react-hot-toast';

class LocationService {
  constructor() {
    this.watchId = null;
    this.currentPosition = null;
    this.trackingEnabled = false;
    this.lastLoggedPosition = null;
    this.logInterval = null;
  }

  // Get current position once
  async getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.currentPosition = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date()
          };
          resolve(this.currentPosition);
        },
        (error) => {
          reject(this.handleLocationError(error));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000 // 1 minute
        }
      );
    });
  }

  // Start continuous location tracking
  startTracking() {
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by this browser.');
      return false;
    }

    if (this.trackingEnabled) {
      return true;
    }

    this.trackingEnabled = true;

    // Watch position changes
    this.watchId = navigator.geolocation.watchPosition(
      (position) => {
        this.currentPosition = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date()
        };

        // Check geofences when position updates
        this.checkGeofences();
        
        // Emit custom event for components to listen
        window.dispatchEvent(new CustomEvent('locationUpdate', { 
          detail: this.currentPosition 
        }));
      },
      (error) => {
        console.error('Location tracking error:', error);
        toast.error('Location tracking error: ' + this.handleLocationError(error).message);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 30000 // 30 seconds
      }
    );

    // Start periodic location logging
    this.startLocationLogging();

    toast.success('Location tracking started');
    return true;
  }

  // Stop location tracking
  stopTracking() {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }

    if (this.logInterval) {
      clearInterval(this.logInterval);
      this.logInterval = null;
    }

    this.trackingEnabled = false;
    toast.success('Location tracking stopped');
  }

  // Start periodic location logging to backend
  startLocationLogging(intervalMs = 60000) { // Default: 1 minute
    this.logInterval = setInterval(async () => {
      if (this.currentPosition && this.shouldLogPosition()) {
        try {
          await this.logCurrentLocation();
        } catch (error) {
          console.error('Failed to log location:', error);
        }
      }
    }, intervalMs);
  }

  // Check if we should log current position (avoid spam)
  shouldLogPosition() {
    if (!this.lastLoggedPosition) return true;

    const distance = this.calculateDistance(
      this.currentPosition.lat,
      this.currentPosition.lng,
      this.lastLoggedPosition.lat,
      this.lastLoggedPosition.lng
    );

    // Log if moved more than 50 meters or 5 minutes passed
    const timeDiff = Date.now() - new Date(this.lastLoggedPosition.timestamp).getTime();
    return distance > 0.05 || timeDiff > 300000; // 5 minutes
  }

  // Log current location to backend
  async logCurrentLocation() {
    if (!this.currentPosition) return;

    const locationData = {
      lat: this.currentPosition.lat,
      lng: this.currentPosition.lng,
      accuracy: this.currentPosition.accuracy,
      battery: await this.getBatteryLevel()
    };

    await touristAPI.logLocation(locationData);
    this.lastLoggedPosition = { ...this.currentPosition };
  }

  // Check geofences for current position
  async checkGeofences() {
    if (!this.currentPosition) return;

    try {
      const response = await geofenceAPI.checkGeofence({
        lat: this.currentPosition.lat,
        lng: this.currentPosition.lng
      });

      if (response.data.inside) {
        toast.error(`Warning: You've entered a restricted zone - ${response.data.zone}`);
        
        // Emit geofence alert event
        window.dispatchEvent(new CustomEvent('geofenceAlert', { 
          detail: { zone: response.data.zone, position: this.currentPosition }
        }));
      }
    } catch (error) {
      console.error('Geofence check failed:', error);
    }
  }

  // Get battery level if available
  async getBatteryLevel() {
    try {
      if ('getBattery' in navigator) {
        const battery = await navigator.getBattery();
        return Math.round(battery.level * 100);
      }
    } catch (error) {
      console.warn('Battery API not available');
    }
    return null;
  }

  // Calculate distance between two coordinates (in km)
  calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in km
    const dLat = this.deg2rad(lat2 - lat1);
    const dLon = this.deg2rad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
  }

  deg2rad(deg) {
    return deg * (Math.PI / 180);
  }

  // Handle location errors
  handleLocationError(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return new Error("Location access denied by user.");
      case error.POSITION_UNAVAILABLE:
        return new Error("Location information is unavailable.");
      case error.TIMEOUT:
        return new Error("Location request timed out.");
      default:
        return new Error("An unknown error occurred while retrieving location.");
    }
  }

  // Get current position synchronously (returns last known)
  getLastKnownPosition() {
    return this.currentPosition;
  }

  // Check if tracking is active
  isTracking() {
    return this.trackingEnabled;
  }
}

export default new LocationService();