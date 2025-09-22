const express = require('express');
const router = express.Router();
const alert = require('../controllers/alertController');
const { authMiddleware } = require('../utils/jwt');

router.post('/panic', authMiddleware, alert.panic);
router.get('/', authMiddleware, alert.getAlerts);

module.exports = router;