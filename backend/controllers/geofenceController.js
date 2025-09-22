const { isInsideRadius } = require('../utils/geofenceUtils');
const Alert = require('../models/Alert');

// Example high-risk zone
const sampleHighRiskZone = {
  name: 'Restricted Valley',
  center: { lat: 26.5, lng: 91.8 },
  radiusMeters: 5000
};

exports.checkGeofence = async (req, res) => {
  try {
    const { lat, lng } = req.body;
    if (lat == null || lng == null) 
      return res.status(400).json({ message: 'lat & lng required' });

    const inside = isInsideRadius(
      lat, 
      lng, 
      sampleHighRiskZone.center.lat, 
      sampleHighRiskZone.center.lng, 
      sampleHighRiskZone.radiusMeters
    );

    if (inside) {
      // Create an alert in MongoDB
      const alert = new Alert({
        tourist: req.user?.id || null, // replace with authenticated user if available
        type: 'manual',
        message: `Entered high-risk zone: ${sampleHighRiskZone.name}`,
        location: { type: 'Point', coordinates: [lng, lat] }
      });
      await alert.save();
    }

    res.json({ inside, zone: sampleHighRiskZone.name });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};