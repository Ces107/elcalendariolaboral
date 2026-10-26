"""Vacation optimizer 2027: reference implementation. The /vacaciones-2027/ static pages and test_vacopt.py use it;
optimize() in vac.js is the same algorithm step by step (test_vacopt.py runs both and compares).

Objective: "días libres seguidos", the way the press counts puentes. A BREAK is a maximal run of consecutive days off
(weekends, holidays and vacation) that holds at least one vacation day. The plan's total is the sum of the lengths
of its breaks. A break must last at least `min_len` days (default 5: the classic puente, Sat-Wed or Thu-Mon) and at
most `max_len` (0 = no limit). Without a minimum the optimum is a lone Friday or Monday every week (3 days for 1),
which nobody plans; from 5 days on it is puentes and whole weeks.

Days the user already took (`taken`) count against the n days and are always kept. A break that holds a taken day
is exempt from the minimum, and from the maximum while it adds no new day. Blocked months get no new vacation day
(their weekends and holidays can still be part of a break that starts or ends in another month).

Exact DP over the 365 days. f[i][u] = best total for days 0..i-1 using u vacation days, where day i-1 is a working
day left as working (or i = 0). From (i, u):
  keep:  day i stays as it is (not a taken day)                          -> (i+1, u)
  break: only if i == 0 or day i-1 is a working day. It runs i..e, day e+1 is a working day (or e = 31 Dec),
         every working day in i..e is vacation (c of them, c >= 1); day e+1 is left working and must not be a
         taken day                                                        -> (e+2, u+c), + (e-i+1)
Ties keep the first option found (i ascending, u ascending, keep before break, shorter break first), and the end
state with the fewest days used, in both languages.
"""
import datetime as dt

YEAR = 2027
N = 365
DAYS = [dt.date(YEAR, 1, 1) + dt.timedelta(i) for i in range(N)]
MIN_BREAK = 5
MAX_DAYS = 30


def off_days(hol_dates):
    hd = set(hol_dates)
    return [d.weekday() >= 5 or d.isoformat() in hd for d in DAYS]


def candidates(off, i, taken, blocked, cap, min_len, n):
    """Valid breaks starting at day i, shortest first: [(e, cost, length)]."""
    out = []
    c = tk = 0
    e = i
    while e < N:
        if not off[e]:
            if e in taken:
                tk += 1
            elif DAYS[e].month - 1 in blocked:
                break
            c += 1
            if c > n:
                break
        ln = e - i + 1
        new = c - tk
        if new > 0 and ln > cap:
            break
        if c >= 1 and (e + 1 >= N or not off[e + 1]) and (e + 1 >= N or (e + 1) not in taken):
            if (tk > 0 and new == 0) or (ln <= cap and (ln >= min_len or tk > 0)):
                out.append((e, c, ln))
        e += 1
    return out


def optimize(off, n, taken=(), blocked_months=(), max_len=0, min_len=MIN_BREAK):
    """off: 365 bools. n: vacation days. taken: day indexes already booked (off days are ignored).
    blocked_months: 0-11. Returns {"total", "used", "breaks": [{"s", "e", "len", "take": [...]}]} or None."""
    taken = {i for i in taken if 0 <= i < N and not off[i]}
    n = max(n, len(taken))
    blocked = set(blocked_months)
    cap = max_len if max_len and max_len > 0 else N
    min_len = min(min_len, cap)
    f = [[-1] * (n + 1) for _ in range(N + 2)]
    back = [[None] * (n + 1) for _ in range(N + 2)]
    f[0][0] = 0
    for i in range(N):
        row, nxt = f[i], f[i + 1]
        cands = None
        can_start = i == 0 or not off[i - 1]
        for u in range(n + 1):
            v = row[u]
            if v < 0:
                continue
            if i not in taken and nxt[u] < v:
                nxt[u], back[i + 1][u] = v, (i, u, None)
            if not can_start:
                continue
            if cands is None:
                cands = candidates(off, i, taken, blocked, cap, min_len, n)
            for e, c, ln in cands:
                if u + c > n:
                    break
                j = N + 1 if e + 1 >= N else e + 2
                if f[j][u + c] < v + ln:
                    f[j][u + c], back[j][u + c] = v + ln, (i, u, (i, e))
    best, bu, bj = -1, 0, 0
    for u in range(n + 1):
        for j in (N, N + 1):
            if f[j][u] > best:
                best, bu, bj = f[j][u], u, j
    if best < 0:
        return None
    breaks = []
    j, u = bj, bu
    while j > 0:
        pi, pu, br = back[j][u]
        if br:
            s, e = br
            breaks.append({"s": s, "e": e, "len": e - s + 1, "take": [k for k in range(s, e + 1) if not off[k]]})
        j, u = pi, pu
    breaks.reverse()
    return {"total": best, "used": bu, "breaks": breaks}


# ---------------------------------------------------------------- labels (same as breakName() in vac.js)

def break_name(b, hols):
    """'Semana Santa', 'Navidad', the holidays in the break joined by ' · ', or the month(s)."""
    s, e = DAYS[b["s"]].isoformat(), DAYS[b["e"]].isoformat()
    if s <= "2027-03-26" and e >= "2027-03-25":
        return "Semana Santa"
    if e >= "2027-12-24" or s <= "2027-01-06":
        return "Navidad"
    names = [h["name"] for h in hols if s <= h["date"] <= e and DAYS.__getitem__(_idx(h["date"])).weekday() < 5]
    if names:
        return " · ".join(dict.fromkeys(names))
    ms = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    a, z = DAYS[b["s"]].month - 1, DAYS[b["e"]].month - 1
    return ms[a].capitalize() if a == z else f"{ms[a].capitalize()}-{ms[z]}"


def _idx(iso):
    return (dt.date.fromisoformat(iso) - DAYS[0]).days
