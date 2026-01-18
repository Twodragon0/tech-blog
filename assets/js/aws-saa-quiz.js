// AWS SAA 기출문제 풀이 인터랙티브 기능
(function() {
  'use strict';

  // 문제 데이터 구조
  const questionsData = [
    {
      id: 1,
      topic: 'VPC 및 네트워크 보안',
      answer: 'A',
      question: '여러 가용 영역에 걸쳐 고가용성 웹 애플리케이션을 배포하려고 합니다. 인터넷에서의 트래픽을 분산하고, 프라이빗 서브넷의 애플리케이션 서버에 안전하게 연결하려면 어떤 아키텍처를 사용해야 합니까?',
      options: {
        A: 'Application Load Balancer를 퍼블릭 서브넷에 배치하고, 애플리케이션 서버를 프라이빗 서브넷에 배치',
        B: 'Network Load Balancer를 프라이빗 서브넷에 배치하고, 애플리케이션 서버를 퍼블릭 서브넷에 배치',
        C: 'Classic Load Balancer를 퍼블릭 서브넷에 배치하고, 애플리케이션 서버를 프라이빗 서브넷에 배치',
        D: 'Application Load Balancer를 프라이빗 서브넷에 배치하고, 애플리케이션 서버를 퍼블릭 서브넷에 배치'
      },
      explanation: 'Application Load Balancer를 퍼블릭 서브넷에 배치하면 인터넷 트래픽을 받을 수 있고, 프라이빗 서브넷의 애플리케이션 서버는 보안이 강화됩니다. <a href="/posts/2025/12/클라우드_시큐리티_8기_2주차_AWS_보안_아키텍처의_핵심_VPC부터_GuardDuty까지_완벽_정복/" target="_blank" rel="noopener noreferrer">VPC 보안 아키텍처 포스트</a>에서 자세한 설명을 확인하세요.'
    },
    {
      id: 2,
      topic: 'IAM 및 접근 제어',
      answer: 'B',
      question: '여러 AWS 계정을 관리하는 조직에서 중앙 집중식 거버넌스를 구현하려고 합니다. 모든 계정에서 특정 서비스 사용을 제한하려면 어떤 서비스를 사용해야 합니까?',
      options: {
        A: 'IAM Policy',
        B: 'AWS Organizations의 Service Control Policy (SCP)',
        C: 'Resource-based Policy',
        D: 'Security Group'
      },
      explanation: 'AWS Organizations의 Service Control Policy (SCP)는 조직 레벨에서 모든 계정에 적용되는 정책입니다. <a href="/posts/2025/12/클라우드_시큐리티_과정_8기_5주차_AWS_Control_TowerSCP_기반_거버넌스_및_Datadog_SIEM_Cloudflare_보안/" target="_blank" rel="noopener noreferrer">AWS Control Tower 및 SCP 포스트</a>에서 자세한 설명을 확인하세요.'
    }
    // 나머지 문제들은 기존 HTML에서 data 속성으로 읽어옴
  ];

  // 상태 관리
  const state = {
    answers: {},
    checked: {},
    stats: {
      total: 0,
      answered: 0,
      correct: 0
    }
  };

  // DOM 로드 후 초기화
  function init() {
    if (!document.querySelector('.exam-questions')) {
      return;
    }

    // 기존 문제 카드를 인터랙티브 형식으로 변환
    convertExistingQuestions();
    
    // 문제 리스트 테이블 생성
    generateQuestionTable();
    
    // 이벤트 리스너 등록
    setupEventListeners();
    
    // 통계 업데이트
    updateStats();
    
    // localStorage에서 저장된 답안 불러오기
    loadSavedAnswers();
  }

  // 기존 문제 카드를 인터랙티브 형식으로 변환
  function convertExistingQuestions() {
    const questionsSection = document.querySelector('#questions-container');
    if (!questionsSection) return;
    
    const questionCards = questionsSection.querySelectorAll('.question-card:not([data-converted])');
    
    questionCards.forEach((card, index) => {
      // 문제 번호 추출 (문제 1, 문제 2 등)
      const questionNumEl = card.querySelector('.question-number');
      const questionNumMatch = questionNumEl?.textContent.match(/문제\s*(\d+)/);
      const questionNum = questionNumMatch ? parseInt(questionNumMatch[1]) : index + 1;
      
      const topic = card.querySelector('.question-topic')?.textContent.trim() || '기타';
      const answerDiv = card.querySelector('.question-answer');
      
      // 학습 전략, 시험 팁 등은 변환하지 않음
      if (!answerDiv || !questionNumEl || !questionNumEl.textContent.includes('문제')) {
        return;
      }
      
      // 정답 추출
      const answerText = answerDiv.textContent;
      const answerMatch = answerText.match(/정답[:\s]*([A-D])/);
      const correctAnswer = answerMatch ? answerMatch[1] : '';
      
      // 해설 추출 (HTML 포함)
      let explanation = '';
      const explanationP = answerDiv.querySelector('p:last-child');
      if (explanationP) {
        explanation = explanationP.innerHTML.replace(/^<strong>해설[:\s]*<\/strong>\s*/, '');
      }
      
      // data 속성 추가
      card.setAttribute('data-topic', topic);
      card.setAttribute('data-answer', correctAnswer);
      card.setAttribute('data-converted', 'true');
      
      // 기존 옵션을 라디오 버튼으로 변환
      const optionsDiv = card.querySelector('.question-options');
      if (optionsDiv && !optionsDiv.querySelector('.option-radio')) {
        const optionParagraphs = optionsDiv.querySelectorAll('p');
        if (optionParagraphs.length > 0) {
          optionsDiv.innerHTML = '';
          
          optionParagraphs.forEach((p) => {
            const optionText = p.textContent.trim();
            const optionMatch = optionText.match(/^([A-D])[.\s]+(.+)/);
            if (optionMatch) {
              const [, value, text] = optionMatch;
              const label = document.createElement('label');
              label.className = 'option-label';
              
              // Security: Use DOM methods instead of innerHTML to prevent XSS
              const radio = document.createElement('input');
              radio.type = 'radio';
              radio.name = `question-${questionNum}`;
              radio.value = value;
              radio.className = 'option-radio';
              radio.setAttribute('aria-label', `선택지 ${value}`);
              
              const optionText = document.createElement('span');
              optionText.className = 'option-text';
              const strong = document.createElement('strong');
              strong.textContent = `${value}. `;
              optionText.appendChild(strong);
              optionText.appendChild(document.createTextNode(text));
              
              label.appendChild(radio);
              label.appendChild(optionText);
              optionsDiv.appendChild(label);
            }
          });
        }
      }
      
      // 액션 버튼 추가
      if (!card.querySelector('.question-actions')) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'question-actions';
        actionsDiv.innerHTML = `
          <button type="button" class="check-button" data-question="${questionNum}" aria-label="문제 ${questionNum} 정답 확인">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            정답 확인
          </button>
          <button type="button" class="explanation-toggle" data-question="${questionNum}" aria-expanded="false" aria-label="문제 ${questionNum} 해설 보기/숨기기">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span class="explanation-text">해설 보기</span>
          </button>
        `;
        
        // 정답 영역을 숨김 처리하고 새 형식으로 변환
        answerDiv.hidden = true;
        answerDiv.id = `answer-${questionNum}`;
        answerDiv.className = 'question-answer';
        
        // Security: Use DOM methods instead of innerHTML to prevent XSS
        const answerContent = document.createElement('div');
        answerContent.className = 'answer-content';
        
        const answerCorrect = document.createElement('p');
        answerCorrect.className = 'answer-correct';
        const strongCorrect = document.createElement('strong');
        strongCorrect.textContent = '정답: ';
        const answerValue = document.createElement('span');
        answerValue.className = 'answer-value';
        answerValue.textContent = correctAnswer;
        answerCorrect.appendChild(strongCorrect);
        answerCorrect.appendChild(answerValue);
        
        const answerExplanation = document.createElement('p');
        answerExplanation.className = 'answer-explanation';
        const strongExplanation = document.createElement('strong');
        strongExplanation.textContent = '해설: ';
        answerExplanation.appendChild(strongExplanation);
        
        // Security: For explanation HTML content, use a temporary div to parse safely
        if (explanation) {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = explanation; // Only trusted content from our own HTML
          while (tempDiv.firstChild) {
            answerExplanation.appendChild(tempDiv.firstChild);
          }
        } else {
          answerExplanation.appendChild(document.createTextNode('해설이 없습니다.'));
        }
        
        answerContent.appendChild(answerCorrect);
        answerContent.appendChild(answerExplanation);
        answerDiv.appendChild(answerContent);
        
        // 액션 버튼을 정답 영역 앞에 삽입
        answerDiv.parentNode.insertBefore(actionsDiv, answerDiv);
      }
      
      // 상태 표시 추가
      if (!card.querySelector('.question-status')) {
        const header = card.querySelector('.question-header');
        if (header) {
          const statusSpan = document.createElement('span');
          statusSpan.className = 'question-status';
          statusSpan.id = `status-${questionNum}`;
          statusSpan.setAttribute('aria-label', `문제 ${questionNum} 상태`);
          header.appendChild(statusSpan);
        }
      }
    });
    
    // 총 문제 수 업데이트
    const totalQuestions = document.querySelectorAll('.question-card[data-converted]').length;
    const totalElement = document.getElementById('total-questions');
    if (totalElement) {
      totalElement.textContent = totalQuestions;
    }
    state.stats.total = totalQuestions;
  }

  // 이벤트 리스너 설정
  function setupEventListeners() {
    // 정답 확인 버튼
    document.addEventListener('click', (e) => {
      if (e.target.closest('.check-button')) {
        const button = e.target.closest('.check-button');
        const questionId = button.dataset.question;
        checkAnswer(questionId);
      }
    });
    
    // 해설 토글 버튼
    document.addEventListener('click', (e) => {
      if (e.target.closest('.explanation-toggle')) {
        const button = e.target.closest('.explanation-toggle');
        const questionId = button.dataset.question;
        toggleExplanation(questionId);
      }
    });
    
    // 라디오 버튼 선택
    document.addEventListener('change', (e) => {
      if (e.target.classList.contains('option-radio')) {
        const questionId = e.target.name.replace('question-', '');
        const selectedAnswer = e.target.value;
        selectAnswer(questionId, selectedAnswer);
      }
    });
    
    // 필터 변경
    const topicFilter = document.getElementById('topic-filter');
    if (topicFilter) {
      topicFilter.addEventListener('change', (e) => {
        filterQuestions(e.target.value);
        filterQuestionTable(e.target.value);
      });
    }
    
    // 검색 기능
    const searchInput = document.getElementById('question-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuestions(e.target.value);
      });
    }
    
    // 뷰 토글
    const viewButtons = document.querySelectorAll('.view-button');
    viewButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        const view = e.currentTarget.dataset.view;
        switchView(view);
      });
    });
    
    // 초기화 버튼
    const resetButton = document.getElementById('reset-answers');
    if (resetButton) {
      resetButton.addEventListener('click', resetAllAnswers);
    }
    
    // 다운로드 버튼
    const downloadAllButton = document.getElementById('download-all-questions');
    if (downloadAllButton) {
      downloadAllButton.addEventListener('click', downloadAllQuestions);
    }
  }

  // 답안 선택
  function selectAnswer(questionId, answer) {
    state.answers[questionId] = answer;
    saveAnswers();
    updateQuestionStatus(questionId);
  }

  // 정답 확인
  function checkAnswer(questionId) {
    // 문제 카드 찾기
    const cards = document.querySelectorAll('.question-card[data-converted]');
    let card = null;
    
    for (let c of cards) {
      const numEl = c.querySelector('.question-number');
      if (numEl) {
        const numMatch = numEl.textContent.match(/문제\s*(\d+)/);
        if (numMatch && parseInt(numMatch[1]) === parseInt(questionId)) {
          card = c;
          break;
        }
      }
    }
    
    if (!card) return;
    
    const correctAnswer = card.dataset.answer;
    const userAnswer = state.answers[questionId];
    const selectedRadio = card.querySelector(`input[name="question-${questionId}"]:checked`);
    
    if (!userAnswer && !selectedRadio) {
      alert('답을 선택해주세요.');
      return;
    }
    
    const answer = userAnswer || selectedRadio.value;
    state.answers[questionId] = answer;
    
    // 이미 체크한 문제인지 확인
    const wasChecked = state.checked[questionId];
    if (!wasChecked) {
      state.checked[questionId] = true;
      state.stats.answered++;
      
      const isCorrect = answer === correctAnswer;
      if (isCorrect) {
        state.stats.correct++;
      }
    } else {
      // 재체크 시 정답률 재계산
      const isCorrect = answer === correctAnswer;
      const prevCorrect = state.answers[questionId] === card.dataset.answer;
      if (prevCorrect && !isCorrect) {
        state.stats.correct--;
      } else if (!prevCorrect && isCorrect) {
        state.stats.correct++;
      }
    }
    
    const isCorrect = answer === correctAnswer;
    updateQuestionStatus(questionId, isCorrect);
    updateStats();
    saveAnswers();
    
    // 정답 영역 표시
    const answerDiv = card.querySelector(`#answer-${questionId}`);
    if (answerDiv) {
      answerDiv.hidden = false;
      answerDiv.classList.add('show');
    }
  }

  // 문제 상태 업데이트
  function updateQuestionStatus(questionId, isCorrect = null) {
    // 문제 카드 찾기
    const cards = document.querySelectorAll('.question-card[data-converted]');
    let card = null;
    
    for (let c of cards) {
      const numEl = c.querySelector('.question-number');
      if (numEl) {
        const numMatch = numEl.textContent.match(/문제\s*(\d+)/);
        if (numMatch && parseInt(numMatch[1]) === parseInt(questionId)) {
          card = c;
          break;
        }
      }
    }
    
    if (!card) return;
    
    const statusEl = document.getElementById(`status-${questionId}`);
    const userAnswer = state.answers[questionId];
    const isChecked = state.checked[questionId];
    
    // 라디오 버튼 스타일 업데이트
    const radios = card.querySelectorAll('.option-radio');
    radios.forEach(radio => {
      const label = radio.closest('.option-label');
      if (!label) return;
      
      label.classList.remove('selected', 'correct', 'incorrect');
      
      if (radio.checked || radio.value === userAnswer) {
        label.classList.add('selected');
      }
      
      if (isChecked) {
        const correctAnswer = card.dataset.answer;
        if (radio.value === correctAnswer) {
          label.classList.add('correct');
        } else if (radio.value === userAnswer && userAnswer !== correctAnswer) {
          label.classList.add('incorrect');
        }
      }
    });
    
    // 상태 아이콘 업데이트
    if (statusEl) {
      if (isChecked) {
        statusEl.innerHTML = isCorrect !== null && isCorrect
          ? '<span class="status-icon correct" aria-label="정답">✓</span>'
          : '<span class="status-icon incorrect" aria-label="오답">✗</span>';
      } else if (userAnswer) {
        statusEl.innerHTML = '<span class="status-icon pending" aria-label="답안 선택됨">○</span>';
      } else {
        statusEl.innerHTML = '';
      }
    }
  }

  // 해설 토글
  function toggleExplanation(questionId) {
    const button = document.querySelector(`.explanation-toggle[data-question="${questionId}"]`);
    const answerDiv = document.getElementById(`answer-${questionId}`);
    
    if (!button || !answerDiv) return;
    
    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    answerDiv.hidden = !isExpanded;
    button.setAttribute('aria-expanded', !isExpanded);
    
    const textSpan = button.querySelector('.explanation-text');
    if (textSpan) {
      textSpan.textContent = isExpanded ? '해설 보기' : '해설 숨기기';
    }
  }

  // 문제 필터링
  function filterQuestions(topic) {
    const cards = document.querySelectorAll('.question-card[data-converted]');
    cards.forEach(card => {
      if (topic === 'all' || card.dataset.topic === topic) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // 문제 검색
  function searchQuestions(query) {
    const cards = document.querySelectorAll('.question-card[data-converted]');
    const searchTerm = query.toLowerCase().trim();
    
    cards.forEach(card => {
      const questionText = card.querySelector('.question-text')?.textContent.toLowerCase() || '';
      const topic = card.querySelector('.question-topic')?.textContent.toLowerCase() || '';
      const options = Array.from(card.querySelectorAll('.option-text')).map(opt => opt.textContent.toLowerCase()).join(' ');
      
      const matches = questionText.includes(searchTerm) || 
                     topic.includes(searchTerm) || 
                     options.includes(searchTerm);
      
      card.style.display = matches ? '' : 'none';
    });
    
    // 리스트 뷰에서도 검색
    filterQuestionTable(null, searchTerm);
  }

  // 뷰 전환
  function switchView(view) {
    const listView = document.getElementById('question-list-view');
    const cardView = document.getElementById('questions-container');
    const viewButtons = document.querySelectorAll('.view-button');
    
    viewButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    if (view === 'list') {
      listView.style.display = 'block';
      if (cardView) {
        cardView.classList.add('hidden');
      }
    } else {
      listView.style.display = 'none';
      if (cardView) {
        cardView.classList.remove('hidden');
      }
    }
  }

  // 문제 리스트 테이블 생성
  function generateQuestionTable() {
    const tbody = document.getElementById('question-table-body');
    if (!tbody) return;
    
    const cards = document.querySelectorAll('.question-card[data-converted]');
    tbody.innerHTML = '';
    
    cards.forEach((card, index) => {
      const questionNum = index + 1;
      const numEl = card.querySelector('.question-number');
      const numMatch = numEl?.textContent.match(/문제\s*(\d+)/);
      const actualNum = numMatch ? parseInt(numMatch[1]) : questionNum;
      
      const topic = card.dataset.topic || '기타';
      const questionText = card.querySelector('.question-text')?.textContent || '';
      const shortQuestion = questionText.length > 80 ? questionText.substring(0, 80) + '...' : questionText;
      
      const row = document.createElement('tr');
      
      // Security: Use DOM methods instead of innerHTML to prevent XSS
      const createCell = (content) => {
        const td = document.createElement('td');
        if (typeof content === 'string') {
          td.textContent = content;
        } else {
          td.appendChild(content);
        }
        return td;
      };
      
      const createLink = (href, text, ariaLabel, className, dataQuestion) => {
        const a = document.createElement('a');
        // Security: Escape href to prevent XSS
        a.href = href.replace(/[<>"']/g, '');
        a.className = className;
        a.setAttribute('data-question', String(dataQuestion));
        a.setAttribute('aria-label', ariaLabel);
        a.textContent = text;
        return a;
      };
      
      const createButton = (text, className, ariaLabel, dataQuestion) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = className;
        btn.setAttribute('data-question', String(dataQuestion));
        btn.setAttribute('aria-label', ariaLabel);
        btn.textContent = text;
        return btn;
      };
      
      // Security: Escape all user input before using
      const safeActualNum = String(actualNum).replace(/[<>"']/g, '');
      const safeShortQuestion = shortQuestion.replace(/[<>"']/g, '');
      const safeTopic = topic.replace(/[<>"']/g, '');
      
      row.appendChild(createCell(safeActualNum));
      row.appendChild(createCell(safeShortQuestion));
      row.appendChild(createCell(safeTopic));
      row.appendChild(createCell(createLink(`#question-${safeActualNum}`, 'CBT', `문제 ${safeActualNum} CBT`, 'table-link', safeActualNum)));
      row.appendChild(createCell(createLink(`#question-${safeActualNum}`, '보기', `문제 ${safeActualNum} 바로보기`, 'table-link', safeActualNum)));
      row.appendChild(createCell(createButton('다운', 'table-link download-question', `문제 ${safeActualNum} 다운로드`, safeActualNum)));
      row.appendChild(createCell(createButton('다운', 'table-link download-explanation', `해설 ${safeActualNum} 다운로드`, safeActualNum)));
      row.appendChild(createCell(createButton('다운', 'table-link download-both', `문제+해설 ${safeActualNum} 다운로드`, safeActualNum)));
      
      tbody.appendChild(row);
    });
    
    // 테이블 링크 이벤트
    tbody.querySelectorAll('a[data-question]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const questionId = link.dataset.question;
        switchView('card');
        setTimeout(() => {
          scrollToQuestion(questionId);
        }, 100);
      });
    });
    
    // 다운로드 버튼 이벤트
    tbody.querySelectorAll('.download-question').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const questionId = btn.dataset.question;
        downloadQuestion(questionId, 'question');
      });
    });
    
    tbody.querySelectorAll('.download-explanation').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const questionId = btn.dataset.question;
        downloadQuestion(questionId, 'explanation');
      });
    });
    
    tbody.querySelectorAll('.download-both').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const questionId = btn.dataset.question;
        downloadQuestion(questionId, 'both');
      });
    });
  }

  // 문제로 스크롤
  function scrollToQuestion(questionId) {
    const cards = document.querySelectorAll('.question-card[data-converted]');
    for (let card of cards) {
      const numEl = card.querySelector('.question-number');
      if (numEl) {
        const numMatch = numEl.textContent.match(/문제\s*(\d+)/);
        if (numMatch && parseInt(numMatch[1]) === parseInt(questionId)) {
          card.id = `question-${questionId}`;
          card.scrollIntoView({ behavior: 'smooth', block: 'start' });
          card.style.animation = 'highlight 2s ease';
          return;
        }
      }
    }
  }

  // 문제 테이블 필터링
  function filterQuestionTable(topic = null, searchTerm = null) {
    const rows = document.querySelectorAll('#question-table-body tr');
    rows.forEach(row => {
      const topicCell = row.cells[2]?.textContent || '';
      const questionCell = row.cells[1]?.textContent || '';
      
      let show = true;
      
      if (topic && topic !== 'all') {
        show = show && topicCell === topic;
      }
      
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        show = show && (questionCell.toLowerCase().includes(searchLower) || topicCell.toLowerCase().includes(searchLower));
      }
      
      row.style.display = show ? '' : 'none';
    });
  }

  // 문제 다운로드
  function downloadQuestion(questionId, type) {
    const cards = document.querySelectorAll('.question-card[data-converted]');
    let card = null;
    
    for (let c of cards) {
      const numEl = c.querySelector('.question-number');
      if (numEl) {
        const numMatch = numEl.textContent.match(/문제\s*(\d+)/);
        if (numMatch && parseInt(numMatch[1]) === parseInt(questionId)) {
          card = c;
          break;
        }
      }
    }
    
    if (!card) return;
    
    const questionText = card.querySelector('.question-text')?.textContent || '';
    const topic = card.dataset.topic || '';
    const options = Array.from(card.querySelectorAll('.option-text')).map(opt => opt.textContent).join('\n');
    const answer = card.dataset.answer || '';
    const explanation = card.querySelector('.answer-explanation')?.textContent || '';
    
    let content = `AWS SAA 기출문제 - 문제 ${questionId}\n`;
    content += `주제: ${topic}\n\n`;
    content += `문제:\n${questionText}\n\n`;
    content += `선택지:\n${options}\n\n`;
    
    if (type === 'explanation' || type === 'both') {
      content += `정답: ${answer}\n\n`;
      content += `해설:\n${explanation}\n`;
    }
    
    if (type === 'question' || type === 'both') {
      // 문제만 다운로드
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AWS-SAA-문제-${questionId}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  // 전체 문제 다운로드
  function downloadAllQuestions() {
    const cards = document.querySelectorAll('.question-card[data-converted]');
    let content = 'AWS SAA 기출문제 모음\n';
    content += '='.repeat(50) + '\n\n';
    
    cards.forEach((card, index) => {
      const numEl = card.querySelector('.question-number');
      const numMatch = numEl?.textContent.match(/문제\s*(\d+)/);
      const questionNum = numMatch ? parseInt(numMatch[1]) : index + 1;
      
      const questionText = card.querySelector('.question-text')?.textContent || '';
      const topic = card.dataset.topic || '';
      const options = Array.from(card.querySelectorAll('.option-text')).map(opt => opt.textContent).join('\n');
      const answer = card.dataset.answer || '';
      const explanation = card.querySelector('.answer-explanation')?.textContent || '';
      
      content += `문제 ${questionNum}\n`;
      content += `주제: ${topic}\n\n`;
      content += `${questionText}\n\n`;
      content += `선택지:\n${options}\n\n`;
      content += `정답: ${answer}\n\n`;
      content += `해설:\n${explanation}\n\n`;
      content += '-'.repeat(50) + '\n\n';
    });
    
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AWS-SAA-기출문제-전체.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // 통계 업데이트
  function updateStats() {
    const progressCount = document.getElementById('progress-count');
    const accuracyRate = document.getElementById('accuracy-rate');
    
    if (progressCount) {
      progressCount.textContent = state.stats.answered;
    }
    
    if (accuracyRate) {
      const rate = state.stats.answered > 0 
        ? Math.round((state.stats.correct / state.stats.answered) * 100)
        : 0;
      accuracyRate.textContent = `${rate}%`;
    }
  }

  // 모든 답안 초기화
  function resetAllAnswers() {
    if (!confirm('모든 답안을 초기화하시겠습니까?')) {
      return;
    }
    
    state.answers = {};
    state.checked = {};
    state.stats.answered = 0;
    state.stats.correct = 0;
    
    // 라디오 버튼 초기화
    document.querySelectorAll('.option-radio').forEach(radio => {
      radio.checked = false;
      const label = radio.closest('.option-label');
      label.classList.remove('selected', 'correct', 'incorrect');
    });
    
    // 상태 아이콘 초기화
    document.querySelectorAll('.question-status').forEach(status => {
      status.innerHTML = '';
    });
    
    // 정답 영역 숨기기
    document.querySelectorAll('.question-answer').forEach(answer => {
      answer.hidden = true;
      answer.classList.remove('show');
    });
    
    // 해설 버튼 초기화
    document.querySelectorAll('.explanation-toggle').forEach(button => {
      button.setAttribute('aria-expanded', 'false');
      const textSpan = button.querySelector('.explanation-text');
      if (textSpan) {
        textSpan.textContent = '해설 보기';
      }
    });
    
    updateStats();
    localStorage.removeItem('aws-saa-answers');
    localStorage.removeItem('aws-saa-checked');
  }

  // 답안 저장
  function saveAnswers() {
    try {
      localStorage.setItem('aws-saa-answers', JSON.stringify(state.answers));
      localStorage.setItem('aws-saa-checked', JSON.stringify(state.checked));
      localStorage.setItem('aws-saa-stats', JSON.stringify(state.stats));
    } catch (e) {
      console.warn('답안 저장 실패:', e);
    }
  }

  // 저장된 답안 불러오기
  function loadSavedAnswers() {
    try {
      const savedAnswers = localStorage.getItem('aws-saa-answers');
      const savedChecked = localStorage.getItem('aws-saa-checked');
      const savedStats = localStorage.getItem('aws-saa-stats');
      
      if (savedAnswers) {
        state.answers = JSON.parse(savedAnswers);
      }
      if (savedChecked) {
        state.checked = JSON.parse(savedChecked);
      }
      if (savedStats) {
        state.stats = { ...state.stats, ...JSON.parse(savedStats) };
      }
      
      // 저장된 답안 복원
      Object.keys(state.answers).forEach(questionId => {
        const radio = document.querySelector(`input[name="question-${questionId}"][value="${state.answers[questionId]}"]`);
        if (radio) {
          radio.checked = true;
          updateQuestionStatus(questionId);
        }
      });
      
      // 체크된 문제 복원
      Object.keys(state.checked).forEach(questionId => {
        if (state.checked[questionId]) {
          const cards = document.querySelectorAll('.question-card[data-converted]');
          for (let card of cards) {
            const numEl = card.querySelector('.question-number');
            if (numEl) {
              const numMatch = numEl.textContent.match(/문제\s*(\d+)/);
              if (numMatch && parseInt(numMatch[1]) === parseInt(questionId)) {
                const correctAnswer = card.dataset.answer;
                const userAnswer = state.answers[questionId];
                const isCorrect = userAnswer === correctAnswer;
                updateQuestionStatus(questionId, isCorrect);
                
                const answerDiv = card.querySelector(`#answer-${questionId}`);
                if (answerDiv) {
                  answerDiv.hidden = false;
                  answerDiv.classList.add('show');
                }
                break;
              }
            }
          }
        }
      });
      
      updateStats();
    } catch (e) {
      console.warn('답안 불러오기 실패:', e);
    }
  }

  // DOMContentLoaded 또는 즉시 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
