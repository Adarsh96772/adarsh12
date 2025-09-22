const Tourist = require('../models/Tourist');
const LocationLog = require('../models/LocationLog');

exports.getProfile = async (req, res) => {
  try {
    const id = req.params.id || req.user.id;
    const t = await Tourist.findById(id).lean();
    if (!t) return res.status(404).json({ message: 'Not found' });
    res.json(t);
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
};

exports.updateProfile = async (req, res) => {
  try {
    const id = req.user.id;
    const updates = req.body;
    const t = await Tourist.findByIdAndUpdate(id, updates, { new: true });
    res.json(t);
  } catch (err) {
    res.status(500).json({ message: 'Server error' });
  }
};

// log location endpoint
exports.logLocation = async (req, res) => {
  try {
    const { lat, lng, accuracy, battery } = req.body;
    if (lat == null || lng == null) return res.status(400).json({ message: 'lat & lng required' });

    const loc = new LocationLog({
      tourist: req.user.id,
      location: { type: 'Point', coordinates: [lng, lat] },
      accuracy,
      battery
    });
    await loc.save();

    res.status(201).json({ message: 'Location logged', loc });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};