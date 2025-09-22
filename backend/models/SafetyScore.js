const mongoose = require('mongoose');

const SafetyScoreSchema = new mongoose.Schema({
  tourist: { type: mongoose.Schema.Types.ObjectId, ref: 'Tourist', required: true },
  score: Number,
  reason: String,
  computedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('SafetyScore', SafetyScoreSchema);