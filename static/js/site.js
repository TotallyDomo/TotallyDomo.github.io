(function () {
  "use strict";

  var root = document.documentElement;
  var themeCharts = [];

  // INVARIANT: remap neutral labels and grids only; preserve data colors and alpha.
  var lightChartPalette = {
    0xe6edf3: 0x1f2328,
    0x8b98a9: 0x59636e,
    0x2a313c: 0xd1d9e0
  };

  function recolorChartPixels(pixels) {
    for (var i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] === 0) continue;
      var color = (pixels[i] << 16) | (pixels[i + 1] << 8) | pixels[i + 2];
      var replacement = lightChartPalette[color];
      // WHY: canvas alpha round-trips can shift antialiased RGB by a few levels.
      if (replacement === undefined && pixels[i + 3] >= 16 && pixels[i + 3] < 255) {
        var tolerance = Math.ceil(127.5 / pixels[i + 3] + 0.5);
        for (var candidate in lightChartPalette) {
          if (Math.abs(pixels[i] - ((candidate >> 16) & 255)) <= tolerance &&
              Math.abs(pixels[i + 1] - ((candidate >> 8) & 255)) <= tolerance &&
              Math.abs(pixels[i + 2] - (candidate & 255)) <= tolerance) {
            replacement = lightChartPalette[candidate];
            break;
          }
        }
      }
      if (replacement === undefined) continue;
      pixels[i] = (replacement >> 16) & 255;
      pixels[i + 1] = (replacement >> 8) & 255;
      pixels[i + 2] = replacement & 255;
    }
  }

  function updateChartTheme(chart) {
    var source = currentTheme() === "light" && chart.lightSource
      ? chart.lightSource
      : chart.darkSource;
    if (chart.image.getAttribute("src") !== source) {
      chart.image.setAttribute("src", source);
    }
  }

  function prepareChartTheme(chart) {
    var image = chart.image;
    if (chart.lightSource || chart.failed || !image.complete || !image.naturalWidth) return;
    try {
      var canvas = document.createElement("canvas");
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      var context = canvas.getContext("2d", { willReadFrequently: true });
      if (!context) throw new Error("Canvas image processing is unavailable");
      context.drawImage(image, 0, 0);
      var pixels = context.getImageData(0, 0, canvas.width, canvas.height);
      recolorChartPixels(pixels.data);
      context.putImageData(pixels, 0, 0);
      chart.lightSource = canvas.toDataURL("image/png");
      image.classList.remove("theme-chart-fallback");
      updateChartTheme(chart);
    } catch (error) {
      chart.failed = true;
      console.warn("Could not adapt chart colors to the site theme:", chart.darkSource, error);
    }
  }

  function initThemeCharts() {
    Array.prototype.forEach.call(document.querySelectorAll("img[data-theme-chart]"), function (image) {
      var chart = { image: image, darkSource: image.getAttribute("src"), lightSource: null, failed: false };
      themeCharts.push(chart);
      image.addEventListener("load", function () { prepareChartTheme(chart); });
      prepareChartTheme(chart);
    });
  }

  function currentTheme() {
    return root.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function applyTheme(theme, button) {
    if (theme === "light") {
      root.setAttribute("data-theme", "light");
    } else {
      root.removeAttribute("data-theme");
    }
    themeCharts.forEach(updateChartTheme);
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

  initThemeCharts();
  initThemeToggle();
  initCopyButtons();
})();
