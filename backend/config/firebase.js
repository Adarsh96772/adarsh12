// If you integrate Firebase (push notifications), initialize here.
// For now provide a simple interface placeholder.

module.exports = {
  sendPushNotification: async (tokens, payload) => {
    console.log('sendPushNotification -> tokens:', tokens, 'payload:', payload);
    return true;
  }
};