const Tourist = require('../models/Tourist');
const bcrypt = require('bcryptjs');
const { sign } = require('../utils/jwt');
const { issueTouristDigitalId } = require('../utils/blockchainUtils');

exports.register = async (req, res) => {
  try {
    const { name, email, phone, password, passport, aadhaar, tripItinerary, emergencyContacts } = req.body;
    if (!email || !name) return res.status(400).json({ message: 'name & email required' });

    let existing = await Tourist.findOne({ email });
    if (existing) return res.status(409).json({ message: 'Email already registered' });

    const passwordHash = password ? await bcrypt.hash(password, 10) : undefined;

    const t = new Tourist({ name, email, phone, passport, aadhaar, tripItinerary, emergencyContacts, passwordHash });
    await t.save();

    // issue digital id on blockchain (async)
    const bc = await issueTouristDigitalId(t);
    t.digitalId = bc.digitalId || bc.txId;
    await t.save();

    const token = sign({ id: t._id, email: t.email, name: t.name });

    res.status(201).json({ tourist: t, token });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error', error: err.message });
  }
};

exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const t = await Tourist.findOne({ email });
    if (!t) return res.status(404).json({ message: 'User not found' });

    if (!t.passwordHash) return res.status(400).json({ message: 'Password not set for this user' });

    const match = await bcrypt.compare(password, t.passwordHash);
    if (!match) return res.status(401).json({ message: 'Invalid credentials' });

    const token = sign({ id: t._id, email: t.email, name: t.name });
    res.json({ token, tourist: t });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
};