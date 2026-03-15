(function () {
  var btn = document.getElementById('custom-feedback-btn');
  if (!btn) {
    return;
  }

  btn.addEventListener('click', function () {
    window.open('https://github.com/Twodragon0/tech-blog/issues/new', '_blank');
  });
})();
