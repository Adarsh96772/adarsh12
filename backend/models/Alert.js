const mongoose = require('mongoose');

const AlertSchema = new mongoose.Schema({
  tourist: { type: mongoose.Schema.Types.ObjectId, ref: 'Tourist', required: true },
  type: { 
    type: String, 
    enum: ['panic', 'anomaly', 'manual', 'iot'], 
    default: 'panic' 
  },
  message: { type: String, required: true },
  location: {
    type: { type: String, enum: ['Point'], default: 'Point', required: true },
    coordinates: { 
      type: [Number], 
      required: true, 
      validate: {
        validator: function(arr) { return arr.length === 2; },
        message: 'Coordinates must be an array of [lng, lat]'
      }
    }
  },
  resolved: { type: Boolean, default: false },
  createdAt: { type: Date, default: Date.now },
  metadata: { type: Object, default: {} }
});

// Create 2dsphere index for geospatial queries
AlertSchema.index({ location: '2dsphere' });

module.exports = mongoose.model('Alert', AlertSchema);