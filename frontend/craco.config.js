const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Increase asset size limits to handle large video files
      webpackConfig.performance = {
        ...webpackConfig.performance,
        maxAssetSize: 30 * 1024 * 1024, // 30MB
        maxEntrypointSize: 30 * 1024 * 1024, // 30MB
        assetFilter: function (assetFilename) {
          // Don't warn about large video files
          if (assetFilename.endsWith('.mp4') || assetFilename.endsWith('.webm')) {
            return false;
          }
          return true;
        }
      };

      return webpackConfig;
    }
  },
  devServer: {
    // Increase dev server configuration for large assets
    setupMiddlewares: (middlewares, devServer) => {
      // Increase timeout for large file requests
      if (devServer && devServer.app) {
        devServer.app.use((req, res, next) => {
          if (req.url.includes('.mp4') || req.url.includes('.webm')) {
            res.setTimeout(0); // No timeout for video files
          }
          next();
        });
      }
      return middlewares;
    }
  }
};