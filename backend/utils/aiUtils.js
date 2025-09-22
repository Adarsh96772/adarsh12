// placeholder anomaly detection functions.
// Replace with ML models or more complex heuristics.

const detectProlongedInactivity = (recentLocations, minutesThreshold = 30) => {
  if (!recentLocations || recentLocations.length === 0) return false;
  const last = recentLocations[recentLocations.length - 1];
  const first = recentLocations[0];
  const diffMin = (new Date(last.timestamp) - new Date(first.timestamp)) / (60*1000);
  return diffMin > minutesThreshold && recentLocations.every(l => l.accuracy > 100 || !l.moved); // naive
};

module.exports = { detectProlongedInactivity };