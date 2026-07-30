// Progressive enhancement only: the site reads fine with this file blocked.
// Theme bootstrap runs inline in <head>; this handles the toggle and the
// copy-to-clipboard buttons on code blocks.
(function () {
  "use strict";

  var root = document.documentElement;

  function currentTheme() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function applyTheme(theme, button) {
    if (theme === "light") {
      root.setAttribute("data-theme", "light");
    } else {
      root.removeAttribute("data-theme");
    }
    if (button) {
      button.setAttribute(
        "aria-label",
        theme === "light" ? "Switch to dark theme" : "Switch to light theme"
      );
    }
  }

  function initThemeToggle() {
    var button = document.querySelector(".theme-toggle");
    if (!button) return;

    applyTheme(currentTheme(), button);

    button.addEventListener("click", function () {
      var next = currentTheme() === "light" ? "dark" : "light";
      applyTheme(next, button);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
    });
  }

  var COPY_ICON =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
    '<rect x="9" y="9" width="13" height="13" rx="2"></rect>' +
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

  function initCopyButtons() {
    if (!navigator.clipboard) return;

    var blocks = document.querySelectorAll(".post-content pre");
    Array.prototype.forEach.call(blocks, function (pre) {
      // Hugo wraps highlighted code in .highlight; plain fences get no wrapper.
      var parent = pre.parentElement;
      var container;
      if (parent && parent.classList.contains("highlight")) {
        container = parent;
      } else {
        container = document.createElement("div");
        pre.parentNode.insertBefore(container, pre);
        container.appendChild(pre);
      }
      container.classList.add("code-block");

      var button = document.createElement("button");
      button.type = "button";
      button.className = "copy-btn";
      button.setAttribute("aria-label", "Copy code to clipboard");
      button.innerHTML = COPY_ICON;

      button.addEventListener("click", function () {
        var code = pre.querySelector("code") || pre;
        navigator.clipboard.writeText(code.innerText.replace(/\n$/, "")).then(
          function () {
            button.dataset.copied = "true";
            button.textContent = "Copied";
            setTimeout(function () {
              delete button.dataset.copied;
              button.innerHTML = COPY_ICON;
            }, 1600);
          },
          function () {
            button.textContent = "Failed";
            setTimeout(function () {
              button.innerHTML = COPY_ICON;
            }, 1600);
          }
        );
      });

      container.appendChild(button);
    });
  }

  initThemeToggle();
  initCopyButtons();
})();
