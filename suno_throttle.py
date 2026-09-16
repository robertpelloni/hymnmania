"""Throttled Suno upload runner - spreads uploads over 24h in small segments.

Suno occasionally rejects an upload with "COPYRIGHT MATCH" that succeeds on a later try,
so hammering it in one long run both risks account flagging and wastes attempts. This
runs a SMALL BATCH per invocation and is driven by a Windows scheduled task repeating
through the day.

    python suno_throttle.py --plan          # show the queue
    python suno_throttle.py --run           # do one batch (default 3 uploads)
    python suno_throttle.py --run --n 5     # custom batch size
    python suno_throttle.py --rebuild       # rebuild the queue from hymns x sub-genres
    python suno_throttle.py --status

Defaults: 3 uploads per run, every 2 h -> 12 runs/day -> 36 uploads/day.
Each upload becomes one generation (10 credits).
"""
import os, re, sys, json, time, random, subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
GEN = os.path.join(ROOT, "generated")
MIDI_DIR = os.path.join(ROOT, "submodules", "ableton_psytrance_hymn_creator",
                        "hymnmania_src", "hymn_remaker", "input")
RENDER = os.path.join(ROOT, "scripts", "audio_synthesis_render_midi_to_sine_wave_clean.py")
QUEUE = os.path.join(ROOT, ".upload_queue.json")
STATE = os.path.join(ROOT, ".throttle_state.json")
TEMPO = os.path.join(ROOT, ".psytrance_tempo.json")
SUB = os.path.join(ROOT, "psytrance_subgenres.json")

BATCH = 3               # uploads per invocation
GAP = 75                # seconds between uploads inside a batch
DAILY_CAP = 36          # uploads/day across all runs


def jload(p, d):
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            pass
    return d


def jsave(p, o):
    json.dump(o, open(p, "w", encoding="utf-8"), indent=1)


def safe(h):
    return re.sub(r"[^A-Za-z0-9]+", "_", h).strip("_")


def midi_for(hymn):
    p = os.path.join(MIDI_DIR, hymn + ".mid")
    if os.path.exists(p):
        return p
    want = re.sub(r"[^a-z0-9]", "", hymn.lower())
    for f in os.listdir(MIDI_DIR):
        if f.lower().endswith(".mid") and re.sub(r"[^a-z0-9]", "", f[:-4].lower()) == want:
            return os.path.join(MIDI_DIR, f)
    return None


def rebuild():
    """Build every (hymn, sub-genre) job and work out the speed needed per job."""
    sg = {k: v for k, v in jload(SUB, {}).items() if not k.startswith("_")}
    tstate = jload(TEMPO, {})
    hymns = [h for h, v in tstate.items() if v.get("natural_bpm") and midi_for(h)]
    jobs = []
    for h in hymns:
        nat = tstate[h]["natural_bpm"]
        for g, meta in sg.items():
            out = os.path.join(GEN, f"{safe(h)}_10x_{g}_A_cover.mp3")
            if os.path.exists(out) and os.path.getsize(out) > 500000:
                continue
            speed = round(max(0.5, min(3.0, meta["bpm"] / nat)), 3)
            jobs.append({"hymn": h, "genre": g, "speed": speed,
                         "target": meta["bpm"], "label": meta["label"],
                         "status": "pending", "tries": 0, "clip": None})
    # Full-On first (2x weight), then the rest
    jobs.sort(key=lambda j: (-sg[j["genre"]]["weight"], j["hymn"]))
    jsave(QUEUE, jobs)
    print(f"queue rebuilt: {len(jobs)} jobs ({len(hymns)} hymns x {len(sg)} sub-genres)")
    return jobs


def status():
    q = jload(QUEUE, [])
    st = jload(STATE, {})
    today = time.strftime("%Y-%m-%d")
    done_today = st.get("days", {}).get(today, 0)
    from collections import Counter
    c = Counter(j.get("status", "pending") for j in q)
    print(f"queue total     : {len(q)}")
    for k, v in sorted(c.items()):
        print(f"   {k:10s}: {v}")
    print(f"uploads today   : {done_today}/{DAILY_CAP}")
    print(f"covers produced : {len([j for j in q if j.get('status')=='done'])}")


def run(n=BATCH):
    q = jload(QUEUE, [])
    st = jload(STATE, {})
    if not q:
        print("queue empty - run --rebuild")
        return
    today = time.strftime("%Y-%m-%d")
    st.setdefault("days", {})
    done_today = st["days"].get(today, 0)
    if done_today >= DAILY_CAP:
        print(f"daily cap reached ({done_today}/{DAILY_CAP}) - skipping")
        return
    n = min(n, DAILY_CAP - done_today)

    pending = [j for j in q if j.get("status") in (None, "pending", "retry")]
    print(f"batch: {n} of {len(pending)} pending (uploads today {done_today}/{DAILY_CAP})")
    did = 0
    for j in pending:
        if did >= n:
            break
        hymn, g, speed = j["hymn"], j["genre"], j["speed"]
        print(f"\n[{did+1}/{n}] {hymn} / {j['label']} (target {j['target']} BPM, speed {speed}x)",
              flush=True)
        midi = midi_for(hymn)
        wav = os.path.join(ROOT, "mp3_input", f"_thr_{safe(hymn)}_{g}.wav")
        if not (os.path.exists(wav) and os.path.getsize(wav) > 100000):
            r = subprocess.run([PY, RENDER, "--midi", midi, "--wav", wav, "--speed", str(speed)],
                               capture_output=True, text=True, timeout=900)
            if not os.path.exists(wav):
                print("   render failed"); j["status"] = "retry"; j["tries"] += 1; continue

        from upload_helper import upload_with_fallback
        cid = upload_with_fallback(wav)
        if not cid or cid == "BLOCKED":
            j["status"] = "retry"
            j["tries"] = j.get("tries", 0) + 1
            # after 3 failed tries, park it so we move on
            if j["tries"] >= 3:
                j["status"] = "parked"
                print("   parked after 3 tries")
            else:
                print("   will retry next run")
            jsave(QUEUE, q)
            time.sleep(GAP)
            continue

        gm = subprocess.run([PY, os.path.join(ROOT, "gen_only.py"), g, cid, hymn],
                            capture_output=True, text=True, timeout=1800)
        m = re.search(r"CLIPS:([0-9a-f,\-]+)", gm.stdout or "")
        if not m:
            print("   generation failed"); j["status"] = "retry"; j["tries"] += 1
            jsave(QUEUE, q); continue
        clip = m.group(1).split(",")[0]
        j["clip"] = clip
        out = os.path.join(GEN, f"{safe(hymn)}_10x_{g}_A_cover.mp3")
        try:
            subprocess.run([PY, os.path.join(ROOT, "cap_cycle.py"), clip, out],
                           capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            print("   capture timed out")
        if os.path.exists(out):
            # Genre EQ: without this the capture stays melody-forward and bright, which is
            # why a "Full-On psytrance" cover did not sound like psytrance. Mastered in
            # place (low end 20% -> 45%, highs 42% -> 20% on the measured sample).
            try:
                from master_cover import master
                master(out, out, g)
                print("   mastered (genre EQ)")
            except Exception as e:
                print(f"   mastering skipped: {e}")
        j["status"] = "done" if os.path.exists(out) else "captured_failed"
        j["tries"] = j.get("tries", 0) + 1
        did += 1
        st["days"][today] = st["days"].get(today, 0) + 1
        jsave(QUEUE, q); jsave(STATE, st)
        print(f"   -> {j['status']}  (uploads today {st['days'][today]}/{DAILY_CAP})", flush=True)
        if did < n:
            time.sleep(GAP)
    jsave(QUEUE, q); jsave(STATE, st)
    print(f"\nbatch done: {did} processed, {st['days'][today]}/{DAILY_CAP} uploads today")


def main():
    a = sys.argv[1:]
    if "--rebuild" in a:
        rebuild(); return
    if "--plan" in a or "--status" in a:
        status(); return
    if "--run" in a:
        n = BATCH
        if "--n" in a:
            n = int(a[a.index("--n") + 1])
        run(n); return
    status()


if __name__ == "__main__":
    main()
