import React, { useState, useEffect } from 'react';
import {
  User, Mail, Phone, MapPin, Calendar, Shield,
  Edit3, Save, X, Plus, Trash2, Eye, EyeOff,
  Smartphone, CreditCard, CreditCard as IdCard, Clock,
  AlertTriangle, CheckCircle, Camera, QrCode
} from 'lucide-react';
import { touristAPI } from '../services/api';
import authService from '../services/authService';
import toast from 'react-hot-toast';

const TouristProfile = () => {
  const [user, setUser] = useState(authService.getUser());
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await touristAPI.getProfile();
      setProfile(response.data);
      setFormData({
        name: response.data.name || '',
        phone: response.data.phone || '',
        passport: response.data.passport || '',
        aadhaar: response.data.aadhaar || '',
        language: response.data.language || 'en',
        tripItinerary: response.data.tripItinerary || [],
        emergencyContacts: response.data.emergencyContacts || [],
        optedInTracking: response.data.optedInTracking || false
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
      toast.error('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await touristAPI.updateProfile(formData);
      setProfile(response.data);
      setEditing(false);
      toast.success('Profile updated successfully');
      
      // Update auth service user data
      const updatedUser = { ...user, name: response.data.name };
      authService.setAuth(authService.getToken(), updatedUser);
      setUser(updatedUser);
    } catch (error) {
      console.error('Failed to update profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      name: profile.name || '',
      phone: profile.phone || '',
      passport: profile.passport || '',
      aadhaar: profile.aadhaar || '',
      language: profile.language || 'en',
      tripItinerary: profile.tripItinerary || [],
      emergencyContacts: profile.emergencyContacts || [],
      optedInTracking: profile.optedInTracking || false
    });
    setEditing(false);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addItineraryItem = () => {
    setFormData(prev => ({
      ...prev,
      tripItinerary: [...prev.tripItinerary, { place: '', from: '', to: '' }]
    }));
  };

  const removeItineraryItem = (index) => {
    setFormData(prev => ({
      ...prev,
      tripItinerary: prev.tripItinerary.filter((_, i) => i !== index)
    }));
  };

  const handleItineraryChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      tripItinerary: prev.tripItinerary.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const addEmergencyContact = () => {
    setFormData(prev => ({
      ...prev,
      emergencyContacts: [...prev.emergencyContacts, '']
    }));
  };

  const removeEmergencyContact = (index) => {
    setFormData(prev => ({
      ...prev,
      emergencyContacts: prev.emergencyContacts.filter((_, i) => i !== index)
    }));
  };

  const handleEmergencyContactChange = (index, value) => {
    setFormData(prev => ({
      ...prev,
      emergencyContacts: prev.emergencyContacts.map((contact, i) => 
        i === index ? value : contact
      )
    }));
  };

  const getSafetyScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSafetyScoreBg = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Tourist Profile</h1>
              <p className="text-gray-600 mt-1">
                Manage your personal information and travel preferences
              </p>
            </div>
            {!editing ? (
              <button
                onClick={() => setEditing(true)}
                className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Edit3 className="h-4 w-4" />
                <span>Edit Profile</span>
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {saving ? (
                    <div className="spinner w-4 h-4"></div>
                  ) : (
                    <Save className="h-4 w-4" />
                  )}
                  <span>{saving ? 'Saving...' : 'Save'}</span>
                </button>
                <button
                  onClick={handleCancel}
                  className="flex items-center space-x-2 bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <X className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Profile Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <div className="custom-card">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                  <User className="h-6 w-6 mr-2 text-blue-600" />
                  Basic Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    {editing ? (
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    ) : (
                      <p className="text-gray-900 font-medium">{profile?.name}</p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <p className="text-gray-600 flex items-center">
                      <Mail className="h-4 w-4 mr-2" />
                      {profile?.email}
                      <span className="ml-2 text-xs bg-gray-100 px-2 py-1 rounded">
                        Verified
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    {editing ? (
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    ) : (
                      <p className="text-gray-900 flex items-center">
                        <Phone className="h-4 w-4 mr-2" />
                        {profile?.phone || 'Not provided'}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language Preference
                    </label>
                    {editing ? (
                      <select
                        name="language"
                        value={formData.language}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="as">Assamese</option>
                        <option value="bn">Bengali</option>
                        <option value="te">Telugu</option>
                        <option value="ta">Tamil</option>
                        <option value="ml">Malayalam</option>
                        <option value="kn">Kannada</option>
                        <option value="gu">Gujarati</option>
                        <option value="mr">Marathi</option>
                        <option value="pa">Punjabi</option>
                      </select>
                    ) : (
                      <p className="text-gray-900">{profile?.language === 'en' ? 'English' : profile?.language}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Identity Documents */}
            <div className="custom-card">
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                  <Shield className="h-6 w-6 mr-2 text-green-600" />
                  Identity Documents
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Passport Number
                    </label>
                    {editing ? (
                      <div className="relative">
                        <CreditCard className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <input
                          type="text"
                          name="passport"
                          value={formData.passport}
                          onChange={handleChange}
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Enter passport number"
                        />
                      </div>
                    ) : (
                      <p className="text-gray-900 font-mono">
                        {profile?.passport ? `****${profile.passport.slice(-4)}` : 'Not provided'}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Aadhaar Number
                    </label>
                    {editing ? (
                      <div className="relative">
                        <CreditCard className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                        <input
                          type="text"
                          name="aadhaar"
                          value={formData.aadhaar}
                          onChange={handleChange}
                          maxLength="12"
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Enter Aadhaar number"
                        />
                      </div>
                    ) : (
                      <p className="text-gray-900 font-mono">
                        {profile?.aadhaar ? `****${profile.aadhaar.slice(-4)}` : 'Not provided'}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Digital ID */}
                {profile?.digitalId && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <QrCode className="h-5 w-5 text-blue-600 mr-2" />
                        <div>
                          <p className="text-sm font-medium text-blue-800">Digital Tourist ID</p>
                          <p className="text-xs text-blue-600 font-mono">{profile.digitalId}</p>
                        </div>
                      </div>
                      <button className="text-blue-600 hover:text-blue-700">
                        <Eye className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Emergency Contacts */}
            <div className="custom-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 flex items-center">
                    <AlertTriangle className="h-6 w-6 mr-2 text-red-600" />
                    Emergency Contacts
                  </h2>
                  {editing && (
                    <button
                      onClick={addEmergencyContact}
                      className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Contact</span>
                    </button>
                  )}
                </div>
                <div className="space-y-3">
                  {(editing ? formData.emergencyContacts : profile?.emergencyContacts || []).map((contact, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="flex-1">
                        {editing ? (
                          <input
                            type="tel"
                            value={contact}
                            onChange={(e) => handleEmergencyContactChange(index, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Emergency contact number"
                          />
                        ) : (
                          <p className="text-gray-900 flex items-center">
                            <Phone className="h-4 w-4 mr-2 text-gray-400" />
                            {contact}
                          </p>
                        )}
                      </div>
                      {editing && (
                        <button
                          onClick={() => removeEmergencyContact(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  ))}
                  {(!profile?.emergencyContacts || profile.emergencyContacts.length === 0) && !editing && (
                    <p className="text-gray-500 text-center py-4">No emergency contacts added</p>
                  )}
                </div>
              </div>
            </div>

            {/* Trip Itinerary */}
            <div className="custom-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 flex items-center">
                    <MapPin className="h-6 w-6 mr-2 text-purple-600" />
                    Trip Itinerary
                  </h2>
                  {editing && (
                    <button
                      onClick={addItineraryItem}
                      className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Destination</span>
                    </button>
                  )}
                </div>
                <div className="space-y-4">
                  {(editing ? formData.tripItinerary : profile?.tripItinerary || []).map((item, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-gray-900">Destination {index + 1}</h3>
                        {editing && (
                          <button
                            onClick={() => removeItineraryItem(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-xs font-medium text-gray-500 mb-1">Place</label>
                          {editing ? (
                            <input
                              type="text"
                              value={item.place}
                              onChange={(e) => handleItineraryChange(index, 'place', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              placeholder="Destination"
                            />
                          ) : (
                            <p className="text-gray-900">{item.place || 'Not specified'}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-500 mb-1">From Date</label>
                          {editing ? (
                            <input
                              type="date"
                              value={item.from ? new Date(item.from).toISOString().split('T')[0] : ''}
                              onChange={(e) => handleItineraryChange(index, 'from', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                          ) : (
                            <p className="text-gray-900">
                              {item.from ? new Date(item.from).toLocaleDateString() : 'Not specified'}
                            </p>
                          )}
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-500 mb-1">To Date</label>
                          {editing ? (
                            <input
                              type="date"
                              value={item.to ? new Date(item.to).toISOString().split('T')[0] : ''}
                              onChange={(e) => handleItineraryChange(index, 'to', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                          ) : (
                            <p className="text-gray-900">
                              {item.to ? new Date(item.to).toLocaleDateString() : 'Not specified'}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {(!profile?.tripItinerary || profile.tripItinerary.length === 0) && !editing && (
                    <p className="text-gray-500 text-center py-4">No travel plans added</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Safety Score */}
            <div className="custom-card">
              <div className="p-6 text-center">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Safety Score</h3>
                <div className={`w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center ${getSafetyScoreBg(profile?.safetyScore || 50)}`}>
                  <span className={`text-2xl font-bold ${getSafetyScoreColor(profile?.safetyScore || 50)}`}>
                    {profile?.safetyScore || 50}%
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  {(profile?.safetyScore || 50) >= 80 ? 'Excellent Safety Record' : 
                   (profile?.safetyScore || 50) >= 60 ? 'Good Safety Practices' : 
                   'Safety Awareness Needed'}
                </p>
              </div>
            </div>

            {/* Privacy Settings */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Privacy Settings</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">Location Tracking</p>
                      <p className="text-xs text-gray-500">Allow real-time location monitoring</p>
                    </div>
                    {editing ? (
                      <input
                        type="checkbox"
                        name="optedInTracking"
                        checked={formData.optedInTracking}
                        onChange={handleChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    ) : (
                      <div className={`w-4 h-4 rounded ${profile?.optedInTracking ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Account Status */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Account Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Account Type</span>
                    <span className="text-sm font-medium text-blue-600">Tourist</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Member Since</span>
                    <span className="text-sm font-medium text-gray-900">
                      {profile?.createdAt ? new Date(profile.createdAt).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Verification Status</span>
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium text-green-600">Verified</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="custom-card">
              <div className="p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button className="w-full flex items-center space-x-2 py-2 px-3 text-left text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Camera className="h-4 w-4" />
                    <span>Update Profile Photo</span>
                  </button>
                  <button className="w-full flex items-center space-x-2 py-2 px-3 text-left text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Smartphone className="h-4 w-4" />
                    <span>Download Digital ID</span>
                  </button>
                  <button className="w-full flex items-center space-x-2 py-2 px-3 text-left text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                    <Shield className="h-4 w-4" />
                    <span>Privacy Settings</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TouristProfile;