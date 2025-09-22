import React, { useState, useEffect } from 'react';
import {
  Shield, Users, AlertTriangle, MapPin, Clock,
  Phone, Eye, Search, Filter, Download,
  TrendingUp, Activity, RefreshCw, CheckCircle,
  XCircle, Calendar, FileText, Navigation
} from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
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
  BarElement,
} from 'chart.js';
import MapView from '../components/MapView';
import { alertAPI, touristAPI } from '../services/api';
import toast from 'react-hot-toast';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const PoliceDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    totalTourists: 0,
    activeTourists: 0,
    activeAlerts: 0,
    resolvedAlerts: 0
  });

  // Sample data for charts
  const alertTrendData = {
    labels: ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now'],
    datasets: [
      {
        label: 'Emergency Alerts',
        data: [2, 1, 4, 3, 5, 2, 1],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Safety Alerts',
        data: [1, 2, 1, 2, 1, 3, 2],
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        tension: 0.4,
      }
    ],
  };

  const alertTypeData = {
    labels: ['Panic Button', 'Geofence Violation', 'Anomaly Detection', 'Manual Report'],
    datasets: [
      {
        data: [45, 25, 20, 10],
        backgroundColor: [
          '#ef4444',
          '#f59e0b',
          '#8b5cf6',
          '#06b6d4',
        ],
        borderWidth: 0,
      },
    ],
  };

  const responseTimeData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Avg Response Time (minutes)',
        data: [3.2, 2.8, 4.1, 3.5, 2.9, 4.2, 3.1],
        backgroundColor: '#3b82f6',
      },
    ],
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    filterAlerts();
  }, [alerts, filterType, searchTerm]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load alerts
      const alertsResponse = await alertAPI.getAlerts();
      setAlerts(alertsResponse.data);

      // Calculate stats
      const activeAlerts = alertsResponse.data.filter(alert => !alert.resolved).length;
      const resolvedAlerts = alertsResponse.data.filter(alert => alert.resolved).length;
      
      setStats({
        totalTourists: 156,
        activeTourists: 89,
        activeAlerts,
        resolvedAlerts
      });

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
    toast.success('Dashboard refreshed');
  };

  const filterAlerts = () => {
    let filtered = [...alerts];

    // Filter by type
    if (filterType !== 'all') {
      if (filterType === 'active') {
        filtered = filtered.filter(alert => !alert.resolved);
      } else if (filterType === 'resolved') {
        filtered = filtered.filter(alert => alert.resolved);
      } else {
        filtered = filtered.filter(alert => alert.type === filterType);
      }
    }

    // Filter by search term
    if (searchTerm.trim()) {
      filtered = filtered.filter(alert => 
        alert.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.tourist?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alert.tourist?.phone?.includes(searchTerm)
      );
    }

    setFilteredAlerts(filtered);
  };

  const handleResolveAlert = async (alertId) => {
    try {
      // In a real app, this would call an API to resolve the alert
      setAlerts(prev => prev.map(alert => 
        alert._id === alertId ? { ...alert, resolved: true } : alert
      ));
      toast.success('Alert marked as resolved');
    } catch (error) {
      toast.error('Failed to resolve alert');
    }
  };

  const getAlertTypeIcon = (type) => {
    switch (type) {
      case 'panic': return <AlertTriangle className="h-4 w-4" />;
      case 'anomaly': return <Activity className="h-4 w-4" />;
      case 'manual': return <FileText className="h-4 w-4" />;
      default: return <Shield className="h-4 w-4" />;
    }
  };

  const getAlertTypeColor = (type) => {
    switch (type) {
      case 'panic': return 'text-red-600 bg-red-100';
      case 'anomaly': return 'text-purple-600 bg-purple-100';
      case 'manual': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  // Resolve chart text colors based on current theme
  const isDark = () => document.documentElement.classList.contains('dark');
  const chartText = isDark() ? '#e5e7eb' : '#0f172a'; // slate-200 vs slate-900
  const gridColor = isDark() ? 'rgba(148,163,184,0.2)' : 'rgba(100,116,139,0.2)';

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading police dashboard...</p>
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
              <h1 className="text-3xl font-bold text-white flex items-center">
                <Shield className="h-8 w-8 mr-3 text-blue-400" />
                Police Command Center
              </h1>
              <p className="text-slate-200 mt-1">
                Real-time monitoring and incident response dashboard
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-slate-200">Live Monitoring</span>
              </div>
            </div>
          </div>
        </div>

        {/* Key Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="rounded-xl border border-[#1b2347] bg-[#0f1733]/70 backdrop-blur-md shadow-lg">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-300">Total Tourists</p>
                  <p className="text-3xl font-bold text-white">{stats.totalTourists}</p>
                  <p className="text-xs text-green-400 mt-1">+12% from yesterday</p>
                </div>
                <div className="p-3 bg-blue-900/30 rounded-full">
                  <Users className="h-8 w-8 text-blue-400" />
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-[#1b2347] bg-[#0f1733]/70 backdrop-blur-md shadow-lg">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-300">Active Tourists</p>
                  <p className="text-3xl font-bold text-white">{stats.activeTourists}</p>
                  <p className="text-xs text-green-400 mt-1">Currently tracked</p>
                </div>
                <div className="p-3 bg-green-900/30 rounded-full">
                  <Navigation className="h-8 w-8 text-green-400" />
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-[#1b2347] bg-[#0f1733]/70 backdrop-blur-md shadow-lg">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-300">Active Alerts</p>
                  <p className="text-3xl font-bold text-white">{stats.activeAlerts}</p>
                  <p className="text-xs text-red-400 mt-1">Require attention</p>
                </div>
                <div className="p-3 bg-red-900/30 rounded-full">
                  <AlertTriangle className="h-8 w-8 text-red-400" />
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-[#1b2347] bg-[#0f1733]/70 backdrop-blur-md shadow-lg">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-300">Response Time</p>
                  <p className="text-3xl font-bold text-white">3.2m</p>
                  <p className="text-xs text-green-400 mt-1">Average today</p>
                </div>
                <div className="p-3 bg-yellow-900/30 rounded-full">
                  <Clock className="h-8 w-8 text-yellow-400" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Live Map */}
          <div className="lg:col-span-2 custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-slate-100 flex items-center">
                  <MapPin className="h-6 w-6 mr-2 text-blue-400" />
                  Real-Time Tourist Tracking
                </h2>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-slate-200">Real-time</span>
                </div>
              </div>
              <MapView
                height="500px"
                showCurrentLocation={false}
                showSafeZones={true}
                showRestrictedZones={true}
                className="rounded-lg"
              />
            </div>
          </div>

          {/* Recent Alerts */}
          <div className="custom-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-slate-100">Recent Alerts</h3>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="text-sm border border-[#1b2347] bg-[#121833] text-slate-200 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Alerts</option>
                  <option value="active">Active</option>
                  <option value="resolved">Resolved</option>
                  <option value="panic">Panic</option>
                  <option value="anomaly">Anomaly</option>
                  <option value="manual">Manual</option>
                </select>
              </div>

              {/* Search */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search alerts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-[#1b2347] bg-[#121833] text-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {filteredAlerts.length > 0 ? (
                  filteredAlerts.map((alert) => (
                    <div
                      key={alert._id}
                      className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                        alert.resolved 
                          ? 'bg-[#121833] border-[#1b2347] text-slate-200' 
                          : 'bg-red-900/25 border-red-800/50 text-red-300'
                      }`}
                      onClick={() => setSelectedAlert(alert)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium bg-[#0f1733] border border-[#1b2347] text-slate-200`}>
                              {getAlertTypeIcon(alert.type)}
                              <span className="capitalize">{alert.type}</span>
                            </span>
                            {alert.resolved ? (
                              <CheckCircle className="h-4 w-4 text-green-400" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-400" />
                            )}
                          </div>
                          <p className="text-sm font-medium text-white mb-1">
                            {alert.message}
                          </p>
                          <div className="flex items-center space-x-4 text-xs text-slate-300">
                            <span className="flex items-center space-x-1">
                              <Users className="h-3 w-3" />
                              <span>{alert.tourist?.name || 'Unknown'}</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <Clock className="h-3 w-3" />
                              <span>{formatTimeAgo(alert.createdAt)}</span>
                            </span>
                          </div>
                        </div>
                        {!alert.resolved && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleResolveAlert(alert._id);
                            }}
                            className="text-green-300 hover:text-green-200 text-xs px-2 py-1 border border-green-700/40 rounded hover:bg-green-900/20"
                          >
                            Resolve
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <p className="text-slate-300">No alerts found</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Analytics Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Alert Trends */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-slate-100 mb-4 flex items-center">
                <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
                Alert Trends (24h)
              </h3>
              <div className="h-64">
                <Line
                  data={alertTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                        labels: { color: chartText },
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: { color: chartText },
                        grid: { color: gridColor },
                      },
                      x: {
                        ticks: { color: chartText },
                        grid: { color: gridColor },
                      },
                    },
                  }}
                />
              </div>
            </div>
          </div>

          {/* Alert Types */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-slate-100 mb-4 flex items-center">
                <Activity className="h-5 w-5 mr-2 text-purple-600" />
                Alert Distribution
              </h3>
              <div className="h-64 flex items-center justify-center">
                <div style={{ width: '200px', height: '200px' }}>
                  <Doughnut
                    data={alertTypeData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                          labels: { color: chartText },
                        },
                      },
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Response Times */}
          <div className="custom-card">
            <div className="p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-slate-100 mb-4 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-green-600" />
                Response Times
              </h3>
              <div className="h-64">
                <Bar
                  data={responseTimeData}
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
                        title: {
                          display: true,
                          text: 'Minutes',
                          color: chartText,
                        },
                        ticks: { color: chartText },
                        grid: { color: gridColor },
                      },
                      x: {
                        ticks: { color: chartText },
                        grid: { color: gridColor },
                      },
                    },
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Alert Detail Modal */}
        {selectedAlert && (
          <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
            <div className="bg-[#0f1733] text-slate-200 border border-[#1b2347] rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white">Alert Details</h2>
                  <button onClick={() => setSelectedAlert(null)} className="text-slate-400 hover:text-slate-200">
                    <XCircle className="h-6 w-6" />
                  </button>
                </div>

                <div className="space-y-6">
                  {/* Alert Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-200 mb-1">Alert Type</label>
                      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium bg-[#0f1733] border border-[#1b2347] text-slate-200`}>
                        {getAlertTypeIcon(selectedAlert.type)}
                        <span className="capitalize">{selectedAlert.type}</span>
                      </span>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-200 mb-1">Status</label>
                      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium ${
                        selectedAlert.resolved 
                          ? 'bg-green-900/30 text-green-300 border border-green-800/40' 
                          : 'bg-red-900/30 text-red-300 border border-red-800/40'
                      }`}>
                        {selectedAlert.resolved ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                        <span>{selectedAlert.resolved ? 'Resolved' : 'Active'}</span>
                      </span>
                    </div>
                  </div>

                  {/* Message */}
                  <div>
                    <label className="block text-sm font-medium text-slate-200 mb-1">Message</label>
                    <p className="text-white bg-[#121833] border border-[#1b2347] p-3 rounded-lg">{selectedAlert.message}</p>
                  </div>

                  {/* Tourist Info */}
                  {selectedAlert.tourist && (
                    <div className="bg-[#121833] border border-[#1b2347] p-4 rounded-lg">
                      <h3 className="font-medium text-white mb-2">Tourist Information</h3>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-slate-300">Name:</span>
                          <span className="ml-2 text-slate-100 font-medium">{selectedAlert.tourist.name}</span>
                        </div>
                        <div>
                          <span className="text-slate-300">Phone:</span>
                          <span className="ml-2 text-slate-100 font-medium">{selectedAlert.tourist.phone}</span>
                        </div>
                        <div>
                          <span className="text-slate-300">Email:</span>
                          <span className="ml-2 text-slate-100 font-medium">{selectedAlert.tourist.email}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Location */}
                  {selectedAlert.location && (
                    <div>
                      <label className="block text-sm font-medium text-slate-200 mb-2">Location</label>
                      <div className="bg-[#121833] border border-[#1b2347] p-3 rounded-lg">
                        <p className="font-mono text-sm text-slate-200">
                          Lat: {selectedAlert.location.coordinates[1].toFixed(6)}, 
                          Lng: {selectedAlert.location.coordinates[0].toFixed(6)}
                        </p>
                        <button className="mt-2 text-blue-300 hover:text-blue-200 text-sm flex items-center space-x-1">
                          <MapPin className="h-4 w-4" />
                          <span>View on Map</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Timestamp */}
                  <div>
                    <label className="block text-sm font-medium text-slate-200 mb-1">Created</label>
                    <p className="text-slate-100">
                      {new Date(selectedAlert.createdAt).toLocaleString()}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end space-x-3 pt-4 border-t">
                    {!selectedAlert.resolved && (
                      <button
                        onClick={() => {
                          handleResolveAlert(selectedAlert._id);
                          setSelectedAlert(null);
                        }}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                      >
                        Mark as Resolved
                      </button>
                    )}
                    <button
                      onClick={() => setSelectedAlert(null)}
                      className="bg-slate-600 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PoliceDashboard;