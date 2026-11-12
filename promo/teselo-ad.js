/* Teselo playable promo for the house-ad card (build.py house_ads, data-k="teselo"): a one-move block puzzle. Drag or
   tap the piece into the gap, two rows clear (combo), the fox cheers; the whole card links to the Teselo landing.
   Plain canvas. It paints only while the card is on screen, at 30 fps when nothing moves, stops after 20 s idle, never
   creates gradients per frame (they stall Chrome's GPU cache) and never shrinks a sprite more than 2x. */
(function () {
  'use strict';
  if (window.__tslAd) return; window.__tslAd = 1;
  var reduce = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var PAL = {t:['#8fe3d5','#2a9d8f','#1c7064'], y:['#fede95','#e9a72f','#b07614'], p:['#f9b0ca','#d9577f','#a6355a'],
             o:['#fdb592','#e2683d','#ad4620'], b:['#bed3f6','#5f86cf','#3d5d9c']};
  var KEYS = ['t','y','p','o','b'], INK = '#3a2418';
  var me = document.currentScript, base = me && me.src ? me.src.replace(/[^\/]*$/, '') : '/promo/';
  var fox = new Image(); fox.src = base + 'teselo-fox.webp';

  function clamp(v,a,b){ return v < a ? a : v > b ? b : v; }
  function lerp(a,b,t){ return a + (b - a)*t; }
  function eOut(t){ t = clamp(t,0,1); return 1 - Math.pow(1 - t, 3); }
  function eIn(t){ t = clamp(t,0,1); return t*t; }
  function eIO(t){ t = clamp(t,0,1); return t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3)/2; }
  function eBack(t){ t = clamp(t,0,1); var c = 1.7; return 1 + (c + 1)*Math.pow(t - 1, 3) + c*Math.pow(t - 1, 2); }
  function rnd(a){ return a[(Math.random()*a.length)|0]; }
  function mk(w,h){ var c = document.createElement('canvas'); c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h)); return c; }
  function rr(o,x,y,w,h,r){
    w = Math.max(0.01, w); h = Math.max(0.01, h); r = Math.max(0, Math.min(r, w/2, h/2)); o.beginPath();
    if (o.roundRect) o.roundRect(x,y,w,h,r);
    else { o.moveTo(x+r,y); o.arcTo(x+w,y,x+w,y+h,r); o.arcTo(x+w,y+h,x,y+h,r); o.arcTo(x,y+h,x,y,r); o.arcTo(x,y,x+w,y,r); o.closePath(); }
  }
  function blockSprite(k,s){
    var p = PAL[k], c = mk(s,s), o = c.getContext('2d'), r = s*0.24;
    o.fillStyle = p[2]; rr(o,0,0,s,s,r); o.fill();
    var g = o.createLinearGradient(0,0,0,s*0.9); g.addColorStop(0,p[0]); g.addColorStop(1,p[1]); o.fillStyle = g; rr(o,0,0,s,s*0.9,r); o.fill();
    o.save(); rr(o,0,0,s,s*0.9,r); o.clip();
    var rg = o.createRadialGradient(s*0.28,s*0.16,0,s*0.28,s*0.16,s*0.8); rg.addColorStop(0,'rgba(255,255,255,.38)'); rg.addColorStop(1,'rgba(255,255,255,0)');
    o.fillStyle = rg; o.fillRect(0,0,s,s); o.restore();
    o.strokeStyle = 'rgba(255,255,255,.28)'; o.lineWidth = Math.max(1, s*0.022); rr(o,s*0.03,s*0.03,s*0.94,s*0.83,r*0.9); o.stroke();
    o.save(); o.translate(s*0.33,s*0.21); o.rotate(-0.38); o.scale(1,0.5);
    var gg = o.createRadialGradient(0,0,0,0,0,s*0.17); gg.addColorStop(0,'rgba(255,255,255,.95)'); gg.addColorStop(0.55,'rgba(255,255,255,.7)'); gg.addColorStop(1,'rgba(255,255,255,0)');
    o.fillStyle = gg; o.beginPath(); o.arc(0,0,s*0.17,0,Math.PI*2); o.fill(); o.restore();
    return c;
  }
  function radial(sz,stops){ var c = mk(sz,sz), o = c.getContext('2d'), g = o.createRadialGradient(sz/2,sz/2,0,sz/2,sz/2,sz/2);
    stops.forEach(function(s){ g.addColorStop(s[0],s[1]); }); o.fillStyle = g; o.fillRect(0,0,sz,sz); return c; }

  function Ad(card){
    var a = card.querySelector('.tsl-a'), cv = card.querySelector('.tsl-c');
    if (!a || !cv || !cv.getContext) return;
    var x = cv.getContext('2d');
    a.setAttribute('draggable', 'false');
    var grab = document.createElement('span'), gs = grab.style;
    gs.position = 'absolute'; gs.zIndex = '2'; gs.touchAction = 'none'; gs.cursor = 'grab'; gs.borderRadius = '16px';
    grab.setAttribute('aria-hidden', 'true'); a.appendChild(grab);
    var TX = {cta:card.getAttribute('data-cta') || 'Jugar gratis', hook:card.getAttribute('data-hook') || '¿Encaja?',
              combo:card.getAttribute('data-combo') || '¡Combo ×2!', more:card.getAttribute('data-more') || '300 niveles más'};
    var FONT = getComputedStyle(card).fontFamily || 'system-ui, sans-serif';
    var W = 0, H = 0, DPR = 1, L = {}, SP = {}, R = 3, C = 8;
    var board = [], drop = {}, ghosts = [], parts = [], gap = {r:1, c:3}, pk = 'p';
    var phase = 'rain', pieceBorn = 0, drag = null, fly = null, ret = null, demo = null;
    var winT = -1e9, demos = 0, now = 0, lastAct = -1e9, readyT = 0, visible = false, raf = 0, hover = false, odd = false, startT = null;

    function cellXY(i){ return [L.bx + (i%C)*L.cell + L.cell/2, L.by + ((i/C)|0)*L.cell + L.cell/2]; }
    function gapCenter(){ return [L.bx + (gap.c + 1)*L.cell, L.by + (gap.r + 1)*L.cell]; }
    function lvl(px){ var d = px*DPR; return d > SP.lv[1]*1.05 ? '' : d > SP.lv[2]*1.05 ? '1' : '2'; }
    function blk(cx,cy,s,k,al,sx,sy,fl){
      if (s <= 0.5 || al <= 0) return; sx = sx || 1; sy = sy || 1;
      var w = s*sx, h = s*sy, dy = (1 - sy)*s*0.5;
      x.globalAlpha = al; x.drawImage(SP[k + lvl(w)], cx - w/2, cy - h/2 + dy, w, h);
      if (fl > 0){ x.globalAlpha = al*fl; x.drawImage(SP.flash, cx - w/2, cy - h/2 + dy, w, h); }
      x.globalAlpha = 1;
    }
    function piece(cx,cy,s,al){ var o = s*0.54; blk(cx - o, cy - o, s, pk, al); blk(cx + o, cy - o, s, pk, al); blk(cx - o, cy + o, s, pk, al); blk(cx + o, cy + o, s, pk, al); }

    function layout(){
      var rc = a.getBoundingClientRect(); if (rc.width < 50 || rc.height < 50) return false;
      W = rc.width; H = rc.height; DPR = Math.min(2, window.devicePixelRatio || 1);
      cv.width = Math.round(W*DPR); cv.height = Math.round(H*DPR);
      R = H >= 260 ? 4 : 3;
      var pad = clamp(H*0.07, 10, 18), o = {pad:pad, wide:W >= 600}, ctaH, cw;
      o.ws = clamp(H*0.066, 12, 16);
      if (o.wide){
        var right = clamp(W*0.36, 200, 360), region = W - right - pad*2;
        o.cell = Math.min((H - pad*2)/R, region/(C + 3)); o.bx = pad; o.by = (H - o.cell*R)/2;
        o.tcell = o.cell*0.8; o.home = {x:o.bx + o.cell*C + o.cell*1.6, y:o.by + o.cell*(R - 1)};
        ctaH = clamp(H*0.2, 38, 54); x.font = '700 ' + (ctaH*0.4) + 'px ' + FONT; cw = x.measureText(TX.cta).width + ctaH*1.9;
        var left = o.home.x + o.tcell*1.5;
        var fs = Math.min(H*0.84, right*0.48, W - pad*0.5 - 12 - cw - left);
        o.fox = fs >= 70 ? {s:fs, x:W - pad*0.5 - fs, y:H - fs*1.02} : null;
        var limit = o.fox ? o.fox.x - 8 : W - pad;
        o.cta = {w:cw, h:ctaH, x:Math.max(left, limit - cw), y:H/2 + 2};
        o.hook = {x:o.cta.x, y:o.cta.y - ctaH*0.42, s:clamp(H*0.14, 18, 34)};
        o.mark = {x:o.cta.x, y:o.hook.y - o.hook.s*1.5};
      } else {
        o.fox = {s:clamp(H*0.25, 44, 72)}; o.fox.x = W - pad - o.fox.s*0.95; o.fox.y = 1;
        var top = pad + o.fox.s*0.62; ctaH = clamp(H*0.17, 38, 48);
        o.cell = Math.min((W - pad*2)/C, (H - top - pad*2 - ctaH - 8)/R); o.bx = (W - o.cell*C)/2; o.by = top + 4;
        o.tcell = o.cell*0.7;
        var below = o.by + o.cell*R + 8, mid = below + (H - below - pad)/2;
        o.home = {x:o.bx + o.tcell*1.25, y:mid};
        x.font = '700 ' + (ctaH*0.4) + 'px ' + FONT; cw = x.measureText(TX.cta).width + ctaH*1.9;
        o.cta = {w:cw, h:ctaH, x:W - pad - cw, y:mid - ctaH/2};
        o.hook = null; o.mark = {x:pad, y:pad + o.ws*0.2};
      }
      L = o; sprites();
      var g = o.tcell*2.8; gs.left = (o.home.x - g/2) + 'px'; gs.top = (o.home.y - g/2) + 'px'; gs.width = gs.height = g + 'px';
      return true;
    }
    function sprites(){
      var s = Math.ceil(Math.max(24, L.cell*1.15*DPR));
      SP.lv = [s, Math.max(8, Math.round(s/2)), Math.max(6, Math.round(s/4))];
      KEYS.forEach(function(k){ SP[k] = blockSprite(k, s); SP[k+'1'] = blockSprite(k, SP.lv[1]); SP[k+'2'] = blockSprite(k, SP.lv[2]); });
      var fl = mk(s,s), fo = fl.getContext('2d'); fo.fillStyle = '#fff'; rr(fo,0,0,s,s,s*0.24); fo.fill(); SP.flash = fl;
      SP.halo = radial(128, [[0,'rgba(233,167,47,.5)'],[1,'rgba(233,167,47,0)']]);
      SP.ring = radial(256, [[0,'rgba(233,167,47,0)'],[0.74,'rgba(233,167,47,0)'],[0.88,'rgba(233,167,47,.9)'],[1,'rgba(233,167,47,0)']]);
      var bg = mk(W*DPR, H*DPR), bo = bg.getContext('2d'); bo.scale(DPR,DPR);
      bo.fillStyle = '#f6efe4'; bo.fillRect(0,0,W,H);
      var ts = 34; bo.strokeStyle = 'rgba(150,120,90,.12)'; bo.lineWidth = 1;
      for (var yy = -ts/2; yy < H; yy += ts) for (var xx = -ts/2; xx < W; xx += ts){ rr(bo, xx + 3.5, yy + 3.5, ts - 7, ts - 7, 7); bo.stroke(); }
      var bcx = L.bx + L.cell*C/2, bcy = L.by + L.cell*R/2, gr = bo.createRadialGradient(bcx,bcy,0,bcx,bcy,L.cell*C*0.8);
      gr.addColorStop(0,'rgba(233,167,47,.22)'); gr.addColorStop(1,'rgba(233,167,47,0)'); bo.fillStyle = gr; bo.fillRect(0,0,W,H);
      var m = L.cell*0.16, bw = L.cell*C + m*2, bh = L.cell*R + m*2, bx = L.bx - m, by = L.by - m, br = L.cell*0.34;
      bo.fillStyle = 'rgba(58,36,24,.09)'; rr(bo, bx + 3, by + 8, bw, bh, br); bo.fill();
      bo.fillStyle = '#cbb596'; rr(bo, bx, by + L.cell*0.08, bw, bh, br); bo.fill();
      bo.fillStyle = '#ece2d3'; rr(bo, bx, by, bw, bh, br); bo.fill();
      for (var i = 0; i < R*C; i++){ var c = cellXY(i), ws = L.cell*0.9; bo.fillStyle = '#dccfbb'; rr(bo, c[0] - ws/2, c[1] - ws/2, ws, ws, ws*0.22); bo.fill();
        bo.fillStyle = 'rgba(110,75,40,.08)'; rr(bo, c[0] - ws/2, c[1] - ws/2, ws, ws*0.3, ws*0.22); bo.fill(); }
      SP.bg = bg;
      var ch = L.cta.h, cwid = L.cta.w, cp = mk(cwid*DPR, ch*1.14*DPR), co = cp.getContext('2d'); co.scale(DPR,DPR);
      co.fillStyle = '#1c7064'; rr(co, 0, ch*0.12, cwid, ch, ch/2); co.fill();
      var cg = co.createLinearGradient(0,0,0,ch); cg.addColorStop(0,'#4fc8b6'); cg.addColorStop(1,'#26988a'); co.fillStyle = cg; rr(co, 0, 0, cwid, ch, ch/2); co.fill();
      co.fillStyle = 'rgba(255,255,255,.3)'; rr(co, ch*0.35, ch*0.09, cwid - ch*0.7, ch*0.2, ch*0.1); co.fill();
      co.font = '700 ' + (ch*0.4) + 'px ' + FONT; co.textBaseline = 'middle'; co.textAlign = 'left'; co.fillStyle = '#fff';
      var tw = co.measureText(TX.cta).width, tri = ch*0.17, total = tw + ch*0.22 + tri*1.3, sx = (cwid - total)/2;
      co.fillText(TX.cta, sx, ch*0.53);
      var t0 = sx + tw + ch*0.22; co.beginPath(); co.moveTo(t0, ch*0.5 - tri*0.75); co.lineTo(t0 + tri*1.3, ch*0.5); co.lineTo(t0, ch*0.5 + tri*0.75); co.closePath(); co.fill();
      SP.cta = cp;
    }

    // ------------------------------------------------------------ play
    function scenario(first){
      board = []; for (var i = 0; i < R*C; i++) board.push(null);
      var gc = 1 + ((Math.random()*(C - 3))|0), r, c;
      for (r = R - 2; r < R; r++) for (c = 0; c < C; c++) if (c !== gc && c !== gc + 1) board[r*C + c] = rnd(KEYS);
      for (r = 0; r < R - 2; r++){ var n = 0; for (c = 0; c < C; c++) if (Math.random() < 0.3 && n < C - 3){ board[r*C + c] = rnd(KEYS); n++; } }
      gap = {r:R - 2, c:gc}; pk = rnd(KEYS); drop = {};
      var t0 = now + (first ? 200 : 0);
      if (!reduce) for (var j = 0; j < R*C; j++) if (board[j]) drop[j] = {t0:t0 + (R - 1 - ((j/C)|0))*70 + (j%C)*20 + Math.random()*40, dur:380};
      phase = 'rain'; pieceBorn = t0 + (reduce ? 0 : 560);
    }
    function place(fx,fy,fs){
      if (phase !== 'ready') return;
      phase = 'fly'; fly = {t0:now, fx:fx, fy:fy, fs:fs}; lastAct = now; demo = demo && demo.auto ? demo : null;
    }
    function land(){
      fly = null;
      for (var r = gap.r; r < gap.r + 2; r++) for (var c = gap.c; c < gap.c + 2; c++){ board[r*C + c] = pk; drop[r*C + c] = {t0:now, dur:0, sq:1}; }
      phase = 'land'; setTimeout(clear, reduce ? 0 : 150);
    }
    function clear(){
      for (var r = R - 2; r < R; r++) for (var c = 0; c < C; c++){
        var i = r*C + c, k = board[i]; if (!k) continue; board[i] = null; delete drop[i];
        ghosts.push({i:i, k:k, t0:now + c*14});
        if (!reduce) for (var m = 0; m < 3; m++){ var p = cellXY(i); parts.push({x:p[0], y:p[1], vx:(Math.random() - .5)*L.cell*14, vy:-L.cell*(3 + Math.random()*7),
          r:Math.random()*6, vr:(Math.random() - .5)*14, s:L.cell*(0.18 + Math.random()*0.2), k:k, t0:now + c*14, life:650 + Math.random()*450}); }
      }
      phase = 'won'; winT = now;
    }

    // the demo finger, while nobody touches
    function startDemo(){
      var g = gapCenter();
      demo = {t0:now, auto:true, from:[L.home.x + L.cell*2, L.home.y + L.cell*2.2], st:[L.home.x, L.home.y], en:[g[0], g[1]], hx:0, hy:0, ha:0, down:false};
      demos++;
    }
    function stepDemo(t){
      var d = demo, e = t - d.t0, A = 520, P = 160, M = 820, Q = 420;
      if (e < A){ var q = eIO(e/A); d.hx = lerp(d.from[0], d.st[0], q); d.hy = lerp(d.from[1], d.st[1], q); d.ha = Math.min(1, e/200); return; }
      if (e < A + P){ d.hx = d.st[0]; d.hy = d.st[1]; d.down = true; return; }
      if (e < A + P + M){
        var q2 = eIO((e - A - P)/M), u = 1 - q2, mx = (d.st[0] + d.en[0])/2, my = Math.min(d.st[1], d.en[1]) - L.cell*1.6;
        d.hx = u*u*d.st[0] + 2*u*q2*mx + q2*q2*d.en[0]; d.hy = u*u*d.st[1] + 2*u*q2*my + q2*q2*d.en[1]; d.carry = true; return;
      }
      if (d.carry){ d.carry = false; d.down = false; phase = 'ready'; place(d.hx, d.hy, lerp(L.tcell, L.cell, 1)); }
      var q3 = (e - A - P - M)/Q; if (q3 >= 1){ demo = null; return; }
      d.hx = d.en[0] + q3*L.cell*0.8; d.hy = d.en[1] + q3*L.cell; d.ha = 1 - q3;
    }

    function logic(t){
      if (phase === 'rain' && t >= pieceBorn && !Object.keys(drop).some(function(k){ return !drop[k].sq; })){ phase = 'ready'; readyT = t; }
      if (phase === 'won' && t - winT > (reduce ? 1400 : 2300)) scenario(false);
      if (demo) stepDemo(t);
      else if (phase === 'ready' && !drag && !fly && !reduce && demos < 2 && t - startT > 1000 && t - Math.max(lastAct, readyT) > (demos ? 5200 : 1700)) startDemo();
      if (fly && t - fly.t0 >= (reduce ? 0 : 170)) land();
    }

    // ------------------------------------------------------------ paint
    function paint(t){
      x.setTransform(DPR,0,0,DPR,0,0); x.imageSmoothingEnabled = true; x.globalAlpha = 1;
      x.drawImage(SP.bg, 0, 0, W, H);
      var i, c, cs = L.cell*0.9;
      if (phase === 'ready' && !fly){ var pa = 0.2 + 0.15*Math.sin(t/220), gc2 = gapCenter(), hs = L.cell*2.6;
        x.globalAlpha = 0.55 + 0.25*Math.sin(t/220); x.drawImage(SP.halo, gc2[0] - hs/2, gc2[1] - hs/2, hs, hs); x.globalAlpha = 1;
        for (var r = gap.r; r < gap.r + 2; r++) for (c = gap.c; c < gap.c + 2; c++){ var p = cellXY(r*C + c); blk(p[0], p[1], cs, pk, pa); } }
      for (i = 0; i < R*C; i++){
        var k = board[i]; if (!k) continue;
        var q = cellXY(i), d = drop[i], oy = 0, sx = 1, sy = 1;
        if (d){ var e = t - d.t0; if (e < 0) continue;
          if (e < d.dur) oy = -(1 - eIn(e/d.dur))*H*0.9;
          else { var u = (e - d.dur)/260; if (u >= 1) delete drop[i]; else { var wv = Math.sin(u*Math.PI)*(1 - u); sx = 1 + 0.14*wv; sy = 1 - 0.2*wv; } } }
        blk(q[0], q[1] + oy, cs, k, 1, sx, sy);
      }
      ghosts = ghosts.filter(function(g){ var q = (t - g.t0)/420, p = cellXY(g.i); if (q >= 1) return false;
        if (q < 0) blk(p[0], p[1], cs, g.k, 1); else if (q < 0.3) blk(p[0], p[1], cs*(1 + q*0.5), g.k, 1, 1, 1, q/0.3*0.85);
        else blk(p[0], p[1], cs*1.15*(1 - eOut((q - 0.3)/0.7)), g.k, 1, 1, 1, 0.85*(1 - (q - 0.3)/0.7)); return true; });
      if (phase === 'won' && t - winT < 700 && !reduce){ var rq = (t - winT)/700, gc3 = gapCenter(), RR = lerp(L.cell, L.cell*C*0.9, eOut(rq));
        x.globalAlpha = (1 - rq)*0.5; x.drawImage(SP.ring, gc3[0] - RR, gc3[1] - RR, RR*2, RR*2); x.globalAlpha = 1; }
      // the piece: at home (bobbing), dragged, flying into the gap or going back home
      if (phase === 'ready' || phase === 'fly' || phase === 'rain'){
        var born = clamp((t - pieceBorn)/380, 0, 1);
        if (fly){ var f = eOut((t - fly.t0)/170), g = gapCenter(); piece(lerp(fly.fx, g[0], f), lerp(fly.fy, g[1], f), lerp(fly.fs, L.cell, f)*0.9, 1); }
        else if (drag || (demo && demo.carry)){ var dp = dragPos(); x.globalAlpha = 0.25; x.drawImage(SP.halo, dp.x - dp.s*1.6, dp.y - dp.s*1.1, dp.s*3.2, dp.s*3.2); x.globalAlpha = 1; piece(dp.x, dp.y, dp.s*0.9, 1); }
        else if (born > 0){
          var hx = L.home.x, hy = L.home.y, s = L.tcell;
          if (ret){ var rq2 = eOut((t - ret.t0)/260); if (rq2 >= 1) ret = null; else { hx = lerp(ret.x, hx, rq2); hy = lerp(ret.y, hy, rq2); s = lerp(ret.s, s, rq2); } }
          var bob = reduce ? 0 : Math.sin(t/260)*s*0.12, hs2 = s*3.2;
          x.globalAlpha = (0.5 + 0.3*Math.sin(t/260))*born; x.drawImage(SP.halo, hx - hs2/2, hy - hs2/2, hs2, hs2); x.globalAlpha = 1;
          piece(hx, hy + bob - (hover ? s*0.08 : 0), s*0.92*eBack(born), 1);
        }
      }
      // brand, hook, button
      var ws = L.ws, mx = L.mark.x, my = L.mark.y, ms = ws*0.6;
      blk(mx + ms*0.5, my + ms*0.5, ms*0.94, 't', 1); blk(mx + ms*1.55, my + ms*0.5, ms*0.94, 'y', 1); blk(mx + ms*2.6, my + ms*0.5, ms*0.94, 'p', 1); blk(mx + ms*1.55, my + ms*1.55, ms*0.94, 'o', 1);
      x.font = '700 ' + ws + 'px ' + FONT; x.fillStyle = INK; x.textAlign = 'left'; x.textBaseline = 'middle'; x.fillText('Teselo', mx + ms*3.5, my + ms*0.95);
      var won = phase === 'won' || t - winT < 2600;
      if (L.hook){
        var ht = won ? TX.more : TX.hook, hsz = L.hook.s, room = (L.fox ? L.fox.x - 6 : W - L.pad) - L.hook.x;
        x.font = '800 ' + hsz + 'px ' + FONT; var hw0 = x.measureText(ht).width;
        if (hw0 > room){ hsz *= room/hw0; x.font = '800 ' + hsz + 'px ' + FONT; }   // always fits beside the fox
        x.textBaseline = 'alphabetic'; x.fillStyle = won ? PAL.p[1] : INK; x.fillText(ht, L.hook.x, L.hook.y);
      }
      var pulse = won ? 1 + 0.07*Math.sin((t - winT)/110)*Math.max(0, 1 - (t - winT)/2200) : 1 + (reduce ? 0 : 0.018*Math.max(0, Math.sin(t/520)));
      if (hover) pulse *= 1.03;
      var cta = L.cta, cw = cta.w*pulse, chh = cta.h*1.14*pulse;
      if (won && !reduce){ var gl = Math.max(0, 1 - (t - winT)/2400), hw = cta.w*1.6; x.globalAlpha = gl*0.8; x.drawImage(SP.halo, cta.x + cta.w/2 - hw/2, cta.y + cta.h/2 - hw*0.32, hw, hw*0.64); x.globalAlpha = 1; }
      x.drawImage(SP.cta, cta.x + cta.w/2 - cw/2, cta.y + cta.h*0.57 - chh/2, cw, chh);
      // the fox: breathes, jumps on the combo
      if (L.fox && fox.complete && fox.naturalWidth){
        var fs = L.fox.s, fh = fs*fox.naturalHeight/fox.naturalWidth, jq = (t - winT)/650, jump = (jq >= 0 && jq < 1 && !reduce) ? Math.sin(jq*Math.PI) : 0;
        var br = reduce ? 1 : 1 + 0.015*Math.sin(t/640);
        x.save(); x.translate(L.fox.x + fs/2, L.fox.y + fh); x.rotate(jump*0.12); x.scale(br*(1 - jump*0.04), br*(1 + jump*0.06));
        x.drawImage(fox, -fs/2, -fh - jump*fs*0.2, fs, fh); x.restore();
      }
      // particles and the combo message
      var G = L.cell*26;
      parts = parts.filter(function(p){ var e = t - p.t0; if (e < 0) return true; var q = e/p.life; if (q >= 1) return false; var s = e/1000;
        x.save(); x.globalAlpha = 1 - q*q; x.translate(p.x + p.vx*s, p.y + p.vy*s + 0.5*G*s*s); x.rotate(p.r + s*p.vr);
        x.drawImage(SP[p.k + lvl(p.s)], -p.s/2, -p.s/2, p.s, p.s); x.restore(); return true; });
      var tq = (t - winT)/1100;
      if (tq >= 0 && tq < 1){
        var al = tq < 0.15 ? tq/0.15 : tq > 0.7 ? (1 - tq)/0.3 : 1, sz = L.cell*(L.wide ? 0.95 : 0.8)*(tq < 0.15 ? 0.8 + eBack(tq/0.15)*0.2 : 1);
        x.save(); x.globalAlpha = al; x.font = 'italic 800 ' + sz + 'px ' + FONT; x.textAlign = 'center'; x.textBaseline = 'middle';
        x.lineJoin = 'round'; x.lineWidth = sz*0.22; x.strokeStyle = '#fffaf2'; var cx0 = L.bx + L.cell*C/2, cy0 = L.by + L.cell*R/2 - eOut(tq)*L.cell*0.3;
        x.strokeText(TX.combo, cx0, cy0); x.fillStyle = PAL.p[1]; x.fillText(TX.combo, cx0, cy0); x.restore();
      }
      if (demo && demo.ha > 0){ var hr = L.cell*0.3*(demo.down ? 0.86 : 1);
        x.globalAlpha = demo.ha*0.25; x.drawImage(SP.halo, demo.hx - hr*2, demo.hy - hr*2, hr*4, hr*4);
        x.globalAlpha = demo.ha*0.95; x.fillStyle = '#fffdf8'; x.beginPath(); x.arc(demo.hx, demo.hy + L.cell*0.9, hr, 0, Math.PI*2); x.fill();
        x.lineWidth = 2; x.strokeStyle = 'rgba(58,36,24,.3)'; x.stroke(); x.globalAlpha = 1; }
    }
    function dragPos(){
      if (demo && demo.carry) return {x:demo.hx, y:demo.hy, s:L.cell};
      var g = eOut((now - drag.t0)/150);
      return {x:lerp(L.home.x, drag.px, g), y:lerp(L.home.y, drag.py - drag.lift, g), s:lerp(L.tcell, L.cell, g)};
    }

    // ------------------------------------------------------------ loop
    function busy(t){ return phase !== 'ready' || drag || fly || ret || demo || hover || parts.length || ghosts.length || t - winT < 2600; }
    function frame(t){
      raf = 0; if (!visible) return;
      if (startT === null){ startT = t; now = t; scenario(true); }
      now = t;
      var b = busy(t) || Object.keys(drop).length > 0;
      odd = !odd;
      if (!b && odd){ raf = requestAnimationFrame(frame); return; }
      logic(t); paint(t);
      var idle = !b && t - Math.max(lastAct, readyT) > 20000 && demos >= 2;
      if (!idle) raf = requestAnimationFrame(frame);
    }
    function kick(){ if (!raf && visible && W) raf = requestAnimationFrame(frame); }

    // ------------------------------------------------------------ input (the card itself is the link)
    grab.addEventListener('pointerdown', function(e){
      if (phase !== 'ready' || fly) return;
      e.preventDefault(); e.stopPropagation();
      demo = null; try { grab.setPointerCapture(e.pointerId); } catch (er) {}
      var rc = cv.getBoundingClientRect();
      drag = {px:e.clientX - rc.left, py:e.clientY - rc.top, sx:e.clientX, sy:e.clientY, moved:false, lift:e.pointerType === 'mouse' ? 0 : L.cell*1.1, t0:now};
      lastAct = now; gs.cursor = 'grabbing'; kick();
    });
    grab.addEventListener('pointermove', function(e){
      if (!drag) return; var rc = cv.getBoundingClientRect(); drag.px = e.clientX - rc.left; drag.py = e.clientY - rc.top;
      if (Math.abs(e.clientX - drag.sx) + Math.abs(e.clientY - drag.sy) > 6) drag.moved = true; lastAct = now;
    });
    grab.addEventListener('pointerup', function(){
      if (!drag) return; var p = dragPos(), d = drag; drag = null; gs.cursor = 'grab'; lastAct = now;
      if (!d.moved){ place(L.home.x, L.home.y, L.tcell); return; }
      var g = gapCenter(), over = p.x > L.bx - L.cell && p.x < L.bx + L.cell*(C + 1) && p.y > L.by - L.cell && p.y < L.by + L.cell*(R + 1);
      if (over || Math.abs(p.x - g[0]) + Math.abs(p.y - g[1]) < L.cell*3) place(p.x, p.y, p.s); else ret = {t0:now, x:p.x, y:p.y, s:p.s};
    });
    grab.addEventListener('pointercancel', function(){ if (drag){ var p = dragPos(); drag = null; ret = {t0:now, x:p.x, y:p.y, s:p.s}; } });
    grab.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation(); });
    a.addEventListener('pointerenter', function(e){ if (e.pointerType === 'mouse'){ hover = true; lastAct = now; kick(); } });
    a.addEventListener('pointerleave', function(){ hover = false; });
    a.addEventListener('focus', function(){ hover = true; kick(); }); a.addEventListener('blur', function(){ hover = false; });

    if (!layout()){ grab.remove(); return; }   // no room measured: the static card (the fallback) stays
    card.classList.add('tsl-on');
    if (window.IntersectionObserver) new IntersectionObserver(function(es){ visible = es[0].isIntersecting; if (visible) kick(); }, {threshold:0.15}).observe(card);
    else { visible = true; kick(); }
    if (window.ResizeObserver) new ResizeObserver(function(){ if (layout()) kick(); }).observe(a);
    fox.addEventListener('load', kick);
  }

  function scan(){
    var cs = document.querySelectorAll('.hp.tsl');
    for (var i = 0; i < cs.length; i++){ var c = cs[i]; if (!c.__tsl && !c.hidden && c.offsetParent !== null){ c.__tsl = 1; Ad(c); } }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
})();
