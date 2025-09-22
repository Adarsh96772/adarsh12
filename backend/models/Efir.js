const mongoose = require('mongoose');

const EfirSchema = new mongoose.Schema({
  tourist: { type: mongoose.Schema.Types.ObjectId, ref: 'Tourist' },
  incidentType: String,
  details: String,
  evidence: [String], // URLs/storage ids
  policeStation: String,
  createdAt: { type: Date, default: Date.now },
  status: { type: String, enum: ['draft','filed','closed'], default: 'draft' }
});

module.exports = mongoose.model('Efir', EfirSchema);