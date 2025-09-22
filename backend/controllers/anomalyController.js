const LocationLog = require('../models/LocationLog');
const Alert = require('../models/Alert');
const { detectProlongedInactivity } = require('../utils/aiUtils');

exports.checkAnomalies = async (req, res) => {
  try {
    const touristId = req.params.touristId;
    // get recent 10 location logs
    const recent = await LocationLog.find({ tourist: touristId }).sort({ timestamp: 1 }).limit(20).lean();
    const flag = detectProlongedInactivity(recent, 30); // 30 minutes threshold

    if (flag) {
      const a = new Alert({
        tourist: touristId,
        type: 'anomaly',
        message: 'Prolonged inactivity detected',
        location: recent.length ? recent[recent.length-1].location : undefined,
        metadata: { recentCount: recent.length }
      });
      await a.save();
      return res.json({ anomaly: true, alert: a });
    }
    return res.json({ anomaly: false });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};