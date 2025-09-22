const express = require('express');
const router = express.Router();
const tourist = require('../controllers/touristController');
const { authMiddleware } = require('../utils/jwt');

router.get('/me', authMiddleware, tourist.getProfile);
router.get('/:id', authMiddleware, tourist.getProfile);
router.put('/me', authMiddleware, tourist.updateProfile);
router.post('/me/location', authMiddleware, tourist.logLocation);

module.exports = router;