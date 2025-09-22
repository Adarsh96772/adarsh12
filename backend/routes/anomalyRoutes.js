const express = require('express');
const router = express.Router();
const anomaly = require('../controllers/anomalyController');
const { authMiddleware } = require('../utils/jwt');

router.get('/:touristId/check', authMiddleware, anomaly.checkAnomalies);

module.exports = router;