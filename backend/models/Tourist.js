const mongoose = require('mongoose');

const ItinerarySchema = new mongoose.Schema({
  place: String,
  from: Date,
  to: Date
}, { _id: false });

const TouristSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  phone: String,
  passport: String,
  aadhaar: String,
  digitalId: String, // set after blockchain issuance
  tripItinerary: [ItinerarySchema],
  emergencyContacts: [String],
  safetyScore: { type: Number, default: 50 },
  optedInTracking: { type: Boolean, default: false },
  language: { type: String, default: 'en' },
  passwordHash: { type: String }, // for auth (optional)
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Tourist', TouristSchema);