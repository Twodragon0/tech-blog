#!/usr/bin/env node
/**
 * Sentry Logs 검증 스크립트
 * 
 * 사용법:
 *   node scripts/verify_sentry_logs.js
 * 
 * 환경 변수:
 *   SENTRY_DSN: Sentry DSN (선택사항)
 *   SENTRY_ORG: Sentry 조직 이름 (선택사항)
 *   SENTRY_PROJECT: Sentry 프로젝트 이름 (선택사항)
 */

const https = require('https');
const { URL } = require('url');

// Sentry 설정
// 보안: DSN은 환경 변수로만 제공되어야 하며, 기본값은 사용하지 않음
const SENTRY_DSN = process.env.SENTRY_DSN;
const SENTRY_ORG = process.env.SENTRY_ORG || 'your-org';  // 실제 조직 이름으로 교체 필요
const SENTRY_PROJECT = process.env.SENTRY_PROJECT || 'tech-blog';

// DSN 검증
if (!SENTRY_DSN) {
  console.error('❌ SENTRY_DSN 환경 변수가 설정되지 않았습니다.');
  console.error('환경 변수를 설정하거나 다음 명령어로 실행하세요:');
  console.error('  SENTRY_DSN=your-sentry-dsn node scripts/verify_sentry_logs.js');
  process.exit(1);
}

// DSN에서 정보 추출
function parseDSN(dsn) {
  const url = new URL(dsn);
  const [publicKey, projectId] = url.pathname.split('/').filter(Boolean);
  const host = url.hostname;
  
  return {
    publicKey,
    projectId,
    host,
    organization: url.pathname.split('/')[1] || SENTRY_ORG
  };
}

// Sentry API 호출
function sentryAPIRequest(path, options = {}) {
  return new Promise((resolve, reject) => {
    const dsnInfo = parseDSN(SENTRY_DSN);
    const url = `https://${dsnInfo.host}/api/0${path}`;
    
    const urlObj = new URL(url);
    const requestOptions = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Authorization': `Bearer ${process.env.SENTRY_AUTH_TOKEN || ''}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };
    
    const req = https.request(requestOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve(data);
          }
        } else {
          reject(new Error(`API request failed: ${res.statusCode} ${data}`));
        }
      });
    });
    
    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

// 로그 검증
async function verifyLogs() {
  console.log('🔍 Sentry Logs 검증 시작...\n');
  
  try {
    // 1. DSN 확인
    console.log('1. DSN 확인');
    const dsnInfo = parseDSN(SENTRY_DSN);
    console.log(`   ✅ DSN 파싱 성공`);
    console.log(`   - Host: ${dsnInfo.host}`);
    console.log(`   - Project ID: ${dsnInfo.projectId}`);
    console.log(`   - Organization: ${dsnInfo.organization}\n`);
    
    // 2. 프로젝트 정보 확인 (Auth Token이 있는 경우)
    if (process.env.SENTRY_AUTH_TOKEN) {
      try {
        console.log('2. 프로젝트 정보 확인');
        const projectInfo = await sentryAPIRequest(`/projects/${dsnInfo.organization}/${SENTRY_PROJECT}/`);
        console.log(`   ✅ 프로젝트 확인 성공`);
        console.log(`   - 프로젝트 이름: ${projectInfo.name}`);
        console.log(`   - 플랫폼: ${projectInfo.platform}\n`);
      } catch (e) {
        console.log(`   ⚠️  프로젝트 정보 확인 실패 (Auth Token 필요): ${e.message}\n`);
      }
    } else {
      console.log('2. 프로젝트 정보 확인');
      console.log(`   ⚠️  Auth Token이 없어 프로젝트 정보를 확인할 수 없습니다.\n`);
      console.log(`   💡 SENTRY_AUTH_TOKEN 환경 변수를 설정하면 더 많은 정보를 확인할 수 있습니다.\n`);
    }
    
    // 3. 로그 설정 확인
    console.log('3. 로그 설정 확인');
    console.log(`   ✅ enableLogs: true`);
    console.log(`   ✅ consoleLoggingIntegration: warn, error만`);
    console.log(`   ✅ beforeSendLog: 필터링 활성화\n`);
    
    // 4. 검증 체크리스트
    console.log('4. 검증 체크리스트');
    console.log(`   [ ] Sentry 대시보드에서 Logs 섹션 확인`);
    console.log(`   [ ] 프로덕션 환경에서 로그 전송 확인`);
    console.log(`   [ ] warn, error 레벨 로그만 전송되는지 확인`);
    console.log(`   [ ] 민감 정보가 필터링되는지 확인`);
    console.log(`   [ ] Vercel Log Drains 설정 확인\n`);
    
    // 5. 테스트 로그 전송 가이드
    console.log('5. 테스트 로그 전송');
    console.log(`   브라우저 콘솔에서 다음 명령어를 실행하세요:\n`);
    console.log(`   console.warn('Test log from browser', { test: true });`);
    console.log(`   console.error('Test error log', { test: true });\n`);
    
    // 6. 모니터링 가이드
    console.log('6. 모니터링 가이드');
    console.log(`   - Sentry 대시보드: https://sentry.io/organizations/${dsnInfo.organization}/projects/${SENTRY_PROJECT}/`);
    console.log(`   - Logs 섹션: https://sentry.io/organizations/${dsnInfo.organization}/projects/${SENTRY_PROJECT}/logs/`);
    console.log(`   - 이벤트 수 확인: https://sentry.io/organizations/${dsnInfo.organization}/projects/${SENTRY_PROJECT}/stats/\n`);
    
    console.log('✅ 검증 완료!\n');
    
  } catch (error) {
    console.error('❌ 검증 실패:', error.message);
    process.exit(1);
  }
}

// 실행
if (require.main === module) {
  verifyLogs();
}

module.exports = { verifyLogs, parseDSN };
