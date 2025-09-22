const Alert = require('../models/Alert');
const Tourist = require('../models/Tourist');
const firebase = require('../config/firebase');

exports.panic = async (req, res) => {
  try {
    const { lat, lng, message } = req.body;
    if (lat == null || lng == null) return res.status(400).json({ message: 'lat & lng required' });

    const alert = new Alert({
      tourist: req.user.id,
      type: 'panic',
      message: message || 'Panic button pressed',
      location: { type: 'Point', coordinates: [lng, lat] },
      metadata: { source: 'mobile' }
    });
    await alert.save();

    // fetch tourist emergency contacts
    const tourist = await Tourist.findById(req.user.id);
    // TODO: integrate SMS/WhatsApp/Email/push
    // send push notification (stubbed)
    await firebase.sendPushNotification(tourist.emergencyContacts || [], {
      title: 'Panic Alert',
      body: `${tourist.name} triggered panic at ${lat},${lng}`
    });

    res.status(201).json({ message: 'Alert created', alert });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};

exports.getAlerts = async (req, res) => {
  try {
    const alerts = await Alert.find().sort({ createdAt: -1 }).limit(200).populate('tourist', 'name phone email');
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
};