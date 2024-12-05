// craco.config.js

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Полифиллы для различных Node.js модулей, которые требуются для браузера
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        url: require.resolve('url/'),
        path: require.resolve('path-browserify'),
        zlib: require.resolve('browserify-zlib'),
        crypto: require.resolve('crypto-browserify'),
        fs: false,
        stream: require.resolve('stream-browserify'),
        util: require.resolve('util/'),
        querystring: require.resolve('querystring-es3'),
        buffer: require.resolve('buffer/'),
        net: require.resolve('stream-http'),
        http: require.resolve('stream-http'),
      };

      return webpackConfig;  // Возвращаем измененную конфигурацию
    },
  },
};
