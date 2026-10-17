"use strict";

// Render SVG sources to 2x PNG exports using an installed Electron runtime.
const { app, BrowserWindow, session } = require("electron");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const scratch = path.join(root, "Temp", "chart-review");
fs.mkdirSync(scratch, { recursive: true });
app.disableHardwareAcceleration();
app.setPath("userData", path.join(scratch, "renderer-profile"));

app.whenReady().then(async () => {
  session.defaultSession.webRequest.onBeforeRequest({ urls: ["http://*/*", "https://*/*"] }, (_details, done) => done({ cancel: true }));
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, "chart-manifest.json")));
  const win = new BrowserWindow({ width: 1200, height: 760, show: false, webPreferences: { backgroundThrottling: false, nodeIntegration: false, contextIsolation: true } });
  const report = [];
  for (const { name, height } of manifest) {
    for (const variant of ["", ".light"]) {
      const source = path.join(root, "static", "img", "posts", name + variant + ".svg");
      const markup = fs.readFileSync(source, "utf8");
      await win.loadURL("data:text/html;charset=utf-8," + encodeURIComponent("<style>body{margin:0}</style>" + markup));
      await win.webContents.executeJavaScript("document.fonts.ready");
      const overflow = await win.webContents.executeJavaScript(`Array.from(document.querySelectorAll('text')).map(t=>{const b=t.getBBox();return {text:t.textContent,x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height}}).filter(b=>b.x<0||b.y<0||b.right>1200||b.bottom>${height})`);
      if (overflow.length) throw new Error(name + ": text outside canvas " + JSON.stringify(overflow));
      const png = await win.webContents.executeJavaScript(`(async()=>{const blob=new Blob([${JSON.stringify(markup)}],{type:'image/svg+xml'});const url=URL.createObjectURL(blob);const img=new Image();img.src=url;await img.decode();const c=document.createElement('canvas');c.width=2400;c.height=${height * 2};c.getContext('2d').drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(url);return c.toDataURL('image/png').split(',')[1]})()`);
      // WHY: only dark exports are social assets. Light previews stay local.
      const destination = variant ? path.join(scratch, name + variant + ".png") : source.replace(/\.svg$/, ".png");
      fs.mkdirSync(path.dirname(destination), { recursive: true });
      fs.writeFileSync(destination, Buffer.from(png, "base64"));
      report.push({ name, variant, width: 2400, height: height * 2, overflow });
      console.log("Rendered " + name + variant);
    }
  }
  fs.writeFileSync(path.join(scratch, "render-check.json"), JSON.stringify(report, null, 2));
  win.destroy();
  app.quit();
}).catch(error => { console.error(error); app.exit(1); });
