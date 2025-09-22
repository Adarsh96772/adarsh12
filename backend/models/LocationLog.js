const mongoose = require('mongoose');

const LocationLogSchema = new mongoose.Schema({
  tourist: { type: mongoose.Schema.Types.ObjectId, ref: 'Tourist', required: true },
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true } // [lng, lat]
  },
  timestamp: { type: Date, default: Date.now },
  battery: Number,
  accuracy: Number
});

LocationLogSchema.index({ location: '2dsphere' });

module.exports = mongoose.model('LocationLog', LocationLogSchema);