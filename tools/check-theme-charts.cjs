"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../static/js/site.js"), "utf8");
const original = [
  230, 237, 243, 255,
  230, 237, 243, 128,
  229, 237, 243, 128,
  232, 239, 247, 32,
  139, 152, 169, 255,
  42, 49, 60, 255,
  76, 141, 255, 255,
  222, 116, 34, 255,
  245, 248, 252, 255,
  247, 247, 255, 32,
  13, 17, 23, 255,
  230, 237, 243, 0
];
const expected = [
  31, 35, 40, 255,
  31, 35, 40, 128,
  31, 35, 40, 128,
  31, 35, 40, 32,
  89, 99, 110, 255,
  209, 217, 224, 255,
  76, 141, 255, 255,
  222, 116, 34, 255,
  245, 248, 252, 255,
  247, 247, 255, 32,
  13, 17, 23, 255,
  230, 237, 243, 0
];

function element(attributes = {}) {
  const listeners = {};
  const classes = new Set();
  return {
    attributes, listeners,
    classList: { add: value => classes.add(value), remove: value => classes.delete(value), contains: value => classes.has(value) },
    getAttribute: name => attributes[name] === undefined ? null : attributes[name],
    setAttribute: (name, value) => { attributes[name] = value; },
    removeAttribute: name => { delete attributes[name]; },
    addEventListener: (name, listener) => { listeners[name] = listener; }
  };
}

function scene(initialTheme, lazy = false, failCanvas = false) {
  const root = element(initialTheme === "light" ? { "data-theme": "light" } : {});
  const button = element();
  const image = element({ src: "/img/chart.png" });
  image.classList.add("theme-chart-fallback");
  image.complete = !lazy;
  image.naturalWidth = lazy ? 0 : original.length / 4;
  image.naturalHeight = 1;
  const screenshot = element({ src: "/img/screenshot.png" });
  const rendered = [];
  const warnings = [];
  const stored = {};
  let canvasCount = 0;
  const document = {
    documentElement: root,
    querySelector: selector => selector === ".theme-toggle" ? button : null,
    querySelectorAll: selector => selector === "img[data-theme-chart]" ? [image] : [],
    createElement: tag => {
      assert.equal(tag, "canvas");
      canvasCount++;
      let pixels;
      return {
        getContext: () => {
          if (failCanvas) throw new Error("Canvas unavailable");
          return {
            drawImage: candidate => { assert.equal(candidate, image); },
            getImageData: () => ({ data: new Uint8ClampedArray(original) }),
            putImageData: value => { pixels = Array.from(value.data); }
          };
        },
        toDataURL: type => {
          assert.equal(type, "image/png");
          rendered.push(pixels);
          return "data:image/png;test-render";
        }
      };
    }
  };
  vm.runInNewContext(source, {
    document, navigator: {}, Uint8ClampedArray,
    localStorage: { setItem: (key, value) => { stored[key] = value; } },
    console: { warn: (...args) => warnings.push(args) },
    setTimeout
  });
  return { root, button, image, screenshot, rendered, warnings, stored, canvases: () => canvasCount };
}

const dark = scene("dark");
assert.deepEqual(dark.rendered, [expected]);
assert.equal(dark.image.getAttribute("src"), "/img/chart.png");
assert.equal(dark.screenshot.getAttribute("src"), "/img/screenshot.png");
dark.button.listeners.click();
assert.equal(dark.root.getAttribute("data-theme"), "light");
assert.equal(dark.image.getAttribute("src"), "data:image/png;test-render");
assert.equal(dark.stored.theme, "light");
assert.equal(dark.button.getAttribute("aria-label"), "Switch to dark theme");
dark.image.listeners.load();
dark.button.listeners.click();
assert.equal(dark.image.getAttribute("src"), "/img/chart.png");
assert.equal(dark.root.getAttribute("data-theme"), null);
assert.equal(dark.canvases(), 1);

const light = scene("light");
assert.equal(light.image.getAttribute("src"), "data:image/png;test-render");
assert.equal(light.image.classList.contains("theme-chart-fallback"), false);

const lazy = scene("dark", true);
lazy.button.listeners.click();
assert.equal(lazy.canvases(), 0);
lazy.image.complete = true;
lazy.image.naturalWidth = original.length / 4;
lazy.image.listeners.load();
assert.equal(lazy.image.getAttribute("src"), "data:image/png;test-render");
assert.deepEqual(lazy.rendered, [expected]);

const failed = scene("light", false, true);
assert.equal(failed.image.getAttribute("src"), "/img/chart.png");
assert.equal(failed.image.classList.contains("theme-chart-fallback"), true);
assert.equal(failed.warnings.length, 1);
failed.image.listeners.load();
assert.equal(failed.warnings.length, 1);

console.log("Theme charts passed: initial themes, both toggle directions, lazy loads, cached rendering, fixed bar labels, alpha/data colors, and readable failure fallback.");
