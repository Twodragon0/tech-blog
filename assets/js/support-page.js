(function () {
  'use strict';

  var newsletterForm = document.querySelector('.newsletter-form');
  if (!newsletterForm) {
    return;
  }

  var successMsg = document.createElement('div');
  successMsg.className = 'success-message';
  successMsg.textContent = '✅ 구독이 완료되었습니다! 확인 이메일을 확인해주세요.';

  var errorMsg = document.createElement('div');
  errorMsg.className = 'error-message';
  errorMsg.textContent = '❌ 구독 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';

  newsletterForm.appendChild(successMsg);
  newsletterForm.appendChild(errorMsg);

  newsletterForm.addEventListener('submit', function (event) {
    var emailInput = newsletterForm.querySelector('input[type="email"]');
    var submitButton = newsletterForm.querySelector('button[type="submit"]');

    if (!emailInput.value || !emailInput.validity.valid) {
      event.preventDefault();
      errorMsg.style.display = 'block';
      successMsg.style.display = 'none';
      setTimeout(function () {
        errorMsg.style.display = 'none';
      }, 5000);
      return false;
    }

    window.open('https://buttondown.com/twodragon', 'popupwindow');

    newsletterForm.classList.add('loading');
    submitButton.disabled = true;
    errorMsg.style.display = 'none';
    successMsg.style.display = 'none';

    setTimeout(function () {
      newsletterForm.classList.remove('loading');
      submitButton.disabled = false;

      var checkPopup = setInterval(function () {
        try {
          if (window.open('', 'popupwindow').closed === false) {
            clearInterval(checkPopup);
            successMsg.style.display = 'block';
            emailInput.value = '';
          }
        } catch (_error) {
          clearInterval(checkPopup);
        }
      }, 100);

      setTimeout(function () {
        clearInterval(checkPopup);
      }, 3000);
    }, 1000);

    return true;
  });

  var emailInput = newsletterForm.querySelector('input[type="email"]');
  if (emailInput) {
    emailInput.addEventListener('focus', function () {
      errorMsg.style.display = 'none';
      successMsg.style.display = 'none';
    });
  }

  var buyMeCoffeeBtn = document.getElementById('buyme-coffee-btn');
  if (buyMeCoffeeBtn) {
    buyMeCoffeeBtn.addEventListener('click', function (event) {
      event.preventDefault();
      alert('Buy Me a Coffee 계정을 만들고 링크를 설정해주세요. buymeacoffee.com');
    });
  }
})();
