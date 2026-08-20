(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  function el(n, a, t) { const e = document.createElementNS(NS, n); for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]); if (t != null) e.textContent = t; return e; }

  /* ===== STEP 1 アニメーション ===== */
  const FPSLIST = [1, 2, 5, 8, 12, 24, 30, 60];
  let fps = 12, running = true, ball1 = null, ball2 = null, cap = null, W = 480, H = 190, PAD = 30;
  function buildAnim() {
    const svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'フレームレートの比較アニメーション' });
    [58, 132].forEach(y => svg.appendChild(el('line', { x1: PAD, y1: y, x2: W - PAD, y2: y, class: 'track' })));
    svg.appendChild(el('text', { x: PAD, y: 30, class: 'lab' }, '選んだフレームレート'));
    svg.appendChild(el('text', { x: PAD, y: 104, class: 'lab' }, '参考：なめらかな動き（60fps）'));
    cap = el('text', { x: W - PAD, y: 30, class: 'lab', 'text-anchor': 'end' });
    svg.appendChild(cap);
    ball1 = el('circle', { cx: PAD, cy: 58, r: 11, class: 'ball' });
    ball2 = el('circle', { cx: PAD, cy: 132, r: 11, class: 'ball2' });
    svg.appendChild(ball1); svg.appendChild(ball2);
    const box = $('animBox'); box.innerHTML = ''; box.appendChild(svg);
  }
  const posAt = ms => {                                   // 2秒で往復
    const p = (ms % 2400) / 2400;
    const u = p < 0.5 ? p * 2 : (1 - p) * 2;
    return PAD + u * (W - 2 * PAD);
  };
  let base = null;
  function tick(now) {
    if (base === null) base = now;
    if (running) {
      const t = now - base;
      const step = 1000 / fps;
      const tq = Math.floor(t / step) * step;             // 選んだfpsで止まった時刻
      ball1.setAttribute('cx', posAt(tq));
      ball2.setAttribute('cx', posAt(t));
      cap.textContent = fps + ' fps（' + (Math.round(1000 / fps * 10) / 10) + ' ミリ秒ごとに1枚）';
    }
    requestAnimationFrame(tick);
  }
  function drawFpsBtns() {
    $('fpsBtns').innerHTML = FPSLIST.map(f =>
      '<button class="btn' + (f === fps ? ' on' : '') + '" data-f="' + f + '">' + f + ' fps</button>').join('');
    $('fpsBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      fps = +b.dataset.f; drawFpsBtns(); noteFps();
    }));
  }
  function noteFps() {
    const n = $('animNote');
    n.className = 'note ' + (fps >= 24 ? 'ok' : 'warn');
    n.innerHTML = fps >= 30 ? '<strong>' + fps + 'fps</strong>：ほとんど連続した動きに見えます。スポーツ中継やゲームでよく使われます。'
      : fps >= 24 ? '<strong>24fps</strong>：映画でよく使われる値です。自然な動きに見えますが、速い動きでは少しカクつきます。'
      : fps >= 8 ? '<strong>' + fps + 'fps</strong>：動いては見えますが、カクカクします。1枚あたり ' + (Math.round(1000 / fps)) + ' ミリ秒も止まっているためです。'
      : '<strong>' + fps + 'fps</strong>：ぱらぱら漫画のようです。フレームレートが小さいほどデータ量は減りますが、なめらかさは失われます。';
  }

  /* ===== STEP 2 ===== */
  function drawFps2() {
    const a = (+$('fA').value) / (+$('sA').value || 1), b = (+$('fB').value) / (+$('sB').value || 1);
    $('fpsA').textContent = (Math.round(a * 100) / 100) + ' fps';
    $('fpsB').textContent = (Math.round(b * 100) / 100) + ' fps';
    const n = $('fpsNote');
    const book = +$('fA').value === 1440 && +$('sA').value === 60 && +$('fB').value === 900 && +$('sB').value === 30;
    n.className = 'note ' + (book ? 'ok' : 'info');
    n.innerHTML = (book ? '本文の条件です。1440÷60＝<strong>24fps</strong>、900÷30＝<strong>30fps</strong>。' : '') +
      (Math.abs(a - b) < 1e-9 ? '2つのフレームレートは同じです。'
        : '<strong>動画' + (a > b ? 'A' : 'B') + '</strong>のほうがフレームレートが大きく、なめらかに見えます。' +
          (book ? '<br>本文の選択肢⓪は「動画Aのほうが大きい」としているので<strong>誤り</strong>です。' : ''));
  }

  /* ===== STEP 3 ===== */
  function fmtBytes(b) {
    if (b >= 1e9) return (Math.round(b / 1e9 * 100) / 100) + ' GB';
    if (b >= 1e6) return (Math.round(b / 1e6 * 100) / 100) + ' MB';
    if (b >= 1e3) return (Math.round(b / 1e3 * 10) / 10) + ' kB';
    return Math.round(b) + ' B';
  }
  const ABC = [
    { k: 'A', w: 2560, h: 1440, b: 8, f: 24, d: '256階調グレースケール' },
    { k: 'B', w: 1920, h: 1080, b: 24, f: 30, d: 'RGB各8ビットカラー' },
    { k: 'C', w: 3840, h: 2160, b: 24, f: 30, d: '24ビットフルカラー' }
  ];
  function drawVid() {
    const w = +$('vw').value || 0, h = +$('vh').value || 0, b = +$('vb').value, f = +$('vf').value || 0, s = +$('vs').value || 0;
    const frameBits = w * h * b, bits = frameBits * f * s, bytes = bits / 8;
    $('vEq').innerHTML = '1フレーム ＝ ' + w.toLocaleString() + ' × ' + h.toLocaleString() + ' × ' + b + '（ビット） ＝ ' +
      (frameBits / 8).toLocaleString() + '（バイト）<br>' +
      (frameBits / 8).toLocaleString() + ' × ' + f + '（fps）' + (s === 1 ? '' : ' × ' + s + '（秒）') + '<br>＝ ' + (bytes).toLocaleString() + '（バイト）';
    $('vSize').textContent = fmtBytes(bytes);
    $('vFrame').textContent = fmtBytes(frameBits / 8);
    const n = $('vNote');
    n.innerHTML = '1画素 ' + b + 'ビット ＝ ' + (b / 8) + 'バイト。' +
      '解像度を縦横それぞれ2倍にするとデータ量は<strong>4倍</strong>、フレームレートを2倍にすると<strong>2倍</strong>になります。';
    const rows = ABC.map(x => ({ ...x, bytes: x.w * x.h * x.b / 8 * x.f }));
    const sorted = rows.slice().sort((p, q) => p.bytes - q.bytes);
    $('abcTable').innerHTML = '<thead><tr><th></th><th>1画素</th><th>解像度</th><th>fps</th><th>1秒あたりのデータ量</th></tr></thead><tbody>' +
      rows.map(x => '<tr><td><strong>' + x.k + '</strong><br><span class="small">' + x.d + '</span></td>' +
        '<td class="mono">' + (x.b / 8) + ' B</td><td class="mono">' + x.w + '×' + x.h + '</td><td class="mono">' + x.f + '</td>' +
        '<td class="mono">' + x.bytes.toLocaleString() + ' B<br><span class="small">（' + fmtBytes(x.bytes) + '）</span></td></tr>').join('') + '</tbody>';
    $('abcNote').innerHTML = '小さい順に並べると <strong>' + sorted.map(x => x.k).join(' ＜ ') + '</strong>。' +
      'Cは解像度がAの2倍以上・カラーで、1秒あたり約746MBにもなります。だから動画には圧縮が欠かせません。';
  }

  /* ===== STEP 4 ===== */
  const Q1 = [
    { c: '総再生時間が1分、総フレーム数が1440である動画Aと、総再生時間が30秒、総フレーム数が900である動画Bを比べると、動画Aのほうがフレームレートは大きく、より滑らかな動きを実現できる。', ok: false,
      why: 'A＝1440÷60＝24fps、B＝900÷30＝30fps。<strong>Bのほうが大きい</strong>ので誤りです（STEP 2 で確かめられます）。' },
    { c: '動画は少しずつ異なる静止画像を短い時間間隔で連続して表示させることで、あたかも動いているように見せたものである。', ok: true,
      why: '人間の目の<strong>残像現象</strong>を利用しています。STEP 1 で体験したとおりです。' },
    { c: '動画は大量の静止画像の集まりであるから、データ量が大きいが、インターネットの動画配信サービスでは画質を劣化させないために、圧縮技術を活用せずに配信している。', ok: false,
      why: '実際には<strong>圧縮技術を使って</strong>データ量を小さくして配信しています。STEP 3 のとおり、無圧縮では1秒で数百MBにもなり、とても配信できません。' },
    { c: '動画を撮影するとき、解像度とフレームレートの設定が同じであれば、1秒間撮影した動画と30秒間撮影した動画のデータ量は変わらない。', ok: false,
      why: 'データ量は<strong>時間にも比例</strong>します。30秒撮れば30倍です。' }
  ];
  function drawQ1() {
    const box = $('q1Choices'); box.innerHTML = '';
    Q1.forEach((q, i) => {
      const b = document.createElement('button');
      b.className = 'btn'; b.style.textAlign = 'left'; b.dataset.i = i;
      b.textContent = '⓪①②③'[i] + '　' + q.c;
      b.addEventListener('click', () => {
        box.classList.add('locked');
        [...box.children].forEach(x => { if (Q1[+x.dataset.i].ok) x.classList.add('correct'); else if (x === b) x.classList.add('wrong'); });
        const fb = $('q1Fb'); fb.hidden = false; fb.className = 'note ' + (q.ok ? 'ok' : 'ng');
        fb.innerHTML = (q.ok ? '正解（①）。' : '正解は <strong>①</strong>。') + q.why;
      });
      box.appendChild(b);
    });
  }

  /* ===== STEP 5 ===== */
  const Q2 = ['A＜B＜C', 'A＜C＜B', 'B＜A＜C', 'B＜C＜A', 'C＜A＜B', 'C＜B＜A'];
  function drawQ2() {
    const box = $('q2Choices'); box.innerHTML = '';
    Q2.forEach((c, i) => {
      const b = document.createElement('button');
      b.className = 'btn'; b.style.textAlign = 'center'; b.dataset.c = c;
      b.textContent = '⓪①②③④⑤'[i] + '　' + c;
      b.addEventListener('click', () => {
        const ok = c === 'A＜B＜C';
        box.classList.add('locked');
        [...box.children].forEach(x => { if (x.dataset.c === 'A＜B＜C') x.classList.add('correct'); else if (x === b) x.classList.add('wrong'); });
        const fb = $('q2Fb'); fb.hidden = false; fb.className = 'note ' + (ok ? 'ok' : 'ng');
        fb.innerHTML = (ok ? '正解（⓪）。' : '正解は <strong>⓪　A＜B＜C</strong>。') +
          'A＝88,473,600B、B＝186,624,000B、C＝746,496,000B。' +
          'Aはグレースケールで1画素1バイトしか使わないため、解像度は大きくても最小になります。STEP 3 の表で確かめましょう。';
      });
      box.appendChild(b);
    });
  }

  function init() {
    buildAnim(); drawFpsBtns(); noteFps();
    $('playBtn').addEventListener('click', () => {
      running = !running;
      $('playBtn').textContent = running ? '一時停止' : '動かす';
      if (running) base = null;
    });
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      running = false; $('playBtn').textContent = '動かす';
    }
    requestAnimationFrame(tick);
    ['fA', 'sA', 'fB', 'sB'].forEach(i => $(i).addEventListener('input', drawFps2));
    ['vw', 'vh', 'vf', 'vs'].forEach(i => $(i).addEventListener('input', drawVid));
    $('vb').addEventListener('change', drawVid);
    window.Terms.glossary($('glossBox'), ['フレーム', 'フレームレート', '残像現象', '解像度', '階調', 'フルカラー', '圧縮', 'ビット']);
    drawFps2(); drawVid(); drawQ1(); drawQ2();
    window.Terms.attach();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
