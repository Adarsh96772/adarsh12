// small adapter using config/blockchain.js
const blockchain = require('../config/blockchain');

const issueTouristDigitalId = async (touristDoc) => {
  // add attributes needed for immutability
  return blockchain.issueDigitalId({
    touristId: touristDoc._id,
    name: touristDoc.name,
    passport: touristDoc.passport,
    createdAt: new Date()
  });
};

module.exports = { issueTouristDigitalId };