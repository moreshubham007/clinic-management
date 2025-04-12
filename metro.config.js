const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add this to handle .js files properly
config.resolver.sourceExts = [...config.resolver.sourceExts, 'mjs', 'js', 'jsx', 'json', 'ts', 'tsx'];

module.exports = config; 