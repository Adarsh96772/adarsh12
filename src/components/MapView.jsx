import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { MapPin, AlertTriangle, Shield, User, Navigation } from 'lucide-react';
import locationService from '../services/locationService';

const MapView = ({ 
  center = [26.2006, 92.9376], // Default to Guwahati
  zoom = 13,
  height = '400px',
  showSafeZones = true,
  showRestrictedZones = true,
  showCurrentLocation = true,
  onLocationUpdate = () => {},
  className = ""
}) => {
  const [currentPosition, setCurrentPosition] = useState(null);
  const [userTrail, setUserTrail] = useState([]);
  const mapRef = useRef();

  // Sample safe zones (green polygons)
  const safeZones = [
    {
      id: 1,
      name: "Tourist Information Center",
      coordinates: [
        [26.2106, 92.9276],
        [26.2156, 92.9276],
        [26.2156, 92.9326],
        [26.2106, 92.9326]
      ],
      color: '#10b981',
      type: 'safe'
    },
    {
      id: 2,
      name: "Main Market Area",
      coordinates: [
        [26.1906, 92.9476],
        [26.1956, 92.9476],
        [26.1956, 92.9526],
        [26.1906, 92.9526]
      ],
      color: '#10b981',
      type: 'safe'
    }
  ];

  // Sample restricted zones (red polygons)
  const restrictedZones = [
    {
      id: 1,
      name: "Military Area - Restricted",
      coordinates: [
        [26.2206, 92.9176],
        [26.2256, 92.9176],
        [26.2256, 92.9226],
        [26.2206, 92.9226]
      ],
      color: '#ef4444',
      type: 'restricted'
    },
    {
      id: 2,
      name: "High-Risk Valley",
      coordinates: [
        [26.1806, 92.9576],
        [26.1856, 92.9576],
        [26.1856, 92.9626],
        [26.1806, 92.9626]
      ],
      color: '#ef4444',
      type: 'restricted'
    }
  ];

  // Sample other tourists (blue markers)
  const otherTourists = [
    {
      id: 1,
      name: "John Doe",
      position: [26.2056, 92.9426],
      safetyScore: 85,
      status: 'active'
    },
    {
      id: 2,
      name: "Jane Smith",
      position: [26.1956, 92.9326],
      safetyScore: 72,
      status: 'active'
    },
    {
      id: 3,
      name: "Alert Tourist",
      position: [26.2156, 92.9176],
      safetyScore: 25,
      status: 'alert'
    }
  ];

  // Custom marker icons
  const createCustomIcon = (color, iconName, size = 30) => {
    const iconHtml = `
      <div style="
        background: ${color};
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${size * 0.4}px;
        color: white;
      ">
        ${iconName}
      </div>
    `;
    return divIcon({
      html: iconHtml,
      className: 'custom-marker-icon',
      iconSize: [size, size],
      iconAnchor: [size/2, size/2]
    });
  };

  useEffect(() => {
    // Get initial position
    const getCurrentPos = async () => {
      try {
        const position = await locationService.getCurrentPosition();
        setCurrentPosition(position);
        setUserTrail(prev => [...prev, position]);
        onLocationUpdate(position);
      } catch (error) {
        console.error('Failed to get location:', error);
      }
    };

    getCurrentPos();

    // Listen for location updates
    const handleLocationUpdate = (event) => {
      const position = event.detail;
      setCurrentPosition(position);
      setUserTrail(prev => [...prev.slice(-50), position]); // Keep last 50 positions
      onLocationUpdate(position);

      // Center map on user location
      if (mapRef.current) {
        mapRef.current.setView([position.lat, position.lng], zoom);
      }
    };

    window.addEventListener('locationUpdate', handleLocationUpdate);
    return () => window.removeEventListener('locationUpdate', handleLocationUpdate);
  }, [onLocationUpdate, zoom]);

  const getSafetyColor = (score) => {
    if (score >= 70) return '#10b981'; // Green
    if (score >= 40) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  const getSafetyStatus = (score) => {
    if (score >= 70) return 'Safe';
    if (score >= 40) return 'Caution';
    return 'Alert';
  };

  return (
    <div className={`relative ${className}`} style={{ height }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        className="rounded-lg shadow-lg"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Safe Zones */}
        {showSafeZones && safeZones.map(zone => (
          <Polygon
            key={`safe-${zone.id}`}
            positions={zone.coordinates}
            pathOptions={{ 
              color: zone.color, 
              fillColor: zone.color,
              fillOpacity: 0.2,
              weight: 2
            }}
          >
            <Popup>
              <div className="text-center">
                <Shield className="h-6 w-6 text-green-500 mx-auto mb-2" />
                <h4 className="font-semibold text-green-700">{zone.name}</h4>
                <p className="text-sm text-gray-600">Safe Zone</p>
              </div>
            </Popup>
          </Polygon>
        ))}

        {/* Restricted Zones */}
        {showRestrictedZones && restrictedZones.map(zone => (
          <Polygon
            key={`restricted-${zone.id}`}
            positions={zone.coordinates}
            pathOptions={{ 
              color: zone.color, 
              fillColor: zone.color,
              fillOpacity: 0.3,
              weight: 2,
              dashArray: '10, 10'
            }}
          >
            <Popup>
              <div className="text-center">
                <AlertTriangle className="h-6 w-6 text-red-500 mx-auto mb-2" />
                <h4 className="font-semibold text-red-700">{zone.name}</h4>
                <p className="text-sm text-gray-600">Restricted Area</p>
                <p className="text-xs text-red-600 mt-1">⚠️ Entry Not Allowed</p>
              </div>
            </Popup>
          </Polygon>
        ))}

        {/* Current User Location */}
        {showCurrentLocation && currentPosition && (
          <>
            <Marker
              position={[currentPosition.lat, currentPosition.lng]}
              icon={createCustomIcon('#3b82f6', '📍', 35)}
            >
              <Popup>
                <div className="text-center">
                  <User className="h-6 w-6 text-blue-500 mx-auto mb-2" />
                  <h4 className="font-semibold text-blue-700">Your Location</h4>
                  <p className="text-sm text-gray-600">
                    Lat: {currentPosition.lat.toFixed(6)}<br />
                    Lng: {currentPosition.lng.toFixed(6)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Accuracy: ±{currentPosition.accuracy}m
                  </p>
                </div>
              </Popup>
            </Marker>

            {/* Location accuracy circle */}
            <Circle
              center={[currentPosition.lat, currentPosition.lng]}
              radius={currentPosition.accuracy || 100}
              pathOptions={{
                color: '#3b82f6',
                fillColor: '#3b82f6',
                fillOpacity: 0.1,
                weight: 1
              }}
            />
          </>
        )}

        {/* Other Tourists */}
        {otherTourists.map(tourist => (
          <Marker
            key={tourist.id}
            position={tourist.position}
            icon={createCustomIcon(
              getSafetyColor(tourist.safetyScore),
              tourist.status === 'alert' ? '⚠️' : '👤',
              25
            )}
          >
            <Popup>
              <div className="text-center">
                <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${
                  tourist.status === 'alert' ? 'bg-red-500 animate-pulse' : 'bg-green-500'
                }`}></div>
                <h4 className="font-semibold">{tourist.name}</h4>
                <div className="flex items-center justify-center space-x-2 mt-2">
                  <span className="text-sm">Safety Score:</span>
                  <span 
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      tourist.safetyScore >= 70 
                        ? 'bg-green-100 text-green-700' 
                        : tourist.safetyScore >= 40 
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {tourist.safetyScore}% - {getSafetyStatus(tourist.safetyScore)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Status: {tourist.status.toUpperCase()}
                </p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* User Trail (optional) */}
        {userTrail.length > 1 && (
          <React.Fragment>
            {userTrail.slice(0, -1).map((position, index) => (
              <Circle
                key={index}
                center={[position.lat, position.lng]}
                radius={5}
                pathOptions={{
                  color: '#3b82f6',
                  fillColor: '#3b82f6',
                  fillOpacity: 0.6,
                  weight: 0
                }}
              />
            ))}
          </React.Fragment>
        )}
      </MapContainer>

      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-10 space-y-2">
        {/* Location Button */}
        <button
          onClick={async () => {
            try {
              const position = await locationService.getCurrentPosition();
              if (mapRef.current) {
                mapRef.current.setView([position.lat, position.lng], 15);
              }
            } catch (error) {
              console.error('Failed to get location:', error);
            }
          }}
          className="p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          title="Center on my location"
        >
          <Navigation className="h-5 w-5 text-blue-600" />
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-lg p-3 space-y-2">
        <h4 className="text-sm font-semibold text-gray-700">Legend</h4>
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Your Location</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span>Safe Zone</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Restricted Zone</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            <span>Other Tourists</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;