#!/usr/bin/env node
/**
 * Frontend Verification Script
 * Validates React component imports, dependencies, and API integrations
 * 
 * Run: node frontend/verify_frontend.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  bold: '\x1b[1m',
};

let checksRunning = 0;
let checksPassed = 0;

function log(level, message) {
  const timestamp = new Date().toLocaleTimeString();
  const prefix = `[${timestamp}]`;
  
  switch (level) {
    case 'ok':
      console.log(`${colors.green}✓${colors.reset} ${prefix} ${message}`);
      checksPassed++;
      break;
    case 'error':
      console.log(`${colors.red}✗${colors.reset} ${prefix} ${message}`);
      break;
    case 'warn':
      console.log(`${colors.yellow}⚠${colors.reset} ${prefix} ${message}`);
      break;
    case 'info':
      console.log(`${colors.blue}ℹ${colors.reset} ${prefix} ${message}`);
      break;
    case 'title':
      console.log(`\n${colors.bold}${colors.blue}${message}${colors.reset}`);
      break;
  }
}

function runCheck(name) {
  checksRunning++;
  log('info', `Running check: ${name}`);
  return {
    pass: (msg) => { log('ok', `${name}: ${msg}`); },
    fail: (msg) => { log('error', `${name}: ${msg}`); },
    warn: (msg) => { log('warn', `${name}: ${msg}`); },
  };
}

function fileExists(filePath) {
  return fs.existsSync(filePath);
}

function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch (err) {
    return null;
  }
}

function checkImportsInFile(filePath, requiredImports) {
  const content = readFile(filePath);
  if (!content) return [];
  
  const missing = [];
  requiredImports.forEach(imp => {
    if (!content.includes(imp)) {
      missing.push(imp);
    }
  });
  return missing;
}

// ==================== CHECK 1: Package Dependencies ====================
function checkPackageDependencies() {
  const check = runCheck('Package Dependencies');
  
  const packageJsonPath = path.join(__dirname, 'package.json');
  if (!fileExists(packageJsonPath)) {
    check.fail('package.json not found');
    return false;
  }
  
  const packageJson = JSON.parse(readFile(packageJsonPath));
  const requiredDeps = [
    'react', 'react-dom', '@mui/material', '@mui/icons-material', 'axios', 'vite'
  ];
  
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  const missing = requiredDeps.filter(dep => !allDeps[dep]);
  
  if (missing.length > 0) {
    check.fail(`Missing dependencies: ${missing.join(', ')}`);
    return false;
  }
  
  check.pass(`All ${requiredDeps.length} core dependencies present`);
  return true;
}

// ==================== CHECK 2: Core Files Exist ====================
function checkCoreFiles() {
  const check = runCheck('Core Files');
  
  const requiredFiles = [
    'src/App.jsx',
    'src/main.jsx',
    'src/services/api.js',
    'src/components/ErrorBoundary.jsx',
    'src/pages/DashboardPage.jsx',
    'src/pages/ChatPage.jsx',
    'src/pages/KnowledgeBasePage.jsx',
    'src/pages/CyberRangePage.jsx',
    'vite.config.js',
    'index.html',
  ];
  
  const missing = requiredFiles.filter(f => !fileExists(path.join(__dirname, f)));
  
  if (missing.length > 0) {
    check.fail(`Missing files: ${missing.join(', ')}`);
    return false;
  }
  
  check.pass(`All ${requiredFiles.length} core files present`);
  return true;
}

// ==================== CHECK 3: App.jsx Imports ====================
function checkAppImports() {
  const check = runCheck('App.jsx Imports');
  
  const appPath = path.join(__dirname, 'src/App.jsx');
  const requiredImports = [
    'React',
    '@mui/material',
    '@mui/icons-material',
    'DashboardPage',
    'ChatPage',
    'KnowledgeBasePage',
    'ErrorBoundary',
  ];
  
  const missing = checkImportsInFile(appPath, requiredImports);
  
  if (missing.length > 0) {
    check.fail(`Missing imports in App.jsx: ${missing.join(', ')}`);
    return false;
  }
  
  check.pass(`All ${requiredImports.length} required imports present in App.jsx`);
  return true;
}

// ==================== CHECK 4: API Client Configuration ====================
function checkApiClient() {
  const check = runCheck('API Client Configuration');
  
  const apiPath = path.join(__dirname, 'src/services/api.js');
  const apiContent = readFile(apiPath);
  
  if (!apiContent) {
    check.fail('api.js not found');
    return false;
  }
  
  const requiredFunctions = [
    'getApiUrl',
    'getUserDashboard',
    'getKnowledgeBaseItems',
    'getLabInstructions',
    'healthCheck',
  ];
  
  const missing = requiredFunctions.filter(fn => !apiContent.includes(`export const ${fn}`));
  
  if (missing.length > 0) {
    check.fail(`Missing API functions: ${missing.join(', ')}`);
    return false;
  }
  
  check.pass(`All ${requiredFunctions.length} core API functions exported`);
  return true;
}

// ==================== CHECK 5: Component Structure ====================
function checkComponentStructure() {
  const check = runCheck('Component Structure');
  
  const components = {
    'src/components/ErrorBoundary.jsx': ['React', 'Component', 'componentDidCatch'],
    'src/pages/DashboardPage.jsx': ['useState', 'useEffect', 'getUserDashboard'],
    'src/pages/ChatPage.jsx': ['useState', 'useEffect'],
    'src/pages/KnowledgeBasePage.jsx': ['useState', 'useEffect'],
  };
  
  let validCount = 0;
  const issues = [];
  
  Object.entries(components).forEach(([filePath, requiredContent]) => {
    const fullPath = path.join(__dirname, filePath);
    if (!fileExists(fullPath)) {
      issues.push(`Missing: ${filePath}`);
      return;
    }
    
    const content = readFile(fullPath);
    const missing = requiredContent.filter(item => !content.includes(item));
    
    if (missing.length === 0) {
      validCount++;
    } else {
      issues.push(`${filePath}: Missing ${missing.join(', ')}`);
    }
  });
  
  if (issues.length > 0) {
    check.warn(`Some component issues: ${issues.join('; ')}`);
    return true; // Not a fatal error
  }
  
  check.pass(`All ${validCount} component structures verified`);
  return true;
}

// ==================== CHECK 6: No Duplicate Files ====================
function checkNoDuplicates() {
  const check = runCheck('No Duplicate Files');
  
  const duplicates = [
    { jsx: 'src/components/ErrorBoundary.jsx', js: 'src/components/ErrorBoundary.js' },
  ];
  
  const found = [];
  duplicates.forEach(({ jsx, js }) => {
    const jsxPath = path.join(__dirname, jsx);
    const jsPath = path.join(__dirname, js);
    
    if (fileExists(jsxPath) && fileExists(jsPath)) {
      found.push(`${jsx} and ${js}`);
    }
  });
  
  if (found.length > 0) {
    check.warn(`Duplicate files found: ${found.join(', ')}`);
    return true; // Not fatal
  }
  
  check.pass('No duplicate component files found');
  return true;
}

// ==================== CHECK 7: Vite Configuration ====================
function checkViteConfig() {
  const check = runCheck('Vite Configuration');
  
  const vitePath = path.join(__dirname, 'vite.config.js');
  const viteContent = readFile(vitePath);
  
  if (!viteContent) {
    check.fail('vite.config.js not found');
    return false;
  }
  
  const requiredConfigs = [
    'export default defineConfig',
    'plugins',
    '@vitejs/plugin-react',
  ];
  
  const missing = requiredConfigs.filter(cfg => !viteContent.includes(cfg));
  
  if (missing.length > 0) {
    check.warn(`Missing config: ${missing.join(', ')}`);
    return true;
  }
  
  check.pass('Vite configuration valid');
  return true;
}

// ==================== CHECK 8: HTML Entry Point ====================
function checkHtmlEntry() {
  const check = runCheck('HTML Entry Point');
  
  const htmlPath = path.join(__dirname, 'index.html');
  const htmlContent = readFile(htmlPath);
  
  if (!htmlContent) {
    check.fail('index.html not found');
    return false;
  }
  
  if (!htmlContent.includes('id="root"') && !htmlContent.includes('id="app"')) {
    check.fail('No root element found in index.html');
    return false;
  }
  
  if (!htmlContent.includes('<script')) {
    check.fail('No script tag in index.html');
    return false;
  }
  
  check.pass('HTML entry point properly configured');
  return true;
}

// ==================== MAIN EXECUTION ====================
async function main() {
  console.log(`${colors.bold}${colors.blue}════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.bold}Frontend Verification - CYBER-SENSEI${colors.reset}`);
  console.log(`${colors.bold}${colors.blue}════════════════════════════════════════════════════════${colors.reset}\n`);
  
  log('title', 'Starting Frontend Verification Checks');
  
  const checks = [
    checkPackageDependencies,
    checkCoreFiles,
    checkAppImports,
    checkApiClient,
    checkComponentStructure,
    checkNoDuplicates,
    checkViteConfig,
    checkHtmlEntry,
  ];
  
  const results = checks.map(check => {
    try {
      return check();
    } catch (err) {
      log('error', `Check failed with error: ${err.message}`);
      return false;
    }
  });
  
  // Summary
  console.log(`\n${colors.bold}${colors.blue}════════════════════════════════════════════════════════${colors.reset}`);
  console.log(`${colors.bold}Verification Summary${colors.reset}`);
  console.log(`${colors.bold}${colors.blue}════════════════════════════════════════════════════════${colors.reset}`);
  
  const passedChecks = results.filter(r => r).length;
  const totalChecks = results.length;
  
  console.log(`Checks Passed: ${colors.green}${checksPassed}/${totalChecks}${colors.reset}`);
  console.log(`Status: ${passedChecks === totalChecks ? colors.green + '✓ ALL CHECKS PASSED' + colors.reset : colors.red + '✗ SOME CHECKS FAILED' + colors.reset}`);
  console.log(`\n`);
  
  if (passedChecks === totalChecks) {
    console.log(`${colors.green}Frontend is properly structured and ready for testing!${colors.reset}\n`);
    process.exit(0);
  } else {
    console.log(`${colors.red}Please fix the issues above before proceeding.${colors.reset}\n`);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
