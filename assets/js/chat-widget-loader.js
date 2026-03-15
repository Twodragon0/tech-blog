(function () {
  'use strict';

  var script = document.currentScript;
  var widgetSrc = (script && script.getAttribute('data-chat-src')) || '/assets/js/chat-widget.js';
  var chatWidgetLoaded = false;
  var chatToggle = document.getElementById('chat-widget-toggle');

  if (!chatToggle) {
    return;
  }

  function loadChatWidget() {
    if (chatWidgetLoaded) {
      return;
    }

    chatWidgetLoaded = true;

    var purifyScript = document.createElement('script');
    purifyScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.4/purify.min.js';
    purifyScript.integrity = 'sha384-eEu5CTj3qGvu9PdJuS+YlkNi7d2XxQROAFYOr59zgObtlcux1ae1Il3u7jvdCSWu';
    purifyScript.crossOrigin = 'anonymous';
    document.head.appendChild(purifyScript);

    var node = document.createElement('script');
    node.src = widgetSrc;
    node.defer = true;
    node.onload = function () {
      chatToggle.click();
    };
    node.onerror = function () {
      chatWidgetLoaded = false;
    };
    document.body.appendChild(node);
  }

  chatToggle.addEventListener('click', loadChatWidget, { once: true, passive: true });
})();
