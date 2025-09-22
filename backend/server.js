require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const connectDB = require('./config/db');

// Routes
const authRoutes = require('./routes/authRoutes');
const touristRoutes = require('./routes/touristRoutes');
const alertRoutes = require('./routes/alertRoutes');
const geofenceRoutes = require('./routes/geofenceRoutes');
const anomalyRoutes = require('./routes/anomalyRoutes');

const app = express();

// Connect to MongoDB
connectDB();

// Middlewares
// Use CORS only in development; in production we serve frontend and backend from same origin
if (process.env.NODE_ENV !== 'production') {
  app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
}
app.use(bodyParser.json());
app.use(morgan('dev'));

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/tourists', touristRoutes);
app.use('/api/alerts', alertRoutes);
app.use('/api/geofence', geofenceRoutes);
app.use('/api/anomaly', anomalyRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', env: process.env.NODE_ENV || 'development', time: new Date().toISOString() });
});

// Serve React frontend
const rootDir = path.join(__dirname, '..');
const buildPath = path.join(rootDir, 'build');
app.use(express.static(buildPath));

app.get('*', (req, res) => {
  res.sendFile(path.join(buildPath, 'index.html'));
});

// Start server
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));