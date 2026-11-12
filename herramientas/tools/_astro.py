"""Shared astronomy and calendar code of pack C (moon phases, sunrise/sunset, Easter, Chinese New Year).

Ignored by the registry (leading underscore). Each tool's compute must be self-contained, so the JS lives here as
strings that the tool files paste into their compute function; the Python twins render the worked examples of the
explanation blocks at build time (same formulas, so page text and tool agree).

Formulas (reimplemented, no code copied):
- Moon phases: Jean Meeus, Astronomical Algorithms (2nd ed., 1998), chapter 49 (mean phase + periodic and planetary
  terms). Checked against the US Naval Observatory phase list for 2027 (public domain).
- Sun: NOAA Global Monitoring Laboratory solar calculator equations (US government work, public domain), themselves
  from Meeus. Sunrise/sunset at zenith 90.833 deg (refraction + solar radius), civil twilight at 96 deg.
- Easter: the anonymous Gregorian algorithm (Nature, 1876; Meeus ch. 8); Orthodox Easter by the Julian computus.
"""
import datetime as dt
import math
import zoneinfo

TZ_PEN, TZ_CAN = zoneinfo.ZoneInfo("Europe/Madrid"), zoneinfo.ZoneInfo("Atlantic/Canary")
SYN = 29.530588861

# ---------------------------------------------------------------- Python twins (build-time examples)

_DT = [(1900, -2.7), (1920, 21.2), (1940, 24.3), (1960, 33.2), (1980, 50.5), (2000, 63.8), (2015, 67.6), (2020, 69.4), (2026, 69.2)]


def delta_t(y):
    """TT - UT in seconds: linear between table points (Espenak/Meeus values), flat after 2026 (minute-level use)."""
    if y <= _DT[0][0]:
        return _DT[0][1]
    for (y0, v0), (y1, v1) in zip(_DT, _DT[1:]):
        if y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return _DT[-1][1]


def _s(x):
    return math.sin(math.radians(x))


def phase_jde(k):
    """Meeus ch. 49: JDE of the phase k (integer = new moon, .25 first quarter, .5 full, .75 last quarter)."""
    T = k / 1236.85
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * T ** 2 - 0.000000150 * T ** 3 + 0.00000000073 * T ** 4
    E = 1 - 0.002516 * T - 0.0000074 * T ** 2
    M = 2.5534 + 29.10535670 * k - 0.0000014 * T ** 2 - 0.00000011 * T ** 3
    Mp = 201.5643 + 385.81693528 * k + 0.0107582 * T ** 2 + 0.00001238 * T ** 3 - 0.000000058 * T ** 4
    F = 160.7108 + 390.67050284 * k - 0.0016118 * T ** 2 - 0.00000227 * T ** 3 + 0.000000011 * T ** 4
    O = 124.7746 - 1.56375588 * k + 0.0020672 * T ** 2 + 0.00000215 * T ** 3
    q = round((k - math.floor(k)) * 4) % 4
    if q in (0, 2):
        c = (-0.40720, 0.17241, 0.01608, 0.01039, 0.00739, -0.00514, 0.00208) if q == 0 else \
            (-0.40614, 0.17302, 0.01614, 0.01043, 0.00734, -0.00515, 0.00209)
        corr = (c[0] * _s(Mp) + c[1] * E * _s(M) + c[2] * _s(2 * Mp) + c[3] * _s(2 * F) + c[4] * E * _s(Mp - M)
                + c[5] * E * _s(Mp + M) + c[6] * E * E * _s(2 * M) - 0.00111 * _s(Mp - 2 * F) - 0.00057 * _s(Mp + 2 * F)
                + 0.00056 * E * _s(2 * Mp + M) - 0.00042 * _s(3 * Mp) + 0.00042 * E * _s(M + 2 * F) + 0.00038 * E * _s(M - 2 * F)
                - 0.00024 * E * _s(2 * Mp - M) - 0.00017 * _s(O) - 0.00007 * _s(Mp + 2 * M) + 0.00004 * _s(2 * Mp - 2 * F)
                + 0.00004 * _s(3 * M) + 0.00003 * _s(Mp + M - 2 * F) + 0.00003 * _s(2 * Mp + 2 * F) - 0.00003 * _s(Mp + M + 2 * F)
                + 0.00003 * _s(Mp - M + 2 * F) - 0.00002 * _s(Mp - M - 2 * F) - 0.00002 * _s(3 * Mp + M) + 0.00002 * _s(4 * Mp))
    else:
        corr = (-0.62801 * _s(Mp) + 0.17172 * E * _s(M) - 0.01183 * E * _s(Mp + M) + 0.00862 * _s(2 * Mp) + 0.00804 * _s(2 * F)
                + 0.00454 * E * _s(Mp - M) + 0.00204 * E * E * _s(2 * M) - 0.00180 * _s(Mp - 2 * F) - 0.00070 * _s(Mp + 2 * F)
                - 0.00040 * _s(3 * Mp) - 0.00034 * E * _s(2 * Mp - M) + 0.00032 * E * _s(M + 2 * F) + 0.00032 * E * _s(M - 2 * F)
                - 0.00028 * E * E * _s(Mp + 2 * M) + 0.00027 * E * _s(2 * Mp + M) - 0.00017 * _s(O) - 0.00005 * _s(Mp - M - 2 * F)
                + 0.00004 * _s(2 * Mp + 2 * F) - 0.00004 * _s(Mp + M + 2 * F) + 0.00004 * _s(Mp - 2 * M) + 0.00003 * _s(Mp + M - 2 * F)
                + 0.00003 * _s(3 * M) + 0.00002 * _s(2 * Mp - 2 * F) + 0.00002 * _s(Mp - M + 2 * F) - 0.00002 * _s(3 * Mp + M))
        c = math.cos
        W = (0.00306 - 0.00038 * E * c(math.radians(M)) + 0.00026 * c(math.radians(Mp)) - 0.00002 * c(math.radians(Mp - M))
             + 0.00002 * c(math.radians(Mp + M)) + 0.00002 * c(math.radians(2 * F)))
        corr += W if q == 1 else -W
    A = [299.77 + 0.107408 * k - 0.009173 * T ** 2, 251.88 + 0.016321 * k, 251.83 + 26.651886 * k, 349.42 + 36.412478 * k,
         84.66 + 18.206239 * k, 141.74 + 53.303771 * k, 207.14 + 2.453732 * k, 154.84 + 7.306860 * k, 34.52 + 27.261239 * k,
         207.19 + 0.121824 * k, 291.34 + 1.844379 * k, 161.72 + 24.198154 * k, 239.56 + 25.513099 * k, 331.55 + 3.592518 * k]
    AC = [0.000325, 0.000165, 0.000164, 0.000126, 0.000110, 0.000062, 0.000060, 0.000056, 0.000047, 0.000042, 0.000040,
          0.000037, 0.000035, 0.000023]
    return jde + corr + sum(a * _s(x) for a, x in zip(AC, A))


def jd_to_utc(jd):
    return dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(days=jd - 2440587.5)


def phase_utc(k):
    jde = phase_jde(k)
    y = 2000 + k / 12.3685
    return jd_to_utc(jde - delta_t(y) / 86400)


def phases(year):
    """[(q, utc datetime)] of every phase whose UTC instant falls in the year; q 0 new, 1 first q., 2 full, 3 last q."""
    out = []
    k0 = math.floor((year - 2000) * 12.3685) - 2
    for i in range(0, 4 * 17):
        k = k0 + i / 4
        t = phase_utc(k)
        if t.year == year:
            out.append((i % 4, t))
    return out


def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    n = h + l_ - 7 * m + 114
    return dt.date(y, n // 31, n % 31 + 1)


def easter_orthodox(y):
    a, b, c = y % 4, y % 7, y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    n = d + e + 114
    jul = dt.date(y, n // 31, n % 31 + 1)
    return jul + dt.timedelta(days=y // 100 - y // 400 - 2)  # Julian -> Gregorian (13 days in 1900-2099)


def sun(date, lat, lon, zen=90.833):
    """UTC minutes after midnight of `date` for sunrise, solar noon and sunset (NOAA equations, 2 iterations).
    None for rise/set when the sun does not cross that zenith that day."""
    def at(mins):
        jd = (dt.datetime(date.year, date.month, date.day) - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400 + 2451545 + mins / 1440
        T = (jd - 2451545) / 36525
        L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
        M = 357.52911 + T * (35999.05029 - 0.0001537 * T)
        e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
        C = _s(M) * (1.914602 - T * (0.004817 + 0.000014 * T)) + _s(2 * M) * (0.019993 - 0.000101 * T) + _s(3 * M) * 0.000289
        lam = L0 + C - 0.00569 - 0.00478 * _s(125.04 - 1934.136 * T)
        eps = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60 + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * T))
        decl = math.degrees(math.asin(_s(eps) * _s(lam)))
        y = math.tan(math.radians(eps / 2)) ** 2
        eot = 4 * math.degrees(y * _s(2 * L0) - 2 * e * _s(M) + 4 * e * y * _s(M) * math.cos(math.radians(2 * L0))
                               - 0.5 * y * y * _s(4 * L0) - 1.25 * e * e * _s(2 * M))
        return decl, eot

    def event(sign):
        t = 720 - 4 * lon
        for _ in range(3):
            decl, eot = at(t)
            noon = 720 - 4 * lon - eot
            if sign == 0:
                t = noon
                continue
            la, de = math.radians(lat), math.radians(decl)
            x = math.cos(math.radians(zen)) / (math.cos(la) * math.cos(de)) - math.tan(la) * math.tan(de)
            if abs(x) > 1:
                return None
            t = noon + sign * 4 * math.degrees(math.acos(x))
        return t
    return {"rise": event(-1), "noon": event(0), "set": event(1)}


def local_hm(date, mins, tz):
    """'HH:MM' local time of a UTC-minute value of `date` (rounded to the minute)."""
    t = dt.datetime(date.year, date.month, date.day, tzinfo=dt.timezone.utc) + dt.timedelta(minutes=round(mins))
    return t.astimezone(tz).strftime("%H:%M")


# ---------------------------------------------------------------- JS (pasted inside compute functions)

# deltaT, phaseJDE(k), phaseMs(k) (UTC ms), phasesIn(ms0, ms1) -> [[q, ms]], illum(ms, list) -> [angle 0-360, fraction]
MOON_JS = r"""
  var DTT = [[1900, -2.7], [1920, 21.2], [1940, 24.3], [1960, 33.2], [1980, 50.5], [2000, 63.8], [2015, 67.6], [2020, 69.4], [2026, 69.2]];
  function deltaT(y) {
    if (y <= DTT[0][0]) return DTT[0][1];
    for (var i = 1; i < DTT.length; i++) if (y <= DTT[i][0]) return DTT[i - 1][1] + (DTT[i][1] - DTT[i - 1][1]) * (y - DTT[i - 1][0]) / (DTT[i][0] - DTT[i - 1][0]);
    return DTT[DTT.length - 1][1];
  }
  function sn(x) { return Math.sin(x * Math.PI / 180); }
  function cs(x) { return Math.cos(x * Math.PI / 180); }
  function phaseJDE(k) {
    var T = k / 1236.85, T2 = T * T, T3 = T2 * T, T4 = T3 * T;
    var jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * T2 - 0.000000150 * T3 + 0.00000000073 * T4;
    var E = 1 - 0.002516 * T - 0.0000074 * T2;
    var M = 2.5534 + 29.10535670 * k - 0.0000014 * T2 - 0.00000011 * T3;
    var P = 201.5643 + 385.81693528 * k + 0.0107582 * T2 + 0.00001238 * T3 - 0.000000058 * T4;
    var F = 160.7108 + 390.67050284 * k - 0.0016118 * T2 - 0.00000227 * T3 + 0.000000011 * T4;
    var O = 124.7746 - 1.56375588 * k + 0.0020672 * T2 + 0.00000215 * T3;
    var q = Math.round((k - Math.floor(k)) * 4) % 4, c;
    if (q === 0 || q === 2) {
      var a = q === 0 ? [-0.40720, 0.17241, 0.01608, 0.01039, 0.00739, -0.00514, 0.00208] : [-0.40614, 0.17302, 0.01614, 0.01043, 0.00734, -0.00515, 0.00209];
      c = a[0] * sn(P) + a[1] * E * sn(M) + a[2] * sn(2 * P) + a[3] * sn(2 * F) + a[4] * E * sn(P - M) + a[5] * E * sn(P + M) + a[6] * E * E * sn(2 * M)
        - 0.00111 * sn(P - 2 * F) - 0.00057 * sn(P + 2 * F) + 0.00056 * E * sn(2 * P + M) - 0.00042 * sn(3 * P) + 0.00042 * E * sn(M + 2 * F)
        + 0.00038 * E * sn(M - 2 * F) - 0.00024 * E * sn(2 * P - M) - 0.00017 * sn(O) - 0.00007 * sn(P + 2 * M) + 0.00004 * sn(2 * P - 2 * F)
        + 0.00004 * sn(3 * M) + 0.00003 * sn(P + M - 2 * F) + 0.00003 * sn(2 * P + 2 * F) - 0.00003 * sn(P + M + 2 * F) + 0.00003 * sn(P - M + 2 * F)
        - 0.00002 * sn(P - M - 2 * F) - 0.00002 * sn(3 * P + M) + 0.00002 * sn(4 * P);
    } else {
      c = -0.62801 * sn(P) + 0.17172 * E * sn(M) - 0.01183 * E * sn(P + M) + 0.00862 * sn(2 * P) + 0.00804 * sn(2 * F) + 0.00454 * E * sn(P - M)
        + 0.00204 * E * E * sn(2 * M) - 0.00180 * sn(P - 2 * F) - 0.00070 * sn(P + 2 * F) - 0.00040 * sn(3 * P) - 0.00034 * E * sn(2 * P - M)
        + 0.00032 * E * sn(M + 2 * F) + 0.00032 * E * sn(M - 2 * F) - 0.00028 * E * E * sn(P + 2 * M) + 0.00027 * E * sn(2 * P + M) - 0.00017 * sn(O)
        - 0.00005 * sn(P - M - 2 * F) + 0.00004 * sn(2 * P + 2 * F) - 0.00004 * sn(P + M + 2 * F) + 0.00004 * sn(P - 2 * M) + 0.00003 * sn(P + M - 2 * F)
        + 0.00003 * sn(3 * M) + 0.00002 * sn(2 * P - 2 * F) + 0.00002 * sn(P - M + 2 * F) - 0.00002 * sn(3 * P + M);
      var W = 0.00306 - 0.00038 * E * cs(M) + 0.00026 * cs(P) - 0.00002 * cs(P - M) + 0.00002 * cs(P + M) + 0.00002 * cs(2 * F);
      c += q === 1 ? W : -W;
    }
    var A = [299.77 + 0.107408 * k - 0.009173 * T2, 251.88 + 0.016321 * k, 251.83 + 26.651886 * k, 349.42 + 36.412478 * k, 84.66 + 18.206239 * k,
      141.74 + 53.303771 * k, 207.14 + 2.453732 * k, 154.84 + 7.306860 * k, 34.52 + 27.261239 * k, 207.19 + 0.121824 * k, 291.34 + 1.844379 * k,
      161.72 + 24.198154 * k, 239.56 + 25.513099 * k, 331.55 + 3.592518 * k];
    var AC = [0.000325, 0.000165, 0.000164, 0.000126, 0.000110, 0.000062, 0.000060, 0.000056, 0.000047, 0.000042, 0.000040, 0.000037, 0.000035, 0.000023];
    for (var i = 0; i < 14; i++) c += AC[i] * sn(A[i]);
    return jde + c;
  }
  function phaseMs(k) { return (phaseJDE(k) - deltaT(2000 + k / 12.3685) / 86400 - 2440587.5) * 864e5; }
  function phasesIn(ms0, ms1) { /* every phase with ms0 <= instant < ms1: [[q, ms]] */
    var y0 = 1970 + ms0 / 31556952e3, out = [], k = Math.floor((y0 - 2000) * 12.3685) - 1;
    for (var i = 0; i < 4000; i++) {
      var kk = k + i / 4, t = phaseMs(kk);
      if (t >= ms1) break;
      if (t >= ms0) out.push([((i % 4) + 4) % 4, t]);
    }
    return out;
  }
  function illum(ms, list) { /* phase angle (0 new, 180 full) by interpolating between the phases around ms */
    for (var i = 0; i < list.length - 1; i++) if (ms >= list[i][1] && ms < list[i + 1][1]) {
      var a = list[i][0] * 90 + 90 * (ms - list[i][1]) / (list[i + 1][1] - list[i][1]);
      return [a, (1 - cs(a)) / 2];
    }
    return [0, 0];
  }
  function moonSvg(a, sz) { /* waxing lit on the right (northern hemisphere) */
    var r = 10, rx = Math.abs(cs(a)) * r, wax = a < 180, gib = Math.abs(a - 180) < 90;
    var d = wax ? 'M0,-10A10,10 0 0 1 0,10A' + rx.toFixed(2) + ',10 0 0 ' + (gib ? 1 : 0) + ' 0,-10'
      : 'M0,-10A10,10 0 0 0 0,10A' + rx.toFixed(2) + ',10 0 0 ' + (gib ? 0 : 1) + ' 0,-10';
    return '<svg class="mo" width="' + sz + '" height="' + sz + '" viewBox="-11 -11 22 22" aria-hidden="true"><circle r="10" class="mo-d"/>' +
      (a > 1 && a < 359 ? '<path class="mo-l" d="' + d + '"/>' : '') + '</svg>';
  }
"""

# tzParts(ms, tz) -> {y, m, d, h, mi}; hm(ms, tz) -> 'HH:MM' (rounded to the minute)
TZ_JS = r"""
  var TZF = {};
  function tzParts(ms, tz) {
    var f = TZF[tz] || (TZF[tz] = new Intl.DateTimeFormat('en-GB', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false }));
    var o = {};
    f.formatToParts(new Date(ms)).forEach(function (p) { o[p.type] = +p.value; });
    return { y: o.year, m: o.month, d: o.day, h: o.hour % 24, mi: o.minute };
  }
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function hm(ms, tz) { var p = tzParts(Math.round(ms / 6e4) * 6e4, tz); return p2(p.h) + ':' + p2(p.mi); }
"""

# sunUtc(y, m, d, lat, lon, zen) -> {rise, noon, set}: UTC minutes after 00:00 UTC of that date (null if none)
SUN_JS = r"""
  function sunUtc(y, m, d, lat, lon, zen) {
    var R = Math.PI / 180, j0 = Date.UTC(y, m - 1, d) / 864e5 + 2440587.5;
    function at(mins) {
      var T = (j0 + mins / 1440 - 2451545) / 36525;
      var L0 = ((280.46646 + T * (36000.76983 + T * 0.0003032)) % 360 + 360) % 360;
      var M = 357.52911 + T * (35999.05029 - 0.0001537 * T), e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T);
      var C = Math.sin(M * R) * (1.914602 - T * (0.004817 + 0.000014 * T)) + Math.sin(2 * M * R) * (0.019993 - 0.000101 * T) + Math.sin(3 * M * R) * 0.000289;
      var lam = L0 + C - 0.00569 - 0.00478 * Math.sin((125.04 - 1934.136 * T) * R);
      var eps = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60 + 0.00256 * Math.cos((125.04 - 1934.136 * T) * R);
      var decl = Math.asin(Math.sin(eps * R) * Math.sin(lam * R)) / R, yy = Math.pow(Math.tan(eps / 2 * R), 2);
      var eot = 4 * (yy * Math.sin(2 * L0 * R) - 2 * e * Math.sin(M * R) + 4 * e * yy * Math.sin(M * R) * Math.cos(2 * L0 * R)
        - 0.5 * yy * yy * Math.sin(4 * L0 * R) - 1.25 * e * e * Math.sin(2 * M * R)) / R;
      return [decl, eot];
    }
    function ev(sign) {
      var t = 720 - 4 * lon;
      for (var i = 0; i < 3; i++) {
        var a = at(t), noon = 720 - 4 * lon - a[1];
        if (!sign) { t = noon; continue; }
        var x = Math.cos(zen * R) / (Math.cos(lat * R) * Math.cos(a[0] * R)) - Math.tan(lat * R) * Math.tan(a[0] * R);
        if (Math.abs(x) > 1) return null;
        t = noon + sign * 4 * Math.acos(x) / R;
      }
      return t;
    }
    return { rise: ev(-1), noon: ev(0), set: ev(1) };
  }
"""

# easter(y) -> Date (UTC midnight) Gregorian; easterOrth(y) -> Date (Gregorian date of the Orthodox Easter)
EASTER_JS = r"""
  function easter(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451), n = h + l - 7 * m + 114;
    return new Date(Date.UTC(y, Math.floor(n / 31) - 1, n % 31 + 1));
  }
  function easterOrth(y) {
    var a = y % 4, b = y % 7, c = y % 19, d = (19 * c + 15) % 30, e = (2 * a + 4 * b - d + 34) % 7, n = d + e + 114;
    return new Date(Date.UTC(y, Math.floor(n / 31) - 1, n % 31 + 1 + Math.floor(y / 100) - Math.floor(y / 400) - 2));
  }
"""

# Moon CSS shared by the two moon pages
MOON_CSS = (".mo{display:block;margin:1px auto 0}.mo-d{fill:#3b3f6b}.mo-l{fill:#f6e7a8}"
            ".ml td{height:40px;vertical-align:top}.ml td.ph{box-shadow:inset 0 0 0 2px #3b3f6b}.ml td small{display:block;font-size:10px;font-weight:700;line-height:1}"
            ".mt{width:100%;margin-top:16px}.mt td,.mt th{text-align:left}.mt td .mo{display:inline-block;vertical-align:-4px;margin:0 4px 0 0}")
