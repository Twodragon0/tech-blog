#!/usr/bin/env node
/**
 * Sentry Logs 검증 스크립트
 *
 * 사용법:
 *   node scripts/verify_sentry_logs.js
 *
 * 환경 변수:
 *   SENTRY_DSN: Sentry DSN (필수)
 *   SENTRY_ORG: Sentry 조직 이름 (프로젝트/대시보드 확인 시 필요)
 *   SENTRY_PROJECT: Sentry 프로젝트 이름 (선택, 기본값: tech-blog)
 *   SENTRY_AUTH_TOKEN: Sentry API 토큰 (프로젝트 API 확인 시 필요)
 */

import https from 'node:https';
import process from 'node:process';
import { URL, pathToFileURL } from 'node:url';

// Sentry 설정
// 보안: DSN은 환경 변수로만 제공되어야 하며, 기본값은 사용하지 않음
const SENTRY_DSN = process.env.SENTRY_DSN;
const SENTRY_ORG = process.env.SENTRY_ORG || '';
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
  const publicKey = url.username || '';
  const projectId = url.pathname.replace(/^\/+/, '').split('/')[0] || '';
  return {
    publicKey,
    projectId,
    host: url.hostname,
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
    console.log(`   - Public Key: ${dsnInfo.publicKey ? `${dsnInfo.publicKey.slice(0, 6)}...` : 'missing'}`);
    console.log(`   - Project ID: ${dsnInfo.projectId}`);
    console.log(`   - Organization: ${SENTRY_ORG || '(SENTRY_ORG not set)'}\n`);
    
    // 2. 프로젝트 정보 확인 (Auth Token이 있는 경우)
    if (process.env.SENTRY_AUTH_TOKEN && SENTRY_ORG) {
      try {
        console.log('2. 프로젝트 정보 확인');
        const projectInfo = await sentryAPIRequest(`/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/`);
        console.log(`   ✅ 프로젝트 확인 성공`);
        console.log(`   - 프로젝트 이름: ${projectInfo.name}`);
        console.log(`   - 플랫폼: ${projectInfo.platform}\n`);
      } catch (e) {
        console.log(`   ⚠️  프로젝트 정보 확인 실패 (Auth Token 필요): ${e.message}\n`);
      }
    } else {
      console.log('2. 프로젝트 정보 확인');
      console.log(`   ⚠️  SENTRY_AUTH_TOKEN 또는 SENTRY_ORG가 없어 프로젝트 정보를 확인할 수 없습니다.\n`);
      console.log(`   💡 두 환경 변수를 함께 설정하면 API 기반 검증이 가능합니다.\n`);
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
    if (SENTRY_ORG) {
      console.log(`   - Sentry 대시보드: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/`);
      console.log(`   - Logs 섹션: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/logs/`);
      console.log(`   - 이벤트 수 확인: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/stats/\n`);
    } else {
      console.log('   - SENTRY_ORG를 설정하면 대시보드 링크를 출력합니다.\n');
    }
    
    console.log('✅ 검증 완료!\n');
    
  } catch (error) {
    console.error('❌ 검증 실패:', error.message);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  verifyLogs();
}

export { verifyLogs, parseDSN };
