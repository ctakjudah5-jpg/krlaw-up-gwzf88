# -*- coding: utf-8 -*-
# ---------------------------------------------------------------
# Upgrade the lecture's law-axtax server in C:\krlaw to the
# instructor's latest release.
# AI 세무실무 강의 수강생 개인 실습용 — 재배포 금지
#
# It touches nothing unless C:\krlaw is the lecture folder: the folder
# must exist, must not be empty, and must hold the lecture code
# (my_law_server.py serving "law-axtax", plus setup_key.py or
# 07_register.py saved from the lecture repository). Missing, empty,
# or someone else's code: it stops with nothing changed.
#
# When it does run:
#   1) download law_mcp_server.py from this repository and check its
#      SHA-256 against RELEASE below
#   2) copy the files about to change into C:\krlaw\backup\<time>\
#   3) write the new server, then turn my_law_server.py into a short
#      start file. The app keeps launching my_law_server.py, so the
#      registration made in lecture step 7 needs no change.
#   4) start the server once (initialize + tools/list) and compare the
#      version and tool count; on a mismatch the old files go back.
#
# The key in law_oc.txt is read only by the start file and never
# printed. The Claude app's own files are never opened.
#
#   python -I upgrade.py                      upgrade (or report "이미 최신")
#   python -I upgrade.py --check              look only; changes nothing
#   python -I upgrade.py --rollback           one step back: the files of the last backup
#   python -I upgrade.py --rollback --check   show where a rollback would go; changes nothing
# ---------------------------------------------------------------
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---- release: rewritten by the instructor's build script ----
VERSION = "2.13.1"
TOOL_COUNT = 36
RELEASE = {
    "law_mcp_server.py": "6008fc8a027aafeae1419bf5a2dbe23463dfdd84dbf3cf9ae05e1d6784b45da2",
    "THIRD_PARTY_NOTICES.txt": "58feb375981108a095665ce6d805a095d883bf619e984b740f633c829a433a62",
}
# ---- end release ----

ROOT = r"C:\krlaw"
RAW = "https://raw.githubusercontent.com/ctakjudah5-jpg/krlaw-up-gwzf88/main/"
ENTRY = "my_law_server.py"      # the file the Claude app runs (lecture step 7)
CORE = "law_mcp_server.py"
NOTICE = "THIRD_PARTY_NOTICES.txt"
BACKUP = "backup"
USED = "-restored"              # suffix of a backup folder already put back
TAG = "# krlaw-upgrade start file"

# The same two lines setup_key.py writes at the top of my_law_server.py.
STAMP_1 = "# 제작: {name} · AI 세무실무 강의 실습 · {date}"
STAMP_2 = "# 개인 실습용 도구 — 재배포 금지"

# Lines found in the lecture files saved verbatim from krlaw-cu9yik.
# Matched as patterns, not hashes, so a copy re-saved with CRLF still counts.
LECTURE_FILES = {
    "setup_key.py": (r'FOLDER\s*=\s*r?["\']C:\\krlaw["\']', r"law_oc\.txt"),
    "07_register.py": (r'SERVER_NAME\s*=\s*["\']law-axtax["\']', r"C:\\krlaw\\my_law_server\.py"),
}

START_FILE = r'''@STAMP1@
@STAMP2@
@TAG@ · law-axtax @VERSION@
# ---------------------------------------------------------------
# Start file written by upgrade.py. The Claude app still runs THIS
# file (registered in lecture step 7), so nothing needs re-registering.
#   1) read the key setup_key.py saved in law_oc.txt (never printed)
#   2) run law_mcp_server.py, the instructor's server, in this process
# The previous my_law_server.py is kept in backup\<date-time>\.
# ---------------------------------------------------------------
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "law_mcp_server.py")
KEY_FILE = os.path.join(HERE, "law_oc.txt")


def read_key():
    """The saved key, or "" -- never printed or logged."""
    try:
        with open(KEY_FILE, encoding="utf-8-sig") as f:
            return f.read().strip().strip("\"'").strip()
    except OSError:
        return ""


def main():
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.stderr.write("개인 실습용 도구입니다 (AI 세무실무 강의 실습) — 재배포 금지\n")
    if not os.environ.get("LAW_OC"):
        key = read_key()
        if key:
            os.environ["LAW_OC"] = key
        else:
            sys.stderr.write("law-axtax: 인증키가 없습니다 — C:\\krlaw\\setup_key.py 를 실행해 넣으세요\n")
    os.environ.setdefault("LAW_VAULT", "0")   # the instructor's office notes are not reachable here
    sys.argv = [SERVER]
    runpy.run_path(SERVER, run_name="__main__")


if __name__ == "__main__":
    main()
'''


class Stop(Exception):
    """Ends the run with a '중단' line."""


def say(text=""):
    print(text, flush=True)


def read_text(path):
    """A file's text for pattern checks, whatever its encoding. "" if unreadable."""
    try:
        with open(path, "rb") as f:
            raw = f.read(2000000)
    except OSError:
        return ""
    for enc in ("utf-8-sig", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    try:
        with open(path, "rb") as f:
            return sha256(f.read())
    except OSError:
        return ""


# ---- what C:\krlaw holds (read only) ---------------------------
def inspect(root):
    """-> (state, why). state: missing | empty | foreign | lecture | upgraded."""
    if not os.path.isdir(root):
        return "missing", "%s 폴더가 없습니다" % root
    try:
        names = os.listdir(root)
    except OSError as e:
        return "missing", "%s 폴더를 읽지 못했습니다 (%s)" % (root, e)
    if not names:
        return "empty", "%s 폴더가 비어 있습니다" % root
    entry = read_text(os.path.join(root, ENTRY))
    if not entry.strip():
        return "foreign", "%s 가 없습니다 — 강의 실습 서버가 없는 폴더입니다" % ENTRY
    if TAG in entry:
        return "upgraded", "전에 업그레이드한 강의 실습 폴더입니다"
    if "law-axtax" not in entry or "jsonrpc" not in entry:
        return "foreign", "%s 가 강의 실습 서버(law-axtax)가 아닙니다 — 다른 코드입니다" % ENTRY
    matched = [fn for fn, pats in LECTURE_FILES.items()
               if all(re.search(p, read_text(os.path.join(root, fn))) for p in pats)]
    if not matched:
        return "foreign", "setup_key.py · 07_register.py 가 강의 저장소의 파일이 아닙니다 — 다른 코드입니다"
    return "lecture", "강의 실습 폴더입니다 (%s 확인)" % " · ".join([ENTRY] + matched)


def stamp_lines(root, today=None):
    """Keep the student's name stamp; rebuild it from owner.txt when absent."""
    lines = read_text(os.path.join(root, ENTRY)).splitlines()
    if len(lines) >= 2 and lines[0].startswith("# 제작:") and lines[1].startswith("# 개인 실습용 도구"):
        return lines[0], lines[1]
    owner = read_text(os.path.join(root, "owner.txt")).strip().splitlines()
    name = (owner[0].strip() if owner else "")[:40] or "수강생"
    return STAMP_1.format(name=name, date=today or datetime.date.today().isoformat()), STAMP_2


def start_file(stamp):
    text = START_FILE.replace("@TAG@", TAG).replace("@VERSION@", VERSION)
    return text.replace("@STAMP1@", stamp[0]).replace("@STAMP2@", stamp[1])


def is_latest(root):
    entry = read_text(os.path.join(root, ENTRY)).replace("\r\n", "\n")
    return (all(file_sha(os.path.join(root, n)) == want for n, want in RELEASE.items())
            and entry == start_file(stamp_lines(root)))


def server_version(folder):
    """Which server a folder (C:\\krlaw or one backup) holds."""
    entry = read_text(os.path.join(folder, ENTRY))
    if TAG in entry:
        m = re.search(r'SERVER_VERSION\s*=\s*"([^"]+)"', read_text(os.path.join(folder, CORE)))
        return "law-axtax v%s (업그레이드판)" % (m.group(1) if m else "?")
    return "강의 실습판" if "law-axtax" in entry else "알 수 없음"


def has_key(root):
    p = os.path.join(root, "law_oc.txt")
    return os.path.isfile(p) and os.path.getsize(p) > 0      # size only; the value is never read here


# ---- download · write · check -----------------------------------
def fetch(name):
    """One file from this repository's main branch -> bytes."""
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(RAW + name, headers={"User-Agent": "krlaw-upgrade",
                                                              "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read(20000000)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Stop("저장소에서 %s 를 찾지 못했습니다 — 저장소가 닫혀 있을 수 있습니다(강사에게 문의). "
                           "아무것도 바꾸지 않았습니다." % name)
            last = e
        except (urllib.error.URLError, OSError) as e:
            last = e
        time.sleep(2 * (attempt + 1))
    raise Stop("저장소에 닿지 못했습니다(인터넷 연결 확인) — %s. 아무것도 바꾸지 않았습니다." % last)


def write_atomic(path, data):
    with open(path + ".new", "wb") as f:
        f.write(data)
    os.replace(path + ".new", path)


def new_backup_dir(root):
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    base = os.path.join(root, BACKUP, stamp)
    path, n = base, 0
    while os.path.exists(path):
        n += 1
        path = "%s-%d" % (base, n)
    os.makedirs(path)
    return path


def put_back(bdir, root):
    """Copy every file of one backup folder back into root."""
    names = sorted(os.listdir(bdir))
    for name in names:
        shutil.copy2(os.path.join(bdir, name), os.path.join(root, name))
    return names


def probe(root):
    """Start my_law_server.py once: initialize + tools/list -> (version, tool count, error)."""
    msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "krlaw-upgrade", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
    env = {k: v for k, v in os.environ.items() if k.upper() != "LAW_OC"}
    try:
        r = subprocess.run([sys.executable, os.path.join(root, ENTRY)], cwd=root, env=env,
                           input="".join(json.dumps(m) + "\n" for m in msgs).encode("utf-8"),
                           capture_output=True, timeout=120)
    except Exception as e:
        return None, 0, str(e)[:160]
    version, count = None, 0
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("id") == 1:
            version = ((d.get("result") or {}).get("serverInfo") or {}).get("version")
        elif d.get("id") == 2:
            count = len((d.get("result") or {}).get("tools") or [])
    err = r.stderr.decode("utf-8", "replace").strip().splitlines()
    return version, count, ("" if version else (err[-1][:160] if err else "응답 없음"))


# ---- the two jobs -----------------------------------------------
def upgrade(root, check_only=False):
    state, why = inspect(root)
    say("  폴더      : %s" % why)
    if state not in ("lecture", "upgraded"):
        raise Stop("업그레이드하지 않았습니다. 이 업그레이드는 강의 실습을 마친 PC 의 C:\\krlaw 에서만 합니다"
                   "(폴더가 없거나 · 비었거나 · 강의 실습 코드가 아니면 진행하지 않음). 아무것도 바꾸지 않았습니다.")
    key = has_key(root)
    say("  지금 서버 : %s" % server_version(root))
    say("  새 판     : law-axtax v%s · 도구 %d개" % (VERSION, TOOL_COUNT))
    say("  인증키    : %s (값은 보지 않습니다)" % ("있음" if key else "없음"))
    if state == "upgraded" and is_latest(root):
        say("")
        say("이미 최신 — law-axtax v%s 가 이미 들어 있습니다. 바꾼 것이 없습니다." % VERSION)
        return 0
    if check_only:
        say("")
        say("보기만 했습니다 — 업그레이드할 수 있는 폴더입니다. 아무것도 바꾸지 않았습니다.")
        return 0
    if sys.version_info < (3, 8):
        raise Stop("파이썬 3.8 이상이 필요합니다(지금 %s). 아무것도 바꾸지 않았습니다." % sys.version.split()[0])

    blobs = {}
    for name, want in RELEASE.items():
        data = fetch(name)
        if sha256(data) != want:
            raise Stop("받은 %s 가 이 판(v%s)과 맞지 않습니다 — 저장소가 막 바뀌는 중일 수 있으니 5분 뒤 다시 하세요. "
                       "아무것도 바꾸지 않았습니다." % (name, VERSION))
        blobs[name] = data
    try:
        compile(blobs[CORE], CORE, "exec")         # never write a server Python cannot read
    except SyntaxError as e:
        raise Stop("받은 서버 파일을 파이썬이 읽지 못합니다(%s). 아무것도 바꾸지 않았습니다." % e)

    stamp = stamp_lines(root)                      # read before my_law_server.py is replaced
    bdir = new_backup_dir(root)
    saved = []
    for name in (ENTRY, CORE, NOTICE):
        src = os.path.join(root, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(bdir, name))
            if file_sha(os.path.join(bdir, name)) != file_sha(src):
                raise Stop("백업을 확인하지 못했습니다(%s). 아무것도 바꾸지 않았습니다." % name)
            saved.append(name)
    say("  백업      : %s (%s)" % (bdir, " · ".join(saved)))

    try:
        write_atomic(os.path.join(root, CORE), blobs[CORE])
        write_atomic(os.path.join(root, NOTICE), blobs[NOTICE])
        write_atomic(os.path.join(root, ENTRY), start_file(stamp).encode("utf-8"))   # the switch, last
    except OSError as e:
        put_back(bdir, root)
        raise Stop("파일을 쓰지 못해(%s) 원래 파일로 되돌렸습니다." % e)

    version, count, err = probe(root)
    if version != VERSION or count != TOOL_COUNT:
        put_back(bdir, root)
        raise Stop("새 서버가 제대로 뜨지 않아(%s) 원래 파일로 되돌렸습니다."
                   % (err or "v%s · 도구 %d개" % (version, count)))
    say("  바꿈      : %s → 시작 파일 · %s → law-axtax v%s" % (ENTRY, CORE, VERSION))
    say("  확인      : 새 서버를 띄워 봄 — v%s · 도구 %d개" % (version, count))
    if not key:
        say("  ※ 인증키가 없습니다 — 앱을 다시 켜기 전에 C:\\krlaw\\setup_key.py 를 실행해 키를 넣으세요.")
    say("")
    say("완료 — Claude 앱을 완전히 종료한 뒤(작업 표시줄 트레이의 Claude 아이콘 우클릭 → 종료, "
        "또는 작업 관리자에서 Claude 끝내기) 다시 켜면 새 도구 %d개가 뜹니다." % TOOL_COUNT)
    return 0


def backups(root):
    """Backup folders not yet put back, oldest first."""
    base = os.path.join(root, BACKUP)
    if not os.path.isdir(base):
        return []
    return sorted(d for d in os.listdir(base)
                  if re.fullmatch(r"\d{8}-\d{6}(-\d+)?", d) and os.path.isfile(os.path.join(base, d, ENTRY)))


def rollback(root, check_only=False):
    """One step back: put back the newest unused backup, then mark it used."""
    state, why = inspect(root)
    if state in ("missing", "empty"):
        raise Stop("%s — 되돌릴 것이 없습니다." % why)
    found = backups(root)
    if not found:
        raise Stop("되돌릴 백업이 없습니다(%s). 아무것도 바꾸지 않았습니다." % os.path.join(root, BACKUP))
    bdir = os.path.join(root, BACKUP, found[-1])
    target = server_version(bdir)
    say("  지금 서버 : %s" % server_version(root))
    say("  되돌릴 곳 : %s (backup\\%s · %s)" % (target, found[-1], " · ".join(sorted(os.listdir(bdir)))))
    if check_only:
        say("")
        say("보기만 했습니다 — 되돌리면 %s으로 바뀝니다. 아무것도 바꾸지 않았습니다." % target)
        return 0
    put_back(bdir, root)
    try:
        os.rename(bdir, bdir + USED)      # the next rollback goes one step further back
    except OSError:
        pass
    more = " 한 번 더 되돌리면 그 앞 단계로 갑니다." if len(found) > 1 else ""
    say("")
    say("되돌림 — %s으로 되돌렸습니다. Claude 앱을 완전히 종료한 뒤 다시 켜세요.%s" % (target, more))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="C:\\krlaw 법령검색도구(law-axtax) 업그레이드")
    ap.add_argument("--check", action="store_true", help="보기만(아무것도 안 바꿈) · --rollback 과 함께 쓰면 되돌릴 곳만 봄")
    ap.add_argument("--rollback", action="store_true", help="마지막 업그레이드 전으로 한 단계 되돌림")
    a = ap.parse_args(argv)
    say("== 법령검색도구 업그레이드 — law-axtax v%s · 도구 %d개 ==" % (VERSION, TOOL_COUNT))
    try:
        return rollback(ROOT, a.check) if a.rollback else upgrade(ROOT, a.check)
    except Stop as e:
        say("")
        say("중단 — %s" % e)
        return 1
    except Exception as e:                # anything unforeseen: one plain line, not a traceback
        say("")
        say("중단 — 예상하지 못한 오류입니다(%s: %s). C:\\krlaw\\backup 에 백업이 있으면 --rollback 으로 "
            "되돌릴 수 있습니다. 이 줄을 강사에게 알려 주세요." % (type(e).__name__, e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
