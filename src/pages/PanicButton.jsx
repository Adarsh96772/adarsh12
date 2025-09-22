import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Phone, MapPin, Clock, 
  Shield, Users, Navigation, Camera,
  Mic, Send, X
} from 'lucide-react';
import { alertAPI } from '../services/api';
import locationService from '../services/locationService';
import toast from 'react-hot-toast';

const PanicButton = () => {
  const [isEmergency, setIsEmergency] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [emergencyMessage, setEmergencyMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emergencyContacts] = useState([
    { name: 'Police', number: '100', type: 'emergency' },
    { name: 'Fire Department', number: '101', type: 'emergency' },
    { name: 'Ambulance', number: '108', type: 'emergency' },
    { name: 'Tourist Helpline', number: '1363', type: 'tourist' },
  ]);

  useEffect(() => {
    // Get current location when component mounts
    getCurrentLocation();
    
    // Listen for location updates
    const handleLocationUpdate = (event) => {
      setCurrentLocation(event.detail);
    };

    window.addEventListener('locationUpdate', handleLocationUpdate);
    return () => window.removeEventListener('locationUpdate', handleLocationUpdate);
  }, []);

  useEffect(() => {
    let timer;
    if (countdown !== null && countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else if (countdown === 0) {
      triggerEmergency();
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const getCurrentLocation = async () => {
    try {
      const position = await locationService.getCurrentPosition();
      setCurrentLocation(position);
    } catch (error) {
      console.error('Failed to get location:', error);
      toast.error('Unable to get your location. Please enable GPS.');
    }
  };

  const startEmergencyCountdown = () => {
    setCountdown(5); // 5 second countdown
    toast.error('Emergency will be triggered in 5 seconds. Tap cancel to stop.');
  };

  const cancelEmergency = () => {
    setCountdown(null);
    setIsEmergency(false);
    toast.success('Emergency cancelled');
  };

  const triggerEmergency = async () => {
    if (!currentLocation) {
      toast.error('Location not available. Getting current location...');
      await getCurrentLocation();
      if (!currentLocation) {
        toast.error('Cannot send emergency alert without location');
        return;
      }
    }

    setIsLoading(true);
    setIsEmergency(true);
    setCountdown(null);

    try {
      const alertData = {
        lat: currentLocation.lat,
        lng: currentLocation.lng,
        message: emergencyMessage || 'Emergency panic button pressed - immediate assistance required'
      };

      await alertAPI.panic(alertData);
      
      toast.success('Emergency alert sent successfully!');
      
      // Auto-dial emergency number after a short delay
      setTimeout(() => {
        window.location.href = 'tel:100'; // Police
      }, 2000);

    } catch (error) {
      console.error('Failed to send emergency alert:', error);
      toast.error('Failed to send emergency alert. Please call emergency services directly.');
    } finally {
      setIsLoading(false);
    }
  };

  const callEmergencyService = (number) => {
    window.location.href = `tel:${number}`;
  };

  if (isEmergency) {
    return (
      <div className="min-h-screen bg-red-600 flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center text-white space-y-6">
          <div className="animate-pulse">
            <AlertTriangle className="h-24 w-24 mx-auto mb-4" />
            <h1 className="text-3xl font-bold mb-2">EMERGENCY ACTIVE</h1>
            <p className="text-xl">Help is on the way!</p>
          </div>

          {isLoading ? (
            <div className="bg-white/20 rounded-lg p-6">
              <div className="spinner w-8 h-8 mx-auto mb-4"></div>
              <p>Sending emergency alert...</p>
            </div>
          ) : (
            <div className="bg-white/20 rounded-lg p-6 space-y-4">
              <p className="text-lg font-semibold">Emergency alert sent successfully!</p>
              <div className="text-sm space-y-2">
                <p>📍 Location: {currentLocation?.lat.toFixed(6)}, {currentLocation?.lng.toFixed(6)}</p>
                <p>🕒 Time: {new Date().toLocaleTimeString()}</p>
                <p>📞 Calling emergency services...</p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {emergencyContacts.slice(0, 4).map((contact) => (
              <button
                key={contact.number}
                onClick={() => callEmergencyService(contact.number)}
                className="bg-white/20 hover:bg-white/30 rounded-lg p-4 transition-all duration-200"
              >
                <Phone className="h-6 w-6 mx-auto mb-2" />
                <p className="text-sm font-medium">{contact.name}</p>
                <p className="text-xs">{contact.number}</p>
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsEmergency(false)}
            className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-lg transition-all duration-200"
          >
            Back to Safety Panel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-red-500 rounded-full flex items-center justify-center mb-4 animate-pulse">
            <AlertTriangle className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-red-600 mb-2">Emergency Panic Button</h1>
          <p className="text-gray-600">
            Press the panic button only in case of real emergency. Help will be dispatched immediately.
          </p>
        </div>

        {countdown !== null && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-red-500 rounded-2xl p-8 text-white text-center max-w-sm mx-4">
              <div className="text-8xl font-bold mb-4 animate-pulse">{countdown}</div>
              <p className="text-xl mb-6">Emergency alert will be sent in {countdown} seconds</p>
              <button
                onClick={cancelEmergency}
                className="bg-white text-red-500 px-8 py-3 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors"
              >
                CANCEL
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Main Panic Button */}
          <div className="custom-card">
            <div className="p-8 text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Emergency Alert</h2>
              
              {/* Location Status */}
              {currentLocation ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-center text-green-600 mb-2">
                    <MapPin className="h-5 w-5 mr-2" />
                    <span className="font-medium">Location Detected</span>
                  </div>
                  <p className="text-sm text-green-700">
                    {currentLocation.lat.toFixed(6)}, {currentLocation.lng.toFixed(6)}
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    Accuracy: ±{currentLocation.accuracy}m
                  </p>
                </div>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center justify-center text-red-600 mb-2">
                    <Navigation className="h-5 w-5 mr-2" />
                    <span className="font-medium">Location Required</span>
                  </div>
                  <p className="text-sm text-red-700">
                    Please enable location services
                  </p>
                  <button
                    onClick={getCurrentLocation}
                    className="text-red-600 hover:text-red-700 text-sm font-medium mt-2"
                  >
                    Retry Location
                  </button>
                </div>
              )}

              {/* Emergency Message */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emergency Message (Optional)
                </label>
                <textarea
                  value={emergencyMessage}
                  onChange={(e) => setEmergencyMessage(e.target.value)}
                  placeholder="Describe your emergency situation..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  rows="3"
                />
              </div>

              {/* Panic Button */}
              <button
                onClick={startEmergencyCountdown}
                disabled={!currentLocation}
                className="w-full h-32 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-2xl font-bold text-2xl shadow-2xl transform transition-all duration-200 hover:scale-105 disabled:cursor-not-allowed disabled:transform-none pulse-glow"
              >
                <div className="flex flex-col items-center">
                  <AlertTriangle className="h-12 w-12 mb-2" />
                  <span>PANIC BUTTON</span>
                </div>
              </button>

              <p className="text-sm text-gray-500 mt-4">
                This will immediately alert emergency services and your emergency contacts
              </p>
            </div>
          </div>

          {/* Emergency Contacts & Information */}
          <div className="space-y-6">
            {/* Quick Call Emergency Services */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Phone className="h-6 w-6 mr-2 text-red-600" />
                  Emergency Services
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {emergencyContacts.map((contact) => (
                    <button
                      key={contact.number}
                      onClick={() => callEmergencyService(contact.number)}
                      className={`p-4 rounded-lg border-2 transition-all duration-200 hover:scale-105 ${
                        contact.type === 'emergency'
                          ? 'border-red-200 bg-red-50 hover:bg-red-100 text-red-700'
                          : 'border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700'
                      }`}
                    >
                      <Phone className="h-5 w-5 mx-auto mb-2" />
                      <p className="text-sm font-bold">{contact.name}</p>
                      <p className="text-xs">{contact.number}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Safety Tips */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <Shield className="h-6 w-6 mr-2 text-green-600" />
                  Safety Tips
                </h3>
                <div className="space-y-3 text-sm text-gray-700">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p>Stay calm and assess your surroundings</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p>If possible, move to a safe, well-lit area</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p>Keep your phone charged and accessible</p>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <p>Inform trusted contacts of your travel plans</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Actions */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Additional Actions</h3>
                <div className="space-y-3">
                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-all duration-200">
                    <Camera className="h-5 w-5" />
                    <span>Take Evidence Photo</span>
                  </button>
                  
                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-green-500 hover:bg-green-600 text-white font-medium rounded-lg transition-all duration-200">
                    <Mic className="h-5 w-5" />
                    <span>Record Voice Note</span>
                  </button>

                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-lg transition-all duration-200">
                    <Send className="h-5 w-5" />
                    <span>Share Live Location</span>
                  </button>

                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-lg transition-all duration-200">
                    <Users className="h-5 w-5" />
                    <span>Alert Emergency Contacts</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Emergency Instructions */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                  <AlertTriangle className="h-6 w-6 mr-2 text-yellow-600" />
                  Emergency Instructions
                </h3>
                <div className="space-y-4">
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                    <h4 className="font-semibold text-yellow-800 mb-2">When to Use Panic Button:</h4>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      <li>• Physical threat or assault</li>
                      <li>• Medical emergency</li>
                      <li>• Lost in dangerous area</li>
                      <li>• Witnessing crime</li>
                      <li>• Natural disaster</li>
                    </ul>
                  </div>

                  <div className="bg-red-50 border-l-4 border-red-400 p-4">
                    <h4 className="font-semibold text-red-800 mb-2">What Happens Next:</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      <li>• Emergency services notified</li>
                      <li>• Your location shared</li>
                      <li>• Emergency contacts alerted</li>
                      <li>• Tourist police dispatched</li>
                      <li>• Help arrives at your location</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Warning */}
        <div className="mt-8 bg-red-100 border border-red-300 rounded-lg p-6 text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-red-800 mb-2">Important Warning</h3>
          <p className="text-red-700">
            The panic button is for genuine emergencies only. False alarms waste valuable emergency 
            resources and may result in penalties. Only use when you genuinely need immediate assistance.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PanicButton;