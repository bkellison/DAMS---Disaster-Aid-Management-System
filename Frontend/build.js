const { execSync } = require('child_process');
const path = require('path');

try {
  // Use node to run vite directly
  const vitePath = path.join(__dirname, 'node_modules', 'vite', 'bin', 'vite.js');
  execSync(`node ${vitePath} build`, { stdio: 'inherit' });
} catch (error) {
  console.error('Build failed:', error);
  process.exit(1);
}