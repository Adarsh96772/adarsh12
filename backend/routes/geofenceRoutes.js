const express = require('express');
const router = express.Router();
const { checkGeofence } = require('../controllers/geofenceController');

// POST /api/geofence/check
router.post('/check', checkGeofence);

module.exports = router;