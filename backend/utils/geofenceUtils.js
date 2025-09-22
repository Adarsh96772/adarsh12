const turf = require('@turf/turf');

/**
 * Check if a point is inside a circular geofence
 * @param {number} lat - Latitude of the point
 * @param {number} lng - Longitude of the point
 * @param {number} centerLat - Latitude of the geofence center
 * @param {number} centerLng - Longitude of the geofence center
 * @param {number} radiusMeters - Radius of the geofence in meters
 * @returns {boolean} - True if point is inside the geofence
 */
const isInsideRadius = (lat, lng, centerLat, centerLng, radiusMeters) => {
  try {
    const point = turf.point([lng, lat]);
    const center = turf.point([centerLng, centerLat]);
    const distance = turf.distance(point, center, { units: 'meters' });
    
    return distance <= radiusMeters;
  } catch (error) {
    console.error('Error calculating geofence:', error);
    return false;
  }
};

/**
 * Check if a point is inside a polygon geofence
 * @param {number} lat - Latitude of the point
 * @param {number} lng - Longitude of the point
 * @param {Array} polygon - Array of [lng, lat] coordinates defining the polygon
 * @returns {boolean} - True if point is inside the polygon
 */
const isInsidePolygon = (lat, lng, polygon) => {
  try {
    const point = turf.point([lng, lat]);
    const poly = turf.polygon([polygon]);
    
    return turf.booleanPointInPolygon(point, poly);
  } catch (error) {
    console.error('Error calculating polygon geofence:', error);
    return false;
  }
};

/**
 * Calculate distance between two points
 * @param {number} lat1 - Latitude of first point
 * @param {number} lng1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lng2 - Longitude of second point
 * @param {string} units - Units for distance ('meters', 'kilometers', 'miles')
 * @returns {number} - Distance between points
 */
const calculateDistance = (lat1, lng1, lat2, lng2, units = 'meters') => {
  try {
    const point1 = turf.point([lng1, lat1]);
    const point2 = turf.point([lng2, lat2]);
    
    return turf.distance(point1, point2, { units });
  } catch (error) {
    console.error('Error calculating distance:', error);
    return 0;
  }
};

/**
 * Check if a point is near a line (route/path)
 * @param {number} lat - Latitude of the point
 * @param {number} lng - Longitude of the point
 * @param {Array} lineCoords - Array of [lng, lat] coordinates defining the line
 * @param {number} toleranceMeters - Distance tolerance in meters
 * @returns {boolean} - True if point is near the line
 */
const isNearLine = (lat, lng, lineCoords, toleranceMeters = 100) => {
  try {
    const point = turf.point([lng, lat]);
    const line = turf.lineString(lineCoords);
    const distance = turf.pointToLineDistance(point, line, { units: 'meters' });
    
    return distance <= toleranceMeters;
  } catch (error) {
    console.error('Error calculating line proximity:', error);
    return false;
  }
};

/**
 * Get the bearing (direction) from one point to another
 * @param {number} lat1 - Latitude of first point
 * @param {number} lng1 - Longitude of first point
 * @param {number} lat2 - Latitude of second point
 * @param {number} lng2 - Longitude of second point
 * @returns {number} - Bearing in degrees (0-360)
 */
const getBearing = (lat1, lng1, lat2, lng2) => {
  try {
    const point1 = turf.point([lng1, lat1]);
    const point2 = turf.point([lng2, lat2]);
    
    return turf.bearing(point1, point2);
  } catch (error) {
    console.error('Error calculating bearing:', error);
    return 0;
  }
};

/**
 * Create a buffer zone around a point
 * @param {number} lat - Latitude of the center point
 * @param {number} lng - Longitude of the center point
 * @param {number} radiusMeters - Radius of the buffer in meters
 * @returns {Object} - GeoJSON polygon representing the buffer
 */
const createBuffer = (lat, lng, radiusMeters) => {
  try {
    const point = turf.point([lng, lat]);
    const buffer = turf.buffer(point, radiusMeters, { units: 'meters' });
    
    return buffer;
  } catch (error) {
    console.error('Error creating buffer:', error);
    return null;
  }
};

/**
 * Check if two geofences overlap
 * @param {Object} geofence1 - First geofence (GeoJSON)
 * @param {Object} geofence2 - Second geofence (GeoJSON)
 * @returns {boolean} - True if geofences overlap
 */
const geofencesOverlap = (geofence1, geofence2) => {
  try {
    return turf.booleanOverlap(geofence1, geofence2) || turf.booleanContains(geofence1, geofence2) || turf.booleanContains(geofence2, geofence1);
  } catch (error) {
    console.error('Error checking geofence overlap:', error);
    return false;
  }
};

/**
 * Simplify a polygon by reducing the number of points
 * @param {Array} coordinates - Array of [lng, lat] coordinates
 * @param {number} tolerance - Simplification tolerance
 * @returns {Array} - Simplified coordinates
 */
const simplifyPolygon = (coordinates, tolerance = 0.01) => {
  try {
    const polygon = turf.polygon([coordinates]);
    const simplified = turf.simplify(polygon, { tolerance, highQuality: true });
    
    return simplified.geometry.coordinates[0];
  } catch (error) {
    console.error('Error simplifying polygon:', error);
    return coordinates;
  }
};

module.exports = {
  isInsideRadius,
  isInsidePolygon,
  calculateDistance,
  isNearLine,
  getBearing,
  createBuffer,
  geofencesOverlap,
  simplifyPolygon
};