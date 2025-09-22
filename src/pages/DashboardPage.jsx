import React, { useState, useEffect } from 'react';
import { 
  Shield, MapPin, AlertTriangle, Activity, 
  Users, Clock, Battery, Navigation, 
  TrendingUp, Eye, Phone, Calendar
} from 'lucide-react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

import MapView from '../components/MapView';
import authService from '../services/authService';
import locationService from '../services/locationService';
import { touristAPI, alertAPI } from '../services/api';
import toast from 'react-hot-toast';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const DashboardPage = () => {
  const [user] = useState(authService.getUser());
  const [currentLocation, setCurrentLocation] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  const [safetyScore, setSafetyScore] = useState(75);
  const [batteryLevel, setBatteryLevel] = useState(85);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Sample data for charts
  const safetyTrendData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Safety Score',
        data: [78, 82, 75, 88, 92, 85, 75],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const activityData = {
    labels: ['Safe Zones', 'Regular Areas', 'Caution Areas'],
    datasets: [
      {
        data: [60, 30, 10],
        backgroundColor: [
          '#10b981',
          '#f59e0b',
          '#ef4444',
        ],
        borderWidth: 0,
      },
    ],
  };

  useEffect(() => {
    initializeDashboard();
  }, []);

  const initializeDashboard = async () => {
    try {
      // Get user profile to update safety score
      const profileResponse = await touristAPI.getProfile();
      setSafetyScore(profileResponse.data.safetyScore || 75);

      // Get recent alerts
      const alertsResponse = await alertAPI.getAlerts();
      setRecentAlerts(alertsResponse.data.slice(0, 5));

      // Get current location
      try {
        const position = await locationService.getCurrentPosition();
        setCurrentLocation(position);
      } catch (error) {
        console.error('Failed to get location:', error);
      }

      // Check if tracking is active
      setIsTracking(locationService.isTracking());

      // Get battery level
      const battery = await locationService.getBatteryLevel();
      if (battery) setBatteryLevel(battery);

    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTracking = () => {
    if (isTracking) {
      locationService.stopTracking();
      setIsTracking(false);
      toast.success('Location tracking stopped');
    } else {
      const started = locationService.startTracking();
      if (started) {
        setIsTracking(true);
        toast.success('Location tracking started');
      }
    }
  };

  const handleLocationUpdate = (location) => {
    setCurrentLocation(location);
  };

  const getSafetyColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSafetyBg = (score) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const safetyRingStyle = (score) => ({
    background: `conic-gradient(#3b82f6 ${score * 3.6}deg, #e5e7eb 0deg)`
  });

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1020] via-[#0d1428] to-[#0b1020] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">Smart Tourist Safety Dashboard</h1>
              <p className="text-sm text-slate-300 mt-1">AI-Powered Monitoring • Geo-Fencing • Blockchain Digital ID</p>
            </div>
            <div className="hidden md:flex items-center gap-3">
              <div className="px-4 py-2 rounded-xl bg-[#121833] text-slate-200 border border-[#1b2347]">
                <p className="text-xs uppercase tracking-wide text-slate-400">Active Tourists</p>
                <p className="text-lg font-semibold">342</p>
              </div>
              <div className="px-4 py-2 rounded-xl bg-[#121833] text-slate-200 border border-[#1b2347]">
                <p className="text-xs uppercase tracking-wide text-slate-400">Alerts</p>
                <p className="text-lg font-semibold">{recentAlerts.filter(a => !a.resolved).length}</p>
              </div>
              <div className="px-4 py-2 rounded-xl bg-[#121833] text-slate-200 border border-[#1b2347]">
                <p className="text-xs uppercase tracking-wide text-slate-400">System Health</p>
                <p className="text-lg font-semibold">{Math.max(50, safetyScore)}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Key Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Safety Score */}
          <div className={`custom-card border-2 ${getSafetyBg(safetyScore)}`}>
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Safety Score</p>
                  <p className={`text-xs inline-flex items-center px-2 py-0.5 rounded-full mt-1 ${
                    safetyScore >= 80 ? 'bg-green-100 text-green-700' : safetyScore >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                  }`}>
                    <Shield className="h-3 w-3 mr-1" />
                    {safetyScore >= 80 ? 'Excellent' : safetyScore >= 60 ? 'Good' : 'Needs Attention'}
                  </p>
                </div>
                {/* Progress Ring */}
                <div className="relative">
                  <div className="h-16 w-16 rounded-full grid place-items-center" style={safetyRingStyle(safetyScore)}>
                    <div className="h-12 w-12 bg-white rounded-full grid place-items-center shadow-inner">
                      <span className={`text-sm font-semibold ${getSafetyColor(safetyScore)}`}>{safetyScore}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Location Status */}
          <div className="custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Location Status</p>
                  <p className="text-lg font-bold text-gray-900">
                    {isTracking ? 'Active' : 'Inactive'}
                  </p>
                  <button
                    onClick={handleToggleTracking}
                    className={`text-xs px-2 py-1 rounded-full mt-1 ${
                      isTracking 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {isTracking ? 'Turn Off' : 'Turn On'}
                  </button>
                </div>
                <div className={`p-3 rounded-full ${
                  isTracking ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  <MapPin className={`h-8 w-8 ${
                    isTracking ? 'text-green-600' : 'text-gray-400'
                  }`} />
                </div>
              </div>
            </div>
          </div>

          {/* Battery Level */}
          <div className="custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Battery Level</p>
                  <p className="text-3xl font-bold text-gray-900">{batteryLevel}%</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className={`h-2 rounded-full ${
                        batteryLevel > 50 ? 'bg-green-500' : 
                        batteryLevel > 20 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${batteryLevel}%` }}
                    ></div>
                  </div>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Battery className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Active Alerts */}
          <div className="custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {recentAlerts.filter(alert => !alert.resolved).length}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {recentAlerts.length} total today
                  </p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <AlertTriangle className="h-8 w-8 text-orange-600" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Live Map */}
          <div className="lg:col-span-2 custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-slate-100 flex items-center">
                  <MapPin className="h-6 w-6 mr-2 text-blue-400" />
                  Real-Time Tourist Tracking
                </h2>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-3 py-1 rounded-full bg-[#121833] text-slate-300 border border-[#1b2347]">Safe zones</span>
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-slate-400">Live</span>
                </div>
              </div>
              <MapView
                height="400px"
                showCurrentLocation={true}
                showSafeZones={true}
                showRestrictedZones={true}
                onLocationUpdate={handleLocationUpdate}
                className="rounded-lg"
              />
              {currentLocation && (
                <div className="mt-4 p-3 bg-[#121833] border border-[#1b2347] text-slate-200 rounded-lg">
                  <p className="text-sm">
                    <strong>Current Location:</strong> {currentLocation.lat.toFixed(6)}, {currentLocation.lng.toFixed(6)}
                  </p>
                  <p className="text-sm text-slate-400">
                    Accuracy: ±{currentLocation.accuracy}m | Updated: {formatTimeAgo(currentLocation.timestamp)}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions & Alerts */}
          <div className="space-y-6">
            {/* Emergency Actions */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Emergency Actions</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => window.location.href = '/panic'}
                    className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 text-white font-medium rounded-lg transform transition-all duration-200 hover:scale-105 shadow-lg"
                  >
                    <AlertTriangle className="h-5 w-5" />
                    <span>Panic Button</span>
                  </button>
                  
                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium rounded-lg transform transition-all duration-200 hover:scale-105">
                    <Phone className="h-5 w-5" />
                    <span>Call Emergency</span>
                  </button>

                  <button className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-medium rounded-lg transform transition-all duration-200 hover:scale-105">
                    <Users className="h-5 w-5" />
                    <span>Contact Family</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Active Incidents */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-slate-100 mb-4">Active Incidents</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {recentAlerts.length > 0 ? (
                    recentAlerts.map((alert) => (
                      <div
                        key={alert._id}
                        className={`p-4 rounded-lg border flex items-start justify-between ${
                          alert.resolved ? 'bg-[#121833] border-[#1b2347] text-slate-300' : 'bg-red-900/20 border-red-800/40 text-red-200'
                        }`}
                      >
                        <div className="flex-1 pr-3">
                          <p className="text-sm font-medium text-gray-900">
                            {alert.message}
                          </p>
                          <div className="mt-2 flex items-center gap-2">
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${alert.resolved ? 'bg-[#0f1733] text-slate-300 border-[#1b2347]' : 'bg-red-900/40 text-red-200 border-red-800/40'}`}>
                              {alert.resolved ? 'Resolved' : 'Active'}
                            </span>
                            <span className="text-xs text-slate-400">{formatTimeAgo(alert.createdAt)}</span>
                          </div>
                        </div>
                        <div className={`w-2 h-2 rounded-full mt-1 ${
                          alert.resolved ? 'bg-slate-500' : 'bg-red-500'
                        }`}></div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500 text-center py-4">
                      No recent alerts
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Safety Trend Chart */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-green-600" />
                Safety Score Trend
              </h3>
              <div className="h-64">
                <Line
                  data={safetyTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                      },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          {/* Activity Distribution */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Activity className="h-6 w-6 mr-2 text-purple-600" />
                Activity Distribution
              </h3>
              <div className="h-64 flex items-center justify-center">
                <div style={{ width: '200px', height: '200px' }}>
                  <Doughnut
                    data={activityData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Insights */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* AI Risk Assessment */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Eye className="h-6 w-6 mr-2 text-cyan-400" />
                AI Risk Assessment
              </h3>
              <div className="space-y-4 text-gray-700">
                {[{ label: 'Crowd Density Risk', value: 72, color: 'bg-cyan-400' }, { label: 'Weather Impact', value: 51, color: 'bg-indigo-400' }, { label: 'Security Threat', value: 18, color: 'bg-amber-400' }].map((item, idx) => (
                  <div key={idx}>
                    <div className="flex items-center justify-between text-sm">
                      <span>{item.label}</span>
                      <span>{item.value}%</span>
                    </div>
                    <div className="mt-2 h-2 rounded-full bg-slate-200">
                      <div className={`h-2 rounded-full ${item.color}`} style={{ width: `${item.value}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-orange-400" />
                AI Recommendations
              </h3>
              <div className="space-y-4">
                {[{
                  title: 'Crowd Management',
                  desc: 'Divert foot traffic from Zone C'
                }, {
                  title: 'Weather Advisory',
                  desc: 'Send rain alerts to 30 tourists in outdoor areas'
                }].map((rec, i) => (
                  <div key={i} className="rounded-lg p-4 bg-slate-900 text-white">
                    <p className="text-sm font-semibold text-white">{rec.title}</p>
                    <p className="text-sm text-slate-300 mt-1">{rec.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Geo-Fence Management */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Navigation className="h-6 w-6 mr-2 text-sky-400" />
                Geo-Fence Management
              </h3>
              <div className="space-y-3">
                {[{ name: 'Historical District', status: 'Active', color: 'bg-green-100 text-green-700' }, { name: 'Beach Area', status: 'Active', color: 'bg-green-100 text-green-700' }, { name: 'Construction Zone', status: 'Restricted', color: 'bg-red-100 text-red-700' }].map((z, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-lg p-4 bg-slate-50">
                    <span className="text-sm text-gray-800">{z.name}</span>
                    <span className={`text-xs px-3 py-1 rounded-full ${z.color}`}>{z.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;