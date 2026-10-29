#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국가법령정보센터(법제처) Open API — 로컬 MCP 서버  [자체 제작 / 외부 패키지 0]
================================================================================
세무자문 프로젝트 전용. 클로드가 대화창에서 판례·조세심판원 심판례·법령해석례·법령을
법제처 '공식' Open API로 직접 조회하도록 MCP 도구를 제공합니다.

설계 원칙
  - 외부 라이브러리 0개  (Python 3.8+ 표준 라이브러리만 사용)
  - 공식 엔드포인트만 호출:  https://www.law.go.kr/DRF/lawSearch.do , /lawService.do
  - 인증: 법제처 OC 키(환경변수 LAW_OC). 제3자 서버 경유 없음.
  - 전 코드가 한 파일에 있으며 누구나 검수 가능.
  - 착상 · API 사실 참고: chrisryugj/korean-law-mcp (MIT). 2026-06 첫 개발(법제처 변수 확인)과 2026-08 국세청
    본문 폴백 때 그 소스를 참고했다. 2026-10-13 클린룸 점검(따로 띄운 점검자가 대조)에서 닮은 조각 7곳을 찾아
    공식 안내 · 실측만으로 새로 짰다(v2.11.2). v2.9 이후 기능은 처음부터 기능만 견주어 보고 새로 짰다.

제공 도구(36개)
  ── v2.13 (2026-10) 더함 ──
  search_nts_precedents  국세법령정보시스템 판례 · 결정례 검색(법원 판결 · 조세심판 · 이의신청 · 심사 · 과세전적부심사 ·
                         결과 구분 국승 · 기각 …) — 본문은 get_tax_interpretation(offset · find 로 긴 판결도 끝까지)
  ── v2.11 (2026-10) 더함 ──
  article_history        조문 연혁(신설 · 개정 · 삭제 판마다 한 줄 · 법제처 lsJoHstInf)
  get_basic_rule         국세 기본통칙 본문(국세법령정보시스템 · 15개 법 · 연도 판)
  get_execution_standard 세법집행기준 목차 · PDF 쪽(본문은 연도별 PDF)
  search_nts_rulings     국세청 · 기재부 해석 검색(국세법령정보시스템 통합검색 — 법제처 목록 밖 해석도)
  ── v2.10 (2026-10) 더함 ──
  compare_versions       신구 조문 대조(두 판 · 표는 칸 글자 기준 · 다른 글자 ⟦ ⟧) · 디스크 캐시(판 고정 본문)
  ── v2.9 (2026-10) 더함 ──
  verify_citations       글 속 법령 인용 일괄 검증(✓ ✗ ⌛ ⊘ ⚠ · 약칭 · 같은 법 · 열거 · 범위)
  law_as_of              행위시법 한 번에(그날 판 + 조문 + 그 뒤 개정 · 시행예정 + 부칙 발췌)
  list_annexes           별표 · 서식 목록(법령 이름 · 날짜로)
  get_annex              별표 · 서식 한 건(긴 표 쪽 나눔 · 행 고르기)
  ── 그 전 ──
  search_precedents      판례 검색            (target=prec)
  get_precedent          판례 전문            (target=prec)
  search_tax_tribunal    조세심판원 심판례 검색 (target=ttSpecialDecc)
  get_tax_tribunal       조세심판원 심판례 전문 (target=ttSpecialDecc)
  search_interpretations 법제처 법령해석례 검색 (target=expc)
  get_interpretation     법령해석례 전문       (target=expc)
  search_law             법령 검색 · 이름이 정확히 같은 법령 맨 앞 (target=law)
  get_law_article        법령 조문 전문(조-항-호-목) (target=eflaw)
  get_law_appendix       법령 별표 본문(표·목록) (target=eflaw 별표노드)
  get_law_addenda        법령 부칙(시행일·적용례) (target=eflaw 부칙노드, 공포번호 누적)
  list_law_history       법령 시행일 연혁 · 판 상태(현행 · 연혁 · 시행예정) (target=eflaw, efYd 범위)
  search_admin_rule      행정규칙 검색(국세청 예규 등) (target=admrul, org=1210000)
  get_admin_rule         행정규칙 전문         (target=admrul)
  verify_citation        인용 실존 검증(판례·법령·심판례·해석)
  search_constitutional  헌법재판소 결정례 검색 (target=detc)
  get_constitutional     헌재 결정례 전문      (target=detc)
  search_admin_appeal    행정심판 재결례 검색   (target=decc)
  get_admin_appeal       행정심판 재결례 전문   (target=decc)
  search_ordinance       자치법규(조례·규칙) 검색 (target=ordin)
  get_ordinance          자치법규 전문         (target=ordin)
  search_english_law     영문법령 검색         (target=elaw)
  get_english_law        영문법령 전문         (target=elaw)
  get_law_structure      법령 체계도(시행령·규칙 연계) (target=lsStmd)
  search_law_appendix    별표·서식 검색         (target=licbyl)
  search_tax_interpretation 국세청·기재부·관세청 세법해석 검색 (target=ntsCgmExpc 등)
  get_tax_interpretation 세법해석 전문 (관세청=법제처 API, 국세청·기재부=국세법령정보시스템 · 판례 · 결정례 본문도)

사용
  1) 환경변수 LAW_OC 에 본인 OC 키 설정
  2) 데스크톱 앱(MCP 클라이언트)이 stdio 로 이 스크립트를 실행
  자체 점검:  python law_mcp_server.py --selftest --oc 본인키
  도구 목록:  python law_mcp_server.py --list-tools
"""

import sys
import os
import json
import re
import html
import html.parser
import ssl
import gzip
import socket
import tempfile
import time
import random
import hashlib
import calendar
import email.utils
import threading
import logging
import logging.handlers
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

# ----- Windows 한글 안전: stdio 를 UTF-8 로 고정 -----
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SERVER_NAME = "law-axtax"   # 2026-10-11 이름 통일(옛 이름 kr-law)
SERVER_VERSION = "2.13.1"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# ----- 동작 파라미터 (모두 환경변수로 조정 가능) -----
TIMEOUT = int(os.environ.get("LAW_TIMEOUT", "25"))          # urlopen 1회 소켓 타임아웃(초)
DEADLINE = int(os.environ.get("LAW_DEADLINE", "35"))        # http_get 전체 벽시계 상한(초)
MAX_TEXT = int(os.environ.get("LAW_MAX_TEXT", "12000"))     # 전문(get_*) 단일 응답 최대 길이(자)
MAX_SEARCH_TEXT = int(os.environ.get("LAW_MAX_SEARCH_TEXT", "6000"))  # 검색 목록 전체 최대 길이(자)
DEFAULT_DISPLAY = int(os.environ.get("LAW_DEFAULT_DISPLAY", "10"))    # 검색 기본 결과 수
MAX_DISPLAY = int(os.environ.get("LAW_MAX_DISPLAY", "100"))           # 검색 결과 수 상한
MAX_WORKERS = int(os.environ.get("LAW_MAX_WORKERS", "4"))             # tools/call 동시 처리 상한
CACHE_TTL = int(os.environ.get("LAW_CACHE_TTL", "3600"))             # 검색 캐시 유효(초) — F7 1시간, 0=비활성
CACHE_TTL_DETAIL = int(os.environ.get("LAW_CACHE_TTL_DETAIL", "86400"))  # 전문(lawService) — F7 하루(현행 전문은 열쇠에 날짜가 들어가 자정에 새로)
DISK_CACHE = os.environ.get("LAW_DISK_CACHE", "1").strip().lower() not in ("0", "false", "no")
DISK_CACHE_MAX_BYTES = int(os.environ.get("LAW_DISK_CACHE_MAX_BYTES", str(300 * 1024 * 1024)))
CACHE_MAX = int(os.environ.get("LAW_CACHE_MAX", "128"))             # 캐시 항목 수 상한(LRU)
CACHE_MAX_BYTES = int(os.environ.get("LAW_CACHE_MAX_BYTES", str(32 * 1024 * 1024)))  # 캐시 총 바이트 상한(기본 32MB)
MAX_RETRIES = int(os.environ.get("LAW_MAX_RETRIES", "3"))           # 429/503/504 재시도 횟수
# 활용신청 안내 페이지 판정 상한(자). 실측 1,455자 — 정상 본문과 섞이지 않게 넉넉히.
UNSUB_MAX_LEN = int(os.environ.get("LAW_UNSUB_MAX_LEN", "8000"))
# 과거본 MST 의 시행일을 찾을 때 연혁 목록을 넘겨 볼 최대 쪽수(100건/쪽).
HISTORY_MAX_PAGES = int(os.environ.get("LAW_HISTORY_MAX_PAGES", "10"))
BACKOFF_BASE = float(os.environ.get("LAW_BACKOFF_BASE", "0.5"))     # 지수 백오프 기준(초)
VERIFY_DISPLAY = max(1, int(os.environ.get("LAW_VERIFY_DISPLAY", "20")))  # verify_citation 검색 폭(정확매칭은 상위 20건 내 결판)

# ----- 배포/교육용 프로필 게이트 (기본 None=전체 노출, 풀버전 동작 불변) -----
#   ALLOWED_TOOLS : 노출/실행 허용 도구 이름 집합. None 이면 제한 없음.
#                   env LAW_ALLOWED_TOOLS(쉼표목록)로도 지정 가능. EXE 빌드는
#                   import 후 코드에서 직접 set 해 env 보다 우선(잠금)한다.
#   SERVICE_NOTICE: 설정 시 모든 tools/call 이 이 안내문만 반환(교육용 만료 등).
ALLOWED_TOOLS = None
SERVICE_NOTICE = None
_env_allow = os.environ.get("LAW_ALLOWED_TOOLS", "").strip()
if _env_allow:
    ALLOWED_TOOLS = {t.strip() for t in _env_allow.split(",") if t.strip()}


# =============================================================================
# 로깅 / 비밀 마스킹 / 동시성
#   - OC 키가 URL·params 어디서 로깅되든 반드시 mask() 통과
#   - 회전 파일 로그(stderr 병행) + traceback 기록으로 무응답 사후추적 가능
# =============================================================================
_OC_RE = re.compile(r"(?i)(OC=)[^&\s]+")


def mask(s):
    """문자열 속 OC 키를 가린다(URL 쿼리·dict repr 양쪽)."""
    s = "" if s is None else str(s)
    s = _OC_RE.sub(r"\1***", s)
    return re.sub(r"(?i)(\"?OC\"?\s*[:=]\s*\"?)[^,\s\"}&]+", r"\1***", s)


def mask_params(p):
    return {k: ("***" if str(k).upper() == "OC" else v) for k, v in (p or {}).items()}


def _make_logger():
    lg = logging.getLogger(SERVER_NAME)
    lg.setLevel(os.environ.get("LAW_LOG_LEVEL", "INFO").upper())
    if lg.handlers:
        return lg
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(fmt)
    lg.addHandler(sh)
    path = os.environ.get("LAW_LOG_FILE")
    if not path:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        d = os.path.join(base, SERVER_NAME + "-mcp")
        try:
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, SERVER_NAME + ".log")
        except Exception:
            path = None
    if path:
        try:
            fh = logging.handlers.RotatingFileHandler(
                path,
                maxBytes=int(os.environ.get("LAW_LOG_MAX_BYTES", "1000000")),
                backupCount=int(os.environ.get("LAW_LOG_BACKUPS", "3")),
                encoding="utf-8")
            fh.setFormatter(fmt)
            lg.addHandler(fh)
        except Exception as e:
            lg.warning("파일 로그 비활성(%s)", e)
    return lg


LOG = _make_logger()


def log(*a):
    """구버전 호환 shim — 내부적으로 LOG.info."""
    LOG.info(" ".join(str(x) for x in a))


_stdout_lock = threading.Lock()   # stdout JSON-RPC 프레이밍 보호(멀티스레드)
_POOL = ThreadPoolExecutor(max_workers=MAX_WORKERS)   # tools/call 워커(읽기 루프 비차단)
_last_good_proto = [None]   # 환경 적응: 마지막 성공 프로토콜을 다음 호출에서 먼저 시도
                            # (HTTPS 가 매번 리셋되는 망에서 HTTP 를 고정해 호출당 1~3s 절약)

# ----- 응답 캐시(TTL+LRU+바이트 상한) : 반복 조회 시 law.go.kr 부하·지연 감소 -----
_CACHE = OrderedDict()          # key -> (만료 monotonic, 텍스트, 바이트수)
_CACHE_LOCK = threading.Lock()
_CACHE_BYTES = [0]              # 캐시 총 문자수 추정(대형 eflaw 전문 누적으로 인한 메모리 폭주 방지)


def _cache_key(endpoint, params):
    # OC 키는 키에서 제외(비밀이 캐시 키에 박히지 않게; 프로세스 내 OC 는 상수)
    items = sorted((k, v) for k, v in params.items() if str(k).upper() != "OC")
    salt = ""
    if endpoint == "lawService.do" and not params.get("efYd"):
        # F7 — 판을 고정하지 않은 전문(현행)은 날마다 새로: 자정에 새 판이 시행될 수 있다
        salt = "@" + time.strftime("%Y%m%d")
    return endpoint + "|" + hashlib.sha256((repr(items) + salt).encode("utf-8")).hexdigest()


def _cache_get(key):
    if CACHE_TTL <= 0:
        return None
    now = time.monotonic()
    with _CACHE_LOCK:
        hit = _CACHE.get(key)
        if hit and hit[0] > now:
            _CACHE.move_to_end(key)
            return hit[1]
        if hit:
            del _CACHE[key]
            _CACHE_BYTES[0] -= hit[2]
    return None


def _cache_put(key, value, ttl=None):
    if CACHE_TTL <= 0:
        return
    if ttl is None:
        ttl = CACHE_TTL
    if ttl <= 0:
        return
    size = len(value)
    with _CACHE_LOCK:
        old = _CACHE.pop(key, None)
        if old is not None:
            _CACHE_BYTES[0] -= old[2]
        _CACHE[key] = (time.monotonic() + ttl, value, size)
        _CACHE_BYTES[0] += size
        while _CACHE and (len(_CACHE) > CACHE_MAX or _CACHE_BYTES[0] > CACHE_MAX_BYTES):
            _k, _v = _CACHE.popitem(last=False)
            _CACHE_BYTES[0] -= _v[2]


# ----- F7 디스크 캐시 — 판 고정 본문(eflaw + MST + efYd)만. 판은 바뀌지 않으므로 기한 없음 -----
#   자리 = %LOCALAPPDATA%\law-axtax-mcp\cache\ (로그와 같은 곳 · LAW_CACHE_DIR 로 바꿈 · LAW_DISK_CACHE=0 이면 끔)
#   열쇠 = OC 를 뺀 매개변수 해시 · 내용은 gzip · 링크 속 'OC=…' 값은 지우고 쓴다(키를 디스크에 남기지 않음)
#   크기 = LAW_DISK_CACHE_MAX_BYTES(기본 300MB) 를 넘으면 오래 안 쓴 것부터 지운다
_OC_IN_BODY = re.compile(r"(?i)(OC=)[^&\s\"'<>\\]+")
_DISK_WRITES = [0]


def _pinned(endpoint, params):
    return (endpoint == "lawService.do" and params.get("target") == "eflaw"
            and bool(params.get("MST")) and bool(params.get("efYd")))


def _disk_dir():
    return os.environ.get("LAW_CACHE_DIR") or os.path.join(
        os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), SERVER_NAME + "-mcp", "cache")


def _disk_path(key):
    h = key.split("|", 1)[-1]
    return os.path.join(_disk_dir(), h[:2], h + ".json.gz")


def _disk_get(key):
    if not DISK_CACHE:
        return None
    path = _disk_path(key)
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            text = f.read()
        os.utime(path, None)                         # 최근에 쓴 것 — 정리 때 뒤로
        return text
    except FileNotFoundError:
        return None
    except Exception as e:
        LOG.debug("디스크 캐시 읽기 실패(무시): %s", e)
        return None


def _disk_put(key, text):
    if not DISK_CACHE:
        return
    path = _disk_path(key)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = "%s.tmp%d" % (path, threading.get_ident())
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            f.write(_OC_IN_BODY.sub(r"\1***", text))
        os.replace(tmp, path)
        _DISK_WRITES[0] += 1
        if _DISK_WRITES[0] % 20 == 1:
            _disk_prune()
    except Exception as e:
        LOG.warning("디스크 캐시 쓰기 실패(무시): %s", e)


def _disk_prune():
    files = []
    for root, _, names in os.walk(_disk_dir()):
        for n in names:
            if n.endswith(".json.gz"):
                fp = os.path.join(root, n)
                try:
                    st = os.stat(fp)
                    files.append((st.st_mtime, st.st_size, fp))
                except OSError:
                    pass
    total = sum(s for _, s, _ in files)
    for _, size, fp in sorted(files):
        if total <= DISK_CACHE_MAX_BYTES:
            break
        try:
            os.remove(fp)
            total -= size
        except OSError:
            pass


def _retry_after(headers, default):
    """Retry-After 헤더(초 또는 HTTP-date)를 초로 환산, 최대 30초로 캡."""
    ra = headers.get("Retry-After") if headers else None
    if not ra:
        return default
    ra = ra.strip()
    if ra.isdigit():
        return min(int(ra), 30.0)
    try:
        dt = email.utils.parsedate(ra)
        if dt:
            return max(0.0, min(calendar.timegm(dt) - time.time(), 30.0))
    except Exception:
        pass
    return default


# 전문 미제공 스텁 감지: 법제처 lawService 는 전문이 없는 판례(국세법령정보시스템 출처·
# 심리불속행·최근 하급심 등)에 대해 {"Law":"일치하는 판례가 없습니다..."} 같은 짧은
# 안내문을 200 으로 반환한다. 이를 빈 응답으로 인식해야 무의미한 재시도를 막을 수 있다.
_NO_CONTENT_MARKERS = ("없습니다", "확인하여 주", "조회되지", "검색되지")


def _looks_unsubscribed(text):
    """OC 키에 해당 API 활용신청이 안 된 경우의 안내 페이지인가.

    ★단순 부분문자열 검사를 하면 안 된다. 법령 본문에 '미신청' 이라는 낱말이
    실제로 들어간다 — 법인세법 시행규칙(MST 287787)은 별지 서식의 표 칸에
    '│신청│미신청│' 가 있어서, 조문 137개가 든 3.4MB 정상 JSON 이 통째로
    '미신청 안내' 로 오판됐다(2026-09-08). 재정경제부령 시행규칙 전반이 조회
    불가가 됐고 verify_citation 은 실재 조문을 '조문 없음' 으로 보고했다.

    실제 안내 페이지는 1.5KB 남짓의 HTML 이다. 그래서 ①정상 데이터(JSON/XML)가
    아니고 ②충분히 짧고 ③고유 문구를 가질 때만 참으로 본다."""
    t = (text or "").strip()
    if not t or len(t) > UNSUB_MAX_LEN:      # 정상 본문은 수십 KB ~ 수 MB
        return False
    if t[0] in "{[":                          # JSON 본문
        return False
    low = t[:200].lstrip().lower()
    if low.startswith("<?xml") or low.startswith("<law") or low.startswith("<prec"):
        return False                          # XML 본문
    return "미신청된" in t or ("OPEN API 신청" in t and "국가법령정보" in t)


def _looks_empty_detail(text):
    t = (text or "").strip()
    if not t:
        return True
    if len(t) < 120 and any(m in t for m in _NO_CONTENT_MARKERS):
        return True
    try:
        d = json.loads(t)
        if isinstance(d, dict) and len(d) == 1:
            v = next(iter(d.values()))
            if isinstance(v, str) and any(m in v for m in _NO_CONTENT_MARKERS):
                return True
    except Exception:
        pass
    return False


# =============================================================================
# HTTP / 공통
# =============================================================================
def get_oc(override=None):
    # override = 도구 인자 law_oc(법제처 키 · 환경변수 LAW_OC 와 같은 뜻). 법령커넥터 게이트웨이(_common gateway.py)가
    # 사용자별 키를 이 이름으로 넣는다 — 게이트웨이와 맞춘 호출 규약이라 함께 바꾼다(2026-10-13 옛 이름에서 바꿈, 대표님 결정).
    # 도구 설명(스키마)에는 싣지 않는다 — 모델이 키를 다룰 일이 없게.
    oc = override or os.environ.get("LAW_OC")
    if not oc:
        raise RuntimeError(
            "법제처 OC 인증키가 없습니다. 환경변수 LAW_OC 를 설정하세요. "
            "(발급: https://open.law.go.kr/LSO/openApi/guideList.do)")
    return oc


HEADERS = {
    "User-Agent": UA,
    # Referer — 6월 첫 개발 기록(개발_인수인계 §7 함정 표): 개인 키로 이 머리 없이 부르면 키가 맞아도
    #   「사용자 정보 검증에 실패」(IP · 도메인 등록 안내)가 왔다. 2026-10-13 공식 시험 키 test 로 다시 재 보니
    #   Referer · User-Agent 를 빼도 200 과 검색결과가 왔다(시험 키에는 이 검사가 없음). 개인 키를 위해 늘 보낸다.
    "Referer": os.environ.get("LAW_REFERER", "https://www.law.go.kr/"),
    "Accept": "application/json, application/xml, text/xml, text/html, */*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "close",
}


def http_get(endpoint, params):
    """endpoint: 'lawSearch.do' | 'lawService.do' . params: dict. -> 응답 텍스트.
    HTTPS 우선, 연결이 리셋/실패하면 자동으로 HTTP 로 폴백(법제처 서버의 TLS/봇 차단 대비).
    LAW_API_PROTOCOL=http|https 로 강제 지정 가능."""
    forced = (os.environ.get("LAW_API_PROTOCOL", "").strip().lower())
    if forced in ("http", "https"):
        protos = [forced]
    else:
        protos = ["https", "http"]
        if _last_good_proto[0] in protos:   # 직전 성공 프로토콜을 먼저
            protos.sort(key=lambda x: 0 if x == _last_good_proto[0] else 1)
    qs = urllib.parse.urlencode(params, encoding="utf-8")
    key = _cache_key(endpoint, params)
    cached = _cache_get(key)
    if cached is not None:
        LOG.debug("cache hit %s", endpoint)
        return cached
    if _pinned(endpoint, params):                 # F7 — 판 고정 본문은 디스크에서(판은 바뀌지 않음)
        disk = _disk_get(key)
        if disk is not None:
            _cache_put(key, disk, ttl=CACHE_TTL_DETAIL)
            LOG.debug("disk cache hit %s", endpoint)
            return disk
    last = "원인 불명"
    start = time.monotonic()
    LOG.debug("GET %s params=%s", endpoint, mask_params(params))
    for proto in protos:
        url = "%s://www.law.go.kr/DRF/%s?%s" % (proto, endpoint, qs)
        for attempt in range(MAX_RETRIES):
            remaining = DEADLINE - (time.monotonic() - start)
            if remaining <= 0:
                raise RuntimeError(
                    "법제처 API 시간초과(%ds): %s — 응답이 지연됩니다. 잠시 후 다시 시도하세요."
                    % (DEADLINE, last))
            per_attempt = max(1.0, min(TIMEOUT, remaining))
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                ctx = ssl.create_default_context() if proto == "https" else None
                with urllib.request.urlopen(req, timeout=per_attempt, context=ctx) as resp:
                    # resp.read() 의 timeout 은 '소켓 recv 1회' 한도일 뿐 전체 읽기 시간 상한이
                    # 아니다. 큰 전체본(eflaw 수백 KB)을 서버가 recv 한도 안쪽 청크로 느리게
                    # 흘려보내면 DEADLINE(시도 사이에서만 검사)을 넘겨 수 분간 매달리고,
                    # 클라이언트 4분 한도에 먼저 걸려 '서버 무응답'으로 보인다. 청크로 읽으며
                    # 전체 벽시계 데드라인을 강제해, 먹통 대신 깔끔한 시간초과로 끝낸다.
                    parts = []
                    while True:
                        if time.monotonic() - start > DEADLINE:
                            raise TimeoutError("본문 수신이 데드라인(%ds)을 초과" % DEADLINE)
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        parts.append(chunk)
                    text = b"".join(parts).decode("utf-8", errors="replace")
            except urllib.error.HTTPError as e:
                last = "HTTP %s" % e.code
                # 429/503/504(과부하·게이트웨이)는 Retry-After/지수백오프로 재시도
                if e.code in (429, 503, 504) and attempt < MAX_RETRIES - 1:
                    budget = DEADLINE - (time.monotonic() - start) - 0.5
                    if budget > 0.5:
                        wait = _retry_after(getattr(e, "headers", None),
                                            BACKOFF_BASE * (2 ** attempt) + random.uniform(0, 0.3))
                        wait = max(0.0, min(wait, budget))   # 음수 sleep 방어
                        LOG.warning("law.go.kr %s %s — %.1fs 후 재시도(%d/%d)",
                                    proto, last, wait, attempt + 1, MAX_RETRIES)
                        time.sleep(wait)
                        continue
                LOG.warning("law.go.kr %s: %s", proto, last)
                break  # 비재시도 코드 -> 다음 프로토콜 시도
            except Exception as e:   # URLError/SSLError/ConnectionResetError(WinError 10054)/OSError 등
                last = getattr(e, "reason", None) or e
                LOG.warning("law.go.kr 연결실패(%s, 시도 %d): %s", proto, attempt + 1, mask(str(last)))
                if DEADLINE - (time.monotonic() - start) > 0.5:
                    time.sleep(max(0.0, min(BACKOFF_BASE * (2 ** attempt), 2.0)))   # 음수 sleep 방어
                continue             # 같은 프로토콜 재시도 후 다음 프로토콜
            head = text.lstrip()[:300].lower()
            if head.startswith("<!doctype html") or head.startswith("<html"):
                # '미신청' = 해당 API 활용신청 누락(키 자체는 유효). 예외로 막지 말고 본문을
                # 그대로 돌려 상위(_detail)가 '신청 안내'를 하게 한다. 캐시는 하지 않음.
                if "미신청" in text or "OPEN API 신청" in text:
                    _last_good_proto[0] = proto
                    return text
                if any(w in text for w in ("검증", "인증", "사용자")):
                    raise RuntimeError("인증 실패로 보입니다. OC 키가 올바른지/승인되었는지 확인하세요. "
                                       "(open.law.go.kr 로그인 후 활용신청 승인 확인)")
                last = "HTML 오류 페이지"
                break                # 다음 프로토콜 시도
            _last_good_proto[0] = proto         # 다음 호출은 이 프로토콜부터
            # 스텁·미신청 안내는 캐시하지 않는다. 미신청 페이지를 캐시하면
            # 폴백으로 복구한 뒤에도 TTL 동안 같은 오답이 되돌아온다.
            if not _looks_empty_detail(text) and not _looks_unsubscribed(text):
                # 전문(lawService)은 MST 고정 시 사실상 불변 → 긴 TTL, 검색은 기본 TTL
                _cache_put(key, text,
                           ttl=(CACHE_TTL_DETAIL if endpoint == "lawService.do" else None))
                if _pinned(endpoint, params):
                    _disk_put(key, text)
            return text
    raise RuntimeError("법제처 API 연결 실패: %s — HTTPS·HTTP 모두 시도했습니다. "
                       "네트워크/방화벽(또는 보안 프로그램)이 law.go.kr 을 막는지, OC 승인 여부를 확인하세요." % last)


# ----- 파싱 결과 캐시(소형 LRU) : eflaw 전체본(수백 KB JSON) 재파싱 방지 -----
#   get_law_article/get_law_appendix/get_law_structure/verify(law_article) 가 같은 MST
#   전체본을 공유하는데, 텍스트 캐시만으로는 호출마다 json.loads(수 MB 객체 트리)가 반복된다.
#   전체본은 크므로 슬롯 8개면 충분. 파싱 결과 dict 는 '읽기 전용'으로만 사용할 것(스레드 공유).
_PARSED = OrderedDict()
_PARSED_LOCK = threading.Lock()
PARSED_MAX = max(1, int(os.environ.get("LAW_PARSED_MAX", "8")))


def http_get_json(endpoint, params, text=None):
    """http_get 응답을 json.loads 한 결과를 TTL+LRU 로 캐시해 반환.
    text 가 주어지면(이미 받아둔 응답) 네트워크 호출 없이 그 텍스트를 파싱한다.
    파싱 실패는 예외 전파(호출부 폴백 유도)."""
    key = _cache_key(endpoint, params)
    now = time.monotonic()
    with _PARSED_LOCK:
        hit = _PARSED.get(key)
        if hit and hit[0] > now:
            _PARSED.move_to_end(key)
            return hit[1]
        if hit:
            del _PARSED[key]
    if text is None:
        text = http_get(endpoint, params)
    data = json.loads(text)
    if CACHE_TTL > 0 and not _looks_empty_detail(text) and not _looks_unsubscribed(text):
        with _PARSED_LOCK:
            _PARSED[key] = (time.monotonic() + CACHE_TTL_DETAIL, data)
            _PARSED.move_to_end(key)
            while len(_PARSED) > PARSED_MAX:
                _PARSED.popitem(last=False)
    return data


# 법제처 응답 글 → 평문 (2026-10-13 새로 짬 — 클린룸 점검 C1). 글을 앞에서부터 훑으며 '<' 를 만날 때마다 다음 '>'
#  까지를 한 덩이로 보고 갈래를 정한다(_markup_kind): 줄바꿈 태그(br — 대소문자 · 닫는 빗금 · 꺾쇠 안 빈칸 모두)와
#  문단 · 구역 · 표 행 · 목록 항목 · 제목 · 표가 끝나는 자리는 줄바꿈, 그 밖의 HTML 태그(꺾쇠 바로 뒤가 영문자 · 빗금 ·
#  느낌표)는 지움, 한글 · 숫자 · 빈칸으로 시작하는 꺾쇠('<과세표준>' · '<세 율>' · '<신설 2024.2.29>')는 법령 본문이라
#  '<' 하나만 내보내고 그 다음 글자부터 다시 훑는다 — 그래서 '<개정 2024.3.15.)<br>' 처럼 깨진 글 속 태그도 잡힌다.
#  줄을 바꿀 끝 태그의 실측(2026-10-13 · 이 함수가 실제로 받은 입력 32,019건 — 시험 키로 도구 30여 가지를 돌린 것과
#  이 PC 디스크 캐시의 판 고정 본문): br 1,079 · 끝 태그 p 712 · img 203 · span 23 · td 22 · tr 10 · tbl 5 · tbody 4 ·
#  table 4 · a 4 · sup 2. 그래서 p · tr · table 을 줄바꿈으로 본다. 표본에는 없지만 HTML 에서 줄이 바뀌는 구역(div) ·
#  목록 항목(li) · 제목(h1~h6)도 함께 둔다.
_BREAK_AFTER = frozenset(("p", "tr", "table", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"))


def _markup_kind(inner):
    """'<' 와 '>' 사이 글 → 'break'(줄바꿈) · 'tag'(지움) · 'text'(본문의 꺾쇠)."""
    word = inner.strip().lower()
    if word.endswith("/"):
        word = word[:-1].rstrip()
    if word == "br":
        return "break"
    lead = inner[:1]
    if not lead or not (lead in "/!" or "a" <= lead.lower() <= "z"):
        return "text"
    if word.startswith("/") and word[1:].strip() in _BREAK_AFTER:
        return "break"
    return "tag"


def _strip_markup(text):
    out, pos, close = [], 0, -1
    while True:
        lt = text.find("<", pos)
        if lt < 0:
            out.append(text[pos:])
            return "".join(out)
        out.append(text[pos:lt])
        if close <= lt:                            # 다음 '>' 는 앞으로만 움직이므로 다시 찾을 때만 찾는다
            close = text.find(">", lt + 1)
        if close < 0:
            out.append(text[lt:])
            return "".join(out)
        kind = _markup_kind(text[lt + 1:close])
        if kind == "text":
            out.append("<")
            pos = lt + 1
        else:
            out.append("\n" if kind == "break" else "")
            pos = close + 1


def _squeeze(run):
    """빈칸 · 탭이 둘 이상 이어지면 빈칸 하나로(하나뿐이면 그대로)."""
    return run.group(0) if len(run.group(0)) == 1 else " "


def clean_text(s):
    """법제처 응답 글(조문 · 판례 · 해석 본문 등) → 평문. 리스트 · 딕트가 와도(깊은 중첩 조문) 글로 바꿔 처리한다.
    줄마다 앞뒤 빈칸 · 탭을 걷고, 빈 줄은 하나까지만 남긴다."""
    if not s:
        return ""
    text = s if isinstance(s, str) else str(s)
    text = html.unescape(_strip_markup(text)).replace("\xa0", " ").replace("\r", "")
    kept, prev_blank = [], True
    for raw in text.split("\n"):
        line = re.sub(r"[ \t]+", _squeeze, raw).strip(" \t")
        if line or not prev_blank:
            kept.append(line)
        prev_blank = not line
    return "\n".join(kept).strip()


def cap(s, n):
    return s if len(s) <= n else s[:n] + " …(이하 생략)"


# =============================================================================
# 목록(검색) 파싱 — 도메인 무관 제네릭
# =============================================================================
def parse_search(text):
    """검색 XML -> (total, page, [item dict,...]).
    메타데이터는 leaf 노드, 개별 항목은 하위 노드를 가진 컨테이너라는 점을 이용."""
    root = ET.fromstring(text)
    total = root.findtext("totalCnt") or root.findtext(".//totalCnt") or "?"
    page = root.findtext("page") or root.findtext(".//page") or "1"
    items = []
    for child in list(root):
        if not list(child):           # leaf = 메타데이터(target/totalCnt/page 등)
            continue
        d = {}
        for k in list(child):
            t = (k.text or "").strip()
            if t:
                d[k.tag] = t
        if d:
            items.append(d)
    return total, page, items


def pick(d, *names):
    for n in names:
        if d.get(n):
            return d[n]
    for n in names:                    # 부분 일치
        for k, v in d.items():
            if n in k and v:
                return v
    return ""


def id_of(d):
    for k, v in d.items():
        if v and (k.endswith("일련번호") or k == "ID"):
            return v
    return pick(d, "법령일련번호", "법령ID", "ID")


NAME_KEYS = ("사건명", "안건명", "법령명한글", "법령명", "재결례명", "행정규칙명",
             "자치법규명", "법령명영문", "별표명", "제목", "title")

# 검색 목록에 노출할 '핵심' 메타데이터만 화이트리스트(전문은 get_* 로 위임).
# 전체 필드 덤프가 대화창 메모리 폭주(강제종료)의 주원인이었으므로 식별·선별용 필드로 한정.
ESSENTIAL_KEYS = (
    "법령명한글", "법령명", "법령명영문", "약칭", "자치법규명", "행정규칙명",
    "법원명", "재결청", "처분청", "질의기관명", "회신기관명", "지자체기관명", "소관부처명",
    "사건번호", "안건번호", "청구번호", "발령번호", "공포번호",
    "선고일자", "의결일자", "회신일자", "처분일자", "해석일자", "공포일자", "시행일자",
    "판 상태",  # list_law_history 가 현행연혁코드를 풀어 넣는 칸(v2.13.1)
    "발령일자", "종국일자",
    "사건종류명", "재결례유형명", "행정규칙종류", "자치법규종류", "세목", "법령구분명", "제개정구분명",
    "데이터출처명", "별표번호", "별표종류", "관련법령명", "별표서식파일링크", "별표서식PDF파일링크",
    "해석기관명", "질의기관명", "법령해석상세링크",
    "법령ID",   # 조회 실패 시 lawId 우회를 쓸 수 있게 노출(2026-09-08 현장 요청)
)


def clamp_display(v, default=None):
    """display 값을 [1, MAX_DISPLAY] 로 강제(문서화된 상한 실제 적용)."""
    if default is None:
        default = DEFAULT_DISPLAY
    try:
        v = int(v)
    except Exception:
        v = default
    return str(max(1, min(MAX_DISPLAY, v)))


def render_item(d):
    idv = id_of(d)
    name = pick(d, *NAME_KEYS)
    out = [("[%s] %s" % (idv, name)).rstrip()]
    for k in ESSENTIAL_KEYS:
        v = d.get(k)
        if v and v != idv and v != name:
            v = mask(clean_text(v))                      # 링크 필드의 OC 키 노출 방지
            v = v if k.endswith("링크") else cap(v, 100)  # 링크는 잘리면 무용하므로 전체 표시
            out.append("   %s: %s" % (k, v))
    return "\n".join(out)


def fmt_search(title, total, page, items, detail_tool):
    if not items:
        return ("[검색결과 없음] %s (총 %s건)\n\n"
                "다시 찾을 때는 검색어를 줄이세요 — 법제처 검색은 빈칸으로 띄운 낱말이 모두 들어 있는 것만 돌려줍니다.\n"
                "그래도 없으면 판례 · 심판례 · 해석의 번호나 내용을 추측해서 채우지 말고, 못 찾았다고 그대로 전하세요."
                % (title, total))
    header = "%s — 총 %s건 · 이 쪽 %d건(%s쪽)\n" % (title, total, len(items), page)   # F7 총건수 · 이 쪽 건수
    lines = [header]
    used = len(header)
    shown = 0
    truncated = False
    for d in items:
        block = render_item(d)
        if shown > 0 and used + len(block) > MAX_SEARCH_TEXT:
            truncated = True
            break
        lines.append(block)
        lines.append("")
        used += len(block) + 1
        shown += 1
    if detail_tool and id_of(items[0]):
        # get_law_article 은 id 파라미터가 없고 mst 만 받는다 — 힌트가 실제 스키마와
        # 다르면 모델이 그대로 따라 하다 실패한다(실사용 리포트).
        param = "mst" if detail_tool == "get_law_article" else "id"
        lines.append('➡ 전문 조회:  %s(%s="%s")' % (detail_tool, param, id_of(items[0])))
    if truncated:
        lines.append("\n⚠️ 출력 한도(%d자) 도달: 총 %s건 중 %d건만 표시. "
                     "query를 좁히거나 page로 이동하고, 상세는 %s 로 조회하세요."
                     % (MAX_SEARCH_TEXT, total, shown, detail_tool or "get_*"))
    return "\n".join(lines)


# 상세 출력에서 먼저 낼 칸 차례 (2026-10-13 새로 정함 — 클린룸 점검 C6). 법제처 공식 가이드(본문 조회)의
# 「출력 결과 필드」 표 차례를 따랐다(2026-10-13 가이드 확인):
#  · 조세심판(specialDeccTtInfoGuide) 차례를 바탕으로, 판례(prec) → 법령해석례(expc) → 헌재(detc) → 행정심판(decc)
#    → 행정규칙(admrul) → 관세청 해석(cgmExpcKcs) 가이드 차례로 훑어 새로 나온 칸을 그 가이드의 바로 앞 칸 뒤에 끼웠다
#    (앞 칸이 없으면 뒤 칸 앞, 둘 다 없으면 끝). 가이드끼리 차례가 어긋나면 앞서 훑은 가이드를 따른다.
#  · 긴 본문(전문 · 판례내용 · 이유 · 조문내용 · 별표 · 회신내용)은 맨 뒤로 옮겼다 — 글자 예산(MAX_TEXT)에 걸려
#    요지 · 주문 · 관련법령이 잘리지 않게. 회신일자 · 회신기관명 · 회신내용은 해석 목록 칸이라 가이드 본문 표에 없다.
PRIORITY_FIELDS = [
    "사건명", "종국일자", "사건번호", "선고일자", "법원명", "사건종류명", "판결유형",
    "판시사항", "결정요지", "판결요지", "참조조문", "참조판례", "심판대상조문",
    "청구번호", "처분일자", "의결일자", "처분청", "재결청", "재결례유형명", "세목",
    "재결요지", "따른결정", "참조결정", "주문", "청구취지",
    "안건명", "안건번호", "해석일자", "질의기관명", "질의요지", "회답", "관련법령",
    "행정규칙명", "행정규칙종류", "발령일자", "발령번호", "소관부처명", "회신일자", "회신기관명",
    "전문", "판례내용", "이유", "조문내용", "별표", "회신내용",
]


def flatten(obj, acc, key=None):
    """dict/list -> [(label, text)]. 문자열·숫자 leaf 를 수집(bool 제외).
    법제처 JSON 상세의 일련번호·조문수 등 숫자형 필드 누락 방지.

    ★리스트 원소가 맨 문자열인 경우도 부모 키를 달아 수집한다. 예전에는 이 가지에서
    그냥 버려서 행정규칙의 조문내용(문자열 249개 리스트)·부칙내용·제개정이유가
    통째로 사라졌다(2026-08-29 확인)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if v.strip():
                    acc.append((k, v.strip()))
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                acc.append((k, str(v)))
            else:
                flatten(v, acc, k)
    elif isinstance(obj, list):
        for it in obj:
            if isinstance(it, str):
                if it.strip() and key:
                    acc.append((key, it.strip()))
            elif isinstance(it, (int, float)) and not isinstance(it, bool):
                if key:
                    acc.append((key, str(it)))
            else:
                flatten(it, acc, key)


def fmt_detail(title, text, data=None):
    """상세 응답 포맷. data= 로 선파싱된 JSON 을 받으면 재파싱을 생략한다
    (eflaw 전체본 폴백 경로에서 같은 수백 KB 텍스트를 2회 json.loads 하지 않게)."""
    pairs = []
    text = text.strip()
    parsed = False
    # 1) JSON 시도
    try:
        if data is None:
            data = json.loads(text)
        inner = data
        if isinstance(data, dict) and len(data) == 1:
            inner = next(iter(data.values()))
        flatten(inner, pairs)
        parsed = bool(pairs)
    except Exception:
        pass
    # 2) XML 시도
    if not parsed:
        try:
            root = ET.fromstring(text)

            def walk(el):
                kids = list(el)
                if not kids:
                    t = (el.text or "").strip()
                    if t:
                        pairs.append((el.tag, t))
                else:
                    for k in kids:
                        walk(k)
            walk(root)
            parsed = bool(pairs)
        except Exception:
            pass
    # 3) raw 폴백 — 비정형 응답(HTML 조각 등)에 echo 된 OC 키도 mask
    if not parsed:
        return "=== %s ===\n\n%s" % (title, cap(mask(clean_text(text)), MAX_TEXT))

    # 우선순위 필드 먼저, 나머지 뒤에
    seen = set()
    out = ["=== %s ===\n" % title]
    budget = [MAX_TEXT]

    def emit(label, value):
        v = mask(clean_text(value))   # 상세링크 등에 echo 되는 OC 키 노출 방지
        if not v or budget[0] <= 0:
            return
        v = cap(v, max(200, budget[0]))
        block = "%s:\n%s\n" % (label, v) if len(v) > 60 else "%s: %s" % (label, v)
        out.append(block)
        budget[0] -= len(v)

    # 같은 키가 여러 번 오면 이어붙인다. 첫 값만 남기면 조문내용 249개 중
    # 1개만 나오는 식으로 본문이 사라진다.
    pmap = {}
    for k, v in pairs:
        pmap.setdefault(k, []).append(v)
    pmap = {k: (chr(10).join(vs) if len(vs) > 1 else vs[0])
            for k, vs in pmap.items()}
    for key in PRIORITY_FIELDS:
        if key in pmap and key not in seen:
            emit(key, pmap[key])
            seen.add(key)
    for k, _v in pairs:
        if k in seen:
            continue
        seen.add(k)
        emit(k, pmap[k])
    return "\n".join(out).strip()


def _detail(title, label, idv, text):
    """전문 응답을 포맷하되, 법제처가 전문을 제공하지 않는 항목이면 명확히 안내한다.
    (재시도해도 동일하므로 모델이 같은 ID 를 반복 호출하지 않게 하는 것이 핵심.)"""
    if _looks_unsubscribed(text):
        return ("[API 미신청] %s 본문(일련번호 %s)\n"
                "이 본문 API 가 현재 OC 키에 활용신청되어 있지 않습니다(키 자체는 정상).\n"
                "→ open.law.go.kr 로그인 → [OPEN API] → [OPEN API 신청] 에서 해당 API(법령종류)를 "
                "추가 신청하면 전문(질의요지·회답·이유 등) 조회가 활성화됩니다.\n"
                "→ 신청 전에는 검색결과의 안건명·해석일자·상세링크(국세법령정보시스템)로 확인하세요.\n"
                "⚠️ 재조회해도 동일 — 신청 전까지 같은 ID 반복 호출 불필요." % (label, idv))
    if _looks_empty_detail(text):
        return ("[전문 미제공] %s 일련번호 %s\n"
                "법제처 API 가 이 %s의 전문을 제공하지 않습니다"
                "(국세법령정보시스템 출처·심리불속행·최근 하급심 등에서 흔함).\n"
                "⚠️ 재조회해도 결과는 동일합니다 — 같은 ID 반복 호출은 불필요합니다.\n"
                "→ 검색결과의 사건명(심리불속행 판례는 사건명에 결론이 담김)·요지를 활용하거나, "
                "사건번호·선고일자로 직접 확인하세요." % (label, idv, label))
    return fmt_detail(title, text)


# =============================================================================
# 도구 구현
# =============================================================================
def tool_search_precedents(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "prec", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1)),
         "search": str(a.get("search", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("sort"):
        p["sort"] = a["sort"]
    fd, td = a.get("from_date"), a.get("to_date")
    if fd or td:
        p["prncYd"] = "%s~%s" % (fd or "", td or "")
    total, page, items = parse_search(http_get("lawSearch.do", p))
    _remember_prec(items)
    text = fmt_search("판례 검색결과", total, page, items, "get_precedent")
    nts = [pick(d, "사건번호") for d in items if "국세법령정보" in pick(d, "데이터출처명")]
    if nts:      # v2.13 — 이 출처 항목은 법제처 lawService 로 본문이 오지 않는다(실측 623875 · 279186)
        text += ("\n\n※ 데이터출처명 '국세법령정보시스템' 항목(%s)은 get_precedent 로 본문이 오지 않습니다 → "
                 "search_nts_precedents(query=\"사건번호\") 로 국세법령정보시스템 문서ID 를 찾아 "
                 "get_tax_interpretation(id=…) 으로 보세요(get_precedent 도 같은 사건을 찾아 알려 줍니다)."
                 % ", ".join(n for n in nts[:3] if n))
    return text


# 판례일련번호 → (사건번호, 데이터출처명). search_precedents 결과를 기억해 두었다가, get_precedent 가 본문을 못 받을 때
# 같은 사건을 국세법령정보시스템에서 찾는 데 쓴다(v2.13 — 세무자문 좌석 10-25 요청서 1-4).
_PREC_NO = OrderedDict()
_PREC_NO_LOCK = threading.Lock()


def _remember_prec(items):
    with _PREC_NO_LOCK:
        for d in items or []:
            sid, no = _num_id(id_of(d)), pick(d, "사건번호")
            if sid and no:
                _PREC_NO[sid] = (no, pick(d, "데이터출처명"))
                _PREC_NO.move_to_end(sid)
        while len(_PREC_NO) > 500:
            _PREC_NO.popitem(last=False)


def _caseno_compact(no):
    """'대법원-2022-두-42020' · '대법원 2022두42020' → '2022두42020'(법원 이름 · 빈칸 · 줄표를 뺀 꼴)."""
    c = re.sub(r"[^0-9가-힣]", "", str(no or ""))
    return re.sub(r"^[가-힣]*?(?=\d)", "", c)


def _prec_nts_hint(a):
    """법제처에 본문이 없는 판례 — 국세법령정보시스템에서 같은 사건의 문서ID 를 찾아 다음 길을 알린다."""
    sid = _num_id(a.get("id"))
    with _PREC_NO_LOCK:
        known = _PREC_NO.get(sid)
    no = str(a.get("case_no") or "").strip() or (known[0] if known else "")
    if not no:
        return ("\n→ 국세법령정보시스템 출처 항목이면 search_nts_precedents(query=\"사건번호\") 로 같은 사건의 문서ID 를 찾아 "
                "get_tax_interpretation(id=…) 으로 본문을 보세요. get_precedent 에 case_no(사건번호)를 주면 바로 찾아 드립니다.")
    want = _caseno_compact(no)
    if not TAXLAW_ENABLED or not want:
        return "\n→ 같은 사건을 국세법령정보시스템에서: search_nts_precedents(query=\"%s\")" % (want or no)
    try:
        _t, rows, _p, _d = _nts_search(want, "precedent", {"display": 5})
    except Exception as e:
        return ("\n→ 국세법령정보시스템에서 같은 사건을 찾지 못했습니다(%s) — search_nts_precedents(query=\"%s\") 로 다시"
                % (mask(str(e))[:80], want))
    hits = [x for x in rows if _caseno_compact(_nts_clean(x.get("NTST_DCM_DSCM_CNTN"))) == want]
    if not hits:
        return ("\n→ 국세법령정보시스템에도 사건번호 %s 가 바로 나오지 않습니다 — search_nts_precedents(query=\"%s\") 로 "
                "직접 찾아보세요." % (no, want))
    x = hits[0]
    did = _num_id(x.get("DOC_ID"))
    res = _nts_outcome(x.get("NTST_DCM_DCS_CL_CD"), x.get("NTST_DCM_DCS_CL_NM"))
    return ("\n→ 국세법령정보시스템에 같은 사건 본문이 있습니다: [%s] %s%s\n"
            "   get_tax_interpretation(id=\"%s\")  — taxlaw-fulltext 가 있으면 get_nts_fulltext(ntstDcmId=\"%s\") 도 같습니다."
            % (did, _nts_clean(x.get("NTST_DCM_DSCM_CNTN")), (" · 결과 " + res) if res else "", did, did))


def tool_get_precedent(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "prec", "type": "JSON", "ID": str(a["id"])}
    if a.get("case_name"):
        p["LM"] = a["case_name"]          # 공식 변수 LM = 판례명
    out = _detail("판례 전문", "판례", a.get("id", ""), http_get("lawService.do", p))
    if out.startswith("[전문 미제공]"):
        out += _prec_nts_hint(a)
    return out


def tool_search_tax_tribunal(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "ttSpecialDecc", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("sort"):
        p["sort"] = a["sort"]
    if a.get("rslYd"):
        p["rslYd"] = a["rslYd"]   # 의결일자 범위 YYYYMMDD~YYYYMMDD
    if a.get("dpaYd"):
        p["dpaYd"] = a["dpaYd"]   # 처분일자 범위
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("조세심판원 재결례 검색결과", total, page, items, "get_tax_tribunal")


def tool_get_tax_tribunal(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "ttSpecialDecc", "type": "JSON", "ID": str(a["id"])}
    if a.get("decision_name"):
        p["LM"] = a["decision_name"]      # 공식 변수 LM = 특별행정심판재결례명
    return _detail("조세심판원 재결례 전문", "재결례", a.get("id", ""), http_get("lawService.do", p))


def tool_search_interpretations(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "expc", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("sort"):
        p["sort"] = a["sort"]
    if a.get("search"):
        p["search"] = str(a["search"])
    for k in ("inq", "rpl"):           # 질의기관/회신기관 코드 필터(선택)
        if a.get(k):
            p[k] = str(a[k])
    if a.get("explYd"):                # 해석일자 범위 YYYYMMDD~YYYYMMDD
        p["explYd"] = a["explYd"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("법령해석례 검색결과", total, page, items, "get_interpretation")


def tool_get_interpretation(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "expc", "type": "JSON", "ID": str(a["id"])}
    return _detail("법령해석례 전문", "해석례", a.get("id", ""), http_get("lawService.do", p))


def _exact_law_rows(name, oc, total):
    """현행 법령 목록에서 이름이 정확히 같은 행 → [(목록 차례, 행)…]. 100건씩 최대 3쪽(300건)까지 본다."""
    k = _name_key(name)
    try:
        n = int(total)
    except (TypeError, ValueError):
        n = 100
    hits = []
    for pg in range(1, min(3, max(1, (n + 99) // 100)) + 1):
        _, _, rows = parse_search(http_get("lawSearch.do", {
            "OC": oc, "target": "law", "type": "XML", "query": name, "display": "100", "page": str(pg)}))
        hits += [((pg - 1) * 100 + i + 1, d) for i, d in enumerate(rows)
                 if _name_key(pick(d, "법령명한글", "법령명")) == k]
        if hits or len(rows) < 100:
            break
    return hits


def _exact_first(items, name, oc, total, page, display):
    """이름이 정확히 같은 법령을 맨 앞으로 → (items, 안내 줄 | "").

    법제처 법령 검색은 그 낱말이 이름에 든 법령을 모두 돌려주는데, 이름이 정확히 같은 법령이 앞에 온다는
    보장이 없다 — '상법' 은 56건 가운데 34번째(보상법 · 배상법 뒤)라 첫 쪽에 없고, '민법' 은 난민법 뒤
    4번째라 맨 아래 '전문 조회' 안내가 난민법을 가리켰다(2026-10-29 실측 · 강의 실습판 04_search_law.py 가
    먼저 막던 것). 이 쪽에 있으면 앞으로 옮기고, 첫 쪽에 없으면 목록 전체에서 찾아 맨 앞에 붙인다."""
    k = _name_key(name)
    idx = [i for i, d in enumerate(items) if _name_key(pick(d, "법령명한글", "법령명")) == k]
    if idx:
        if idx == list(range(len(idx))):                # 이미 맨 앞
            return items, ""
        pos = (page - 1) * display + idx[0] + 1
        items = [items[i] for i in idx] + [d for i, d in enumerate(items) if i not in idx]
    elif page == 1 and _int_arg(total, 10 ** 6) > len(items):     # 첫 쪽이 목록 전부면 더 찾을 것이 없다
        try:
            hits = _exact_law_rows(name, oc, total)
        except Exception as e:                          # 덧 호출이 실패해도 검색 결과는 그대로 낸다
            LOG.warning("정확한 이름 찾기 실패(무시): %s", e)
            hits = []
        if not hits:
            return items, ""
        pos = hits[0][0]
        items = [d for _, d in hits] + items
    else:
        return items, ""
    return items, "※ 맨 앞 = 이름이 정확히 같은 법령 「%s」 (법제처 목록 차례로는 %d번째)" % (
        pick(items[0], "법령명한글", "법령명"), pos)


def tool_search_law(a):
    oc = get_oc(a.get("law_oc"))
    p = {"OC": oc, "target": "law", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    note = ""
    if a.get("query"):
        q, note = resolve_law_name(a["query"])          # F2 — 약칭이면 정식 이름으로
        p["query"] = q or a["query"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    if a.get("query") and items:                        # v2.13.1 — 이름이 정확히 같은 법령을 맨 앞에
        items, moved = _exact_first(items, p["query"], oc, total,
                                    _int_arg(a.get("page"), 1) or 1, int(p["display"]))
        if moved:
            note = (note + "\n" + moved) if note else moved
    for d in items:                                     # 결과에 약칭을 함께 보인다(F2)
        ab = _ALIAS_OF.get(_name_key(pick(d, "법령명한글", "법령명")))
        if ab:
            d["약칭"] = ", ".join(ab[:3])
    out = fmt_search("법령 검색결과", total, page, items, "get_law_article")
    return (note + "\n" + out) if note else out


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def _digits(x):
    """문자열에서 첫 숫자묶음을 정수로(없으면 0). 조문번호/가지번호 매칭용."""
    m = re.search(r"\d+", str(x or ""))
    return int(m.group()) if m else 0


def _text_of(v):
    """*내용(항내용/호내용/목내용 등) 값에서 텍스트만 순서대로 뽑아 합친다.
    법제처 eflaw 는 깊게 중첩된 조문(항→호→목→세목 1)2))에서 *내용을 '문자열'이 아니라
    '리스트(때로 dict 중첩)'로 돌려준다. 그대로 clean_text 에 넣으면 re.sub 가 죽으므로,
    str·list·dict 어떤 형태든 재귀로 평탄화해 텍스트를 회수한다(누락 없이)."""
    if v is None:
        return ""
    if isinstance(v, str):
        return clean_text(v)
    if isinstance(v, list):
        return "\n".join(p for p in (_text_of(x) for x in v) if p)
    if isinstance(v, dict):
        parts = [_text_of(val) for k, val in v.items() if str(k).endswith("내용")]
        if not any(parts):   # '내용' 키가 없으면 문자열 leaf 라도 긁는다
            parts = [clean_text(val) for val in v.values() if isinstance(val, str)]
        return "\n".join(p for p in parts if p)
    return clean_text(str(v))


def _indent(text, prefix):
    """여러 줄 텍스트의 각 줄에 들여쓰기 접두어를 붙인다."""
    return "\n".join(prefix + ln for ln in text.split("\n"))


def _emit_unit(unit, out):
    """조문단위 1개를 조-항-호-목 들여쓰기로 출력. 번호(①·1.·가.)는 *내용에 이미
    포함되어 있어 재구성 없이 사용. *내용이 리스트/중첩이어도 _text_of 로 안전 추출."""
    if not isinstance(unit, dict):
        return
    yn = (unit.get("조문여부") or "").strip()
    # 조문내용도 리스트일 수 있다(조 직속 표: [머리문장, <img>, ASCII표행…]) → _text_of 로 처리
    body = _text_of(unit.get("조문내용"))
    if body:
        # 조문여부가 '조문'이 아니면 편/장/절 등 구조 헤더로 표시
        out.append(("《%s》" % body) if (yn and yn != "조문") else ("\n" + body))
    for hang in _as_list(unit.get("항")):
        if not isinstance(hang, dict):
            continue
        ht = _text_of(hang.get("항내용"))
        if ht:
            out.append(_indent(ht, "  "))
        for ho in _as_list(hang.get("호")):
            if not isinstance(ho, dict):
                continue
            ht2 = _text_of(ho.get("호내용"))
            if ht2:
                out.append(_indent(ht2, "    "))
            for mok in _as_list(ho.get("목")):
                if not isinstance(mok, dict):
                    continue
                mt = _text_of(mok.get("목내용"))
                if mt:
                    out.append(_indent(mt, "      "))
        # 항 바로 밑에 목이 오는 꼴(호 없이 '가. 나.' — 2026-08-08 소득세법 §12① 실측). 호 루프만
        # 돌면 소리 없이 빠지므로 이어서 낸다(호 소속은 응답에 없어 차례만 지킨다).
        for mok in _as_list(hang.get("목")):
            if isinstance(mok, dict):
                mt = _text_of(mok.get("목내용"))
                if mt:
                    out.append(_indent(mt, "      "))


def _format_law_body(data, only_jo=None):
    """eflaw JSON -> 조-항-호-목 계층 텍스트. 구조 인식 실패 시 '' 반환(폴백 유도).
    only_jo 가 주어지면 전체본에서 그 조문(조+가지번호)만 추려서 출력한다.
    (법제처 API 는 JO 필터를 걸면 '조 직속 표'를 떨구는 quirk 가 있어, get_law_article 은
     JO 를 API 에 넘기지 않고 전체본을 받아 여기서 해당 조만 로컬 추출한다.)"""
    law_node = data.get("법령") if isinstance(data, dict) else None
    if not isinstance(law_node, dict):
        return ""
    jo = law_node.get("조문")
    if isinstance(jo, dict):
        units = _as_list(jo.get("조문단위"))
    elif isinstance(jo, list):
        units = jo
    else:
        units = []
    if not units:
        return ""
    if only_jo:                                   # 특정 조문만 추출
        code = jo_code(only_jo)
        jo_n, ji_n = _digits(code[:4]), _digits(code[4:])
        sel = [u for u in units if isinstance(u, dict)
               and _digits(u.get("조문번호")) == jo_n
               and _digits(u.get("조문가지번호")) == ji_n]
        if not sel:
            # 조용히 법령 전체를 덤프하면 모델이 폐지·조번호 오기를 인지하지 못한다 — 명시 안내
            return ("[조문 없음] %s — 이 시행본에 해당 조문이 없습니다(폐지·조번호 오기 가능). "
                    "list_law_history 로 다른 시행본을 확인하거나 verify_citation 으로 검증하세요."
                    % only_jo)
        units = sel
    out = []
    bi = law_node.get("기본정보") or {}
    name = bi.get("법령명_한글") or bi.get("법령명한글")
    if name:
        ef = bi.get("시행일자")
        out.append("=== %s%s ===" % (name, (" [시행 %s]" % ef) if ef else ""))
    for u in units:
        _emit_unit(u, out)
    return "\n".join(out).strip()


def _format_appendix(data, only_byl=None):
    """eflaw 전체본 JSON 의 별표(법령→별표→별표단위)에서 별표 본문을 텍스트로 뽑는다.
    별표내용은 §26 세율표처럼 리스트형(ASCII 표 등)이라 _text_of 로 처리.
    only_byl 지정 시 해당 별표번호만. 파일(PDF/HWP) 다운로드 링크도 함께 제공한다."""
    law_node = data.get("법령") if isinstance(data, dict) else None
    if not isinstance(law_node, dict):
        return ""
    byl = law_node.get("별표")
    if isinstance(byl, dict):
        units = _as_list(byl.get("별표단위"))
    elif isinstance(byl, list):
        units = byl
    else:
        units = []
    units = [u for u in units if isinstance(u, dict)]
    if not units:
        return ""
    want_n = _digits(only_byl) if only_byl else None
    out = []
    for u in units:
        if want_n is not None and _digits(u.get("별표번호")) != want_n:
            continue
        title = clean_text(u.get("별표제목") or u.get("별표제목문자열") or "")
        gubun = (u.get("별표구분") or "별표").strip()
        num = _digits(u.get("별표번호"))
        out.append("=== [%s %s] %s ===" % (gubun, num or "", title))
        content = _text_of(u.get("별표내용"))
        if content:
            out.append(content)
        for label, k in (("PDF", "별표서식PDF파일링크"), ("원본", "별표서식파일링크")):
            link = u.get(k) or ""
            if link.startswith("/"):
                link = "https://www.law.go.kr" + link
            if link:
                out.append("  [%s] %s" % (label, mask(link)))
        out.append("")
    return "\n".join(out).strip()


def _num_id(v):
    """식별자에서 숫자만 남긴다.

    검색 출력의 '[법령ID 001565]' 나 '280405 ' 를 모델이 그대로 넘기는 일이 잦은데,
    법제처는 잡문자가 섞이면 HTTP 500 을 낸다. 그러면 래퍼가 '네트워크/방화벽' 을
    의심하는 엉뚱한 메시지를 내보내 진단이 산으로 간다(2026-08-29 확인)."""
    return re.sub(r"\D", "", str(v or ""))


def _law_unavailable_note(a, text):
    """eflaw·law 양쪽이 모두 거부됐을 때 내보낼 진단. 아니면 빈 문자열.

    법제처는 ①활용신청 누락 ②없는 식별자 ③거부되는 target×식별자 조합 을
    모두 같은 '미신청' 문구로 돌려준다. 그 원문을 그대로 노출하면 읽는 쪽이
    반드시 ①로 오진한다 — 실제로 그렇게 두 번 오진됐다."""
    if not _looks_unsubscribed(text):
        return ""
    who = ("mst=%s" % a.get("mst")) if a.get("mst") else ("lawId=%s" % a.get("lawId"))
    return ("[조회 실패] 법령 본문을 가져오지 못했습니다 (%s).\n"
            "⚠️ 법제처가 돌려준 '미신청' 안내는 인증키 문제가 아닐 수 있습니다. "
            "없는 식별자이거나 거부되는 조합일 때도 같은 문구가 옵니다.\n"
            "→ 확인 순서: ①search_law 로 MST·법령ID 를 다시 확인 "
            "②lawId(6자리 법령ID)로 재시도 ③그래도 안 되면 OC 키 활용신청 상태 확인\n"
            "⚠️ 같은 값으로 반복 호출해도 결과는 동일합니다." % who)


def _law_fallback_note(p):
    """공포본(target=law)으로 떨어졌을 때만 경고를 붙인다.

    공포본과 시행일본은 실제로 크게 다를 수 있다 — 소득세법 실측(2026-08-29):
    law 시행 20260101(조문 393) vs eflaw 시행 20260701(조문 392), **본문이 다른
    조문 53개**, 제164조의4 는 law 에만 존재. 조용히 6개월 뒤진 조문을 현행처럼
    보여주면 세무 실무에서 그대로 사고가 된다."""
    if (p or {}).get("target") != "law":
        return ""
    return ("[공포본 대체] 시행일법령(eflaw) 조회가 되지 않아 공포본으로 대체했습니다. "
            "아래 시행일자 기준 본문이며 요청한 시행일본과 다를 수 있습니다"
            "(조문 신설·개정 미반영 가능).\n"
            "  과거 시점이면 list_law_history 의 그 행 mst·시행일자로 get_law_article(mst=..., efYd=...), "
            "현행이면 search_law 의 법령ID 로 get_law_article(lawId=\"...\") 로 다시 조회하세요.\n\n")


def _bi(text):
    """법령 전체본 JSON 의 기본정보. 해석 실패 시 빈 dict."""
    try:
        return (json.loads(text).get("법령") or {}).get("기본정보") or {}
    except Exception:
        return {}


def _mst_effective_date(law_name, mst, oc):
    """eflaw 연혁 목록에서 MST 의 '진짜' 시행일자를 찾는다. 못 찾으면 ''.

    과거본을 정확히 부르는 조합은 eflaw+MST+efYd 하나뿐이고, efYd 는 그 MST 의
    시행일과 **정확히 같아야** 한다(2026-09-11 실측 — MST 165310 에 20190101 은
    되고 20190601·20181231·20260701 은 전부 거부). law+MST 가 주는 시행일자는
    공포본 기준이라 쓸 수 없다(165310 → 20150101, 4년 어긋남)."""
    if not (law_name and mst):
        return ""
    for pg in range(1, HISTORY_MAX_PAGES + 1):
        p = {"OC": oc, "target": "eflaw", "type": "XML", "query": law_name,
             "display": "100", "page": str(pg)}
        total, _, items = parse_search(http_get("lawSearch.do", p))
        if not items:
            break
        for d in items:
            if pick(d, "법령일련번호") == mst and pick(d, "법령명한글", "법령명") == law_name:
                return _num_id(pick(d, "시행일자"))
        try:
            if pg * 100 >= int(total or 0):
                break
        except ValueError:
            break
    return ""


def _fetch_full_body(a, oc):
    """법령 전체본 조회. (text, params) 반환 — params 는 파싱캐시 키.

    ★원칙: 요청한 시점본을 **다른 시점본으로 조용히 대체하지 않는다.**
    v2.6.1 복구 사슬은 마지막 단계를 efYd 없는 eflaw+ID 로 불러, 과거본 MST 를
    넣어도 현행본으로 '복원'했다(2026-09-11 교육용 세션 보고, 재현 확인:
    MST 165310=2019-01-01 시행본 → [시행 20260701] 반환). 세무에서 과거 시점 법은
    경정청구·과거연도 검토의 핵심이라 이런 대체는 오답보다 위험하다.

    조합별 실측(2026-09-11, 소득세법 연혁본 3건):
      eflaw + MST          → 거부('미신청' 안내)
      eflaw + MST + efYd   → ★정확 (efYd 가 그 MST 의 시행일과 정확히 같을 때만)
      eflaw + ID  + efYd   → 과거 날짜면 빈 {}  (ID 로는 과거본을 못 부른다)
      eflaw + ID           → 현행 시행본
      law   + MST          → 공포본(시행일이 수년 어긋날 수 있음)
    """
    base = {"OC": oc, "type": "JSON"}
    mst_v, id_v = _num_id(a.get("mst")), _num_id(a.get("lawId"))
    efyd = _num_id(a.get("efYd"))
    if mst_v:
        base["MST"] = mst_v
    if id_v:
        base["ID"] = id_v
    if not (mst_v or id_v):
        raise ValueError("mst 또는 lawId 에 숫자가 없습니다 — "
                         "search_law 결과의 번호만 넘기세요(대괄호·라벨 제외).")
    ok = lambda t: not (_looks_empty_detail(t) or _looks_unsubscribed(t))

    # 0) 시행일이 주어지면 그 시점본을 곧바로 — 과거본 조회의 정답 조합
    if mst_v and efyd:
        p0 = {"OC": oc, "type": "JSON", "target": "eflaw", "MST": mst_v, "efYd": efyd}
        t0 = http_get("lawService.do", p0)
        if ok(t0):
            return t0, p0

    # 1) eflaw + 식별자 단독 (MST 단독은 2026-08-29 부터 거부되지만, 법제처가
    #    되돌릴 경우 가장 빠른 정답이라 남겨 둔다)
    p = dict(base, target="eflaw")
    text = http_get("lawService.do", p)
    if ok(text):
        return text, p
    if not mst_v:                           # lawId 만으로는 현행본뿐 — 더 할 게 없다
        return text, p

    # 2) law + MST — 법령명·법령ID·공포번호를 얻는다(본문은 공포본이라 최후 수단)
    p2 = {"OC": oc, "type": "JSON", "target": "law", "MST": mst_v}
    text2 = http_get("lawService.do", p2)
    if not ok(text2):
        return text, p                      # 둘 다 실패 — 원래 응답 그대로
    b2 = _bi(text2)
    law_id = _num_id(b2.get("법령ID"))
    law_name = str(b2.get("법령명_한글") or b2.get("법령명한글") or "").strip()

    # 3) eflaw + ID — 현행 시행본. 공포번호가 같으면 요청 MST 가 곧 현행본이다.
    if law_id:
        p3 = {"OC": oc, "type": "JSON", "target": "eflaw", "ID": law_id}
        text3 = http_get("lawService.do", p3)
        if ok(text3) and _bi(text3).get("공포번호") == b2.get("공포번호"):
            return text3, p3
        # 공포번호가 다르다 = 과거본(또는 시행예정본). 현행본으로 대체하면 안 된다.

    # 4) 과거본 — 목록에서 그 MST 의 진짜 시행일을 찾아 eflaw+MST+efYd
    ef = efyd or _mst_effective_date(law_name, mst_v, oc)
    if ef:
        p4 = {"OC": oc, "type": "JSON", "target": "eflaw", "MST": mst_v, "efYd": ef}
        text4 = http_get("lawService.do", p4)
        if ok(text4):
            return text4, p4

    # 5) 최후 수단 — 공포본. 시행일이 어긋날 수 있으므로 호출부가 경고를 붙인다.
    return text2, p2


def tool_get_law_appendix(a):
    """법령의 별표 본문 조회. eflaw 전체본을 받아 별표 노드를 추출(같은 MST 캐시공유)."""
    if not (a.get("mst") or a.get("lawId")):
        return "[입력 오류] mst(법령일련번호) 또는 lawId 가 필요합니다 — search_law 로 먼저 MST 를 얻으세요."
    text, p = _fetch_full_body(a, get_oc(a.get("law_oc")))
    try:
        data = http_get_json("lawService.do", p, text)
    except Exception:
        if _looks_unsubscribed(text):   # 미신청 HTML 을 일시 오류로 오인해 재호출하지 않게 구분
            return _detail("법령 별표", "별표", str(a.get("mst") or a.get("lawId") or ""), text)
        return ("[오류] 별표 응답을 해석하지 못했습니다(응답이 JSON 이 아님). "
                "mst 가 eflaw 용 법령일련번호인지 확인하세요.")
    body = _format_appendix(data, only_byl=a.get("byl"))
    if body:
        if len(body) > MAX_TEXT:              # 긴 별표(간이세액표 등) — 잘린다는 것과 다음 길을 알린다
            bi = (data.get("법령") or {}).get("기본정보") or {}
            nm = clean_text(str(bi.get("법령명_한글") or bi.get("법령명한글") or "법령명"))
            return cap(body, MAX_TEXT) + (
                "\n\n➡ 이 별표는 %s자라 잘렸습니다. get_annex(law_name=\"%s\", annex_no=\"%s\", page=2) 로 쪽을 넘기거나 "
                "find=\"찾을 글\"(예: 월급여 '3,000') 로 필요한 줄만 보세요(표 그림 줄을 빼서 더 짧게 나옵니다)."
                % (format(len(body), ","), nm, a.get("byl") or "번호"))
        return cap(body, MAX_TEXT)
    allb = _format_appendix(data)
    if a.get("byl") and allb:
        nums = ", ".join(sorted(set(re.findall(r"\[별표 (\d+)\]", allb)), key=int))
        return "[별표 %s 없음] 이 법령의 별표 번호: %s" % (a.get("byl"), nums or "?")
    return ("[별표 없음] 이 법령 전체본에 별표가 없습니다. "
            "별표 '제목/키워드'로 search_law_appendix 를 써보세요.")


# ----- 부칙(附則): 시행일·적용례·경과조치 -----
#   법령 전체본의 '부칙' 노드에는 역대 개정 부칙이 공포번호별로 누적 수록된다
#   (라이브 확인: 조특법 현행본 286597 에 부칙 210건). 따라서 특정 개정의 시행일·
#   적용례는 연혁본 MST 없이도 '현행본 MST + 공포번호'로 바로 찾는 것이 정석.
def _addenda_units(data):
    """전체본 JSON 에서 부칙단위 dict 목록을 (공포번호 오름차순 그대로) 추출."""
    law_node = data.get("법령") if isinstance(data, dict) else None
    if not isinstance(law_node, dict):
        return []
    bu = law_node.get("부칙")
    units = _as_list(bu.get("부칙단위")) if isinstance(bu, dict) else _as_list(bu)
    return [u for u in units if isinstance(u, dict)]


def _select_addenda(units, no=None, query=None):
    """부칙 선택 규칙: no(공포번호) 정확일치 > query(본문 포함, 최신 3건) > 최신 1건.
    (선택목록, 안내문) 반환 — 선택이 비면 안내문에 사유를 담는다."""
    if no:
        sel = [u for u in units if _digits(u.get("부칙공포번호")) == _digits(no)]
        if not sel:
            recent = ", ".join(str(_digits(u.get("부칙공포번호"))) for u in units[-15:])
            return [], ("[부칙 없음] 공포번호 %s 의 부칙이 수록되어 있지 않습니다. "
                        "수록 공포번호(최근 15개): %s" % (_digits(no), recent))
        return sel, ""
    if query:
        q = str(query).strip()
        sel = [u for u in units if q in _text_of(u.get("부칙내용"))]
        if not sel:
            return [], ("[검색 결과 없음] 부칙 본문에 '%s' 포함 부칙이 없습니다(총 %d건 수록). "
                        "list_law_history 로 개정 공포번호를 확인해 no= 로 지정하세요." % (q, len(units)))
        # 매칭 공포번호 전체를 안내 — 표시(최신 3건)·길이 캡에 잘려도 no= 로 후속 조회 가능
        nos = ", ".join(str(_digits(u.get("부칙공포번호"))) for u in sel)
        note = ("'%s' 포함 부칙 %d건 (공포번호: %s) — 최신 %d건 표시, 다른 건은 no= 로 지정."
                % (q, len(sel), nos, min(3, len(sel))))
        return sel[-3:], note   # 최신 3건이면 시행일·적용례 추적에 충분
    return units[-1:], ""     # 미지정 → 최신 부칙


def _format_addendum(u):
    no = _digits(u.get("부칙공포번호"))
    d = re.sub(r"\D", "", str(u.get("부칙공포일자") or ""))
    date = "%s.%s.%s" % (d[:4], int(d[4:6] or 0), int(d[6:8] or 0)) if len(d) == 8 else d
    body = _text_of(u.get("부칙내용")).strip()
    return "=== 부칙 <제%s호, %s> ===\n%s" % (no, date, body)


def tool_get_law_addenda(a):
    """법령 부칙 조회 — 시행일 단서·적용례·경과조치 원문."""
    if not (a.get("mst") or a.get("lawId")):
        return ("[입력 오류] mst(법령일련번호)가 필요합니다 — search_law 로 '현행본' MST 를 얻으세요. "
                "부칙은 현행본에 역대 공포번호별로 누적 수록되어 있어 연혁본 MST 가 필요 없습니다.")
    text, p = _fetch_full_body(a, get_oc(a.get("law_oc")))
    try:
        data = http_get_json("lawService.do", p, text)
    except Exception:
        return _detail("법령 부칙", "법령", str(a.get("mst") or a.get("lawId") or ""), text)
    units = _addenda_units(data)
    if not units:
        return "[부칙 없음] 이 전체본에서 부칙 노드를 찾지 못했습니다(mst 가 법령 전체본용인지 확인)."
    sel, note = _select_addenda(units, no=a.get("no"), query=a.get("query"))
    if not sel:
        return note
    bi = (data.get("법령") or {}).get("기본정보") or {}
    name = clean_text(str(bi.get("법령명_한글") or bi.get("법령명한글") or ""))
    head = "[%s] 부칙 총 %d건 수록 — %d건 표시" % (name or "법령", len(units), len(sel))
    if note:                              # query 매칭 공포번호 전체 안내
        head += "\n" + note
    if not a.get("no") and not a.get("query"):
        recent = ", ".join(str(_digits(u.get("부칙공포번호"))) for u in units[-10:])
        head += ("\n(특정 개정의 시행일·적용례는 no=공포번호 로 지정하세요. "
                 "최근 공포번호: %s)" % recent)
    return cap(head + "\n\n" + "\n\n".join(_format_addendum(u) for u in sel), MAX_TEXT)


def tool_get_law_article(a):
    if a.get("article") and not a.get("jo"):
        a = dict(a, jo=a["article"])
    if not (a.get("mst") or a.get("lawId")) and a.get("law_name"):
        # F2 — 법령 이름(약칭·붙여 쓴 이름 됨)으로 현행 판을 본다. 머리에 풀이 안내.
        oc = get_oc(a.get("law_oc"))
        inf, note = _find_law(a["law_name"], oc)
        if not inf:
            return _law_not_found(a["law_name"], oc)
        if inf["state"] == "폐지":
            return ("[폐지 법령] %s 은 지금 시행 중인 판이 없습니다. 그때 조문은 "
                    "law_as_of(law_name=\"%s\", date=\"YYYY-MM-DD\", article=\"제N조\") 로 보세요."
                    % (inf["name"], inf["name"]))
        res = tool_get_law_article(dict(a, law_name=None, lawId=inf["id"]))
        return (note + "\n" + res) if note else res
    if not (a.get("mst") or a.get("lawId")):
        return ("[입력 오류] mst(법령일련번호)·lawId·law_name(법령 이름 — 약칭 됨) 가운데 하나가 필요합니다 "
                "— 예: get_law_article(law_name=\"조특법\", jo=\"제100조의32\")")
    if "부칙" in str(a.get("jo") or ""):
        return ("[안내] 부칙(시행일·적용례·경과조치)은 get_law_addenda 도구로 조회하세요 — "
                "get_law_addenda(mst=현행본MST, no=공포번호) 또는 query='제95조의2' 형태. "
                "부칙은 현행본에 역대 공포번호별로 누적 수록됩니다.")
    # ★ JO 를 API 에 넘기지 않는다: JO 필터를 걸면 '조 직속 표'(예: 상증세법 §26 세율표)가
    #   누락되는 법제처 quirk 가 있다. 전체본(같은 MST 라 캐시 공유)을 받아 해당 조만 로컬 추출.
    #   시행예정 연혁본 MST 는 eflaw 가 거부 → _fetch_full_body 가 공포본(law)으로 폴백.
    text, p = _fetch_full_body(a, get_oc(a.get("law_oc")))
    data = None
    try:
        note = _law_unavailable_note(a, text)
        if note:
            return note
        data = http_get_json("lawService.do", p, text)   # 파싱 캐시(재파싱 방지)
        body = _format_law_body(data, only_jo=a.get("jo"))
        if body:
            return cap(_law_fallback_note(p) + body, MAX_TEXT)
    except Exception:
        pass
    return fmt_detail("법령 전문", text, data=data)   # data 전달로 같은 텍스트 2회 파싱 방지


_VER_STATE = {"현행": "★현행 — 지금 시행 중인 판", "연혁": "연혁 — 지난 판",
              "시행예정": "시행예정 — 아직 시행 전"}     # 법제처 현행연혁코드 → 목록 '판 상태' 칸


def tool_list_law_history(a):
    """법령 시행일별 연혁 목록(eflaw 검색 + efYd 범위).

    ★옛 전제 정정(2026-09-11): 예전엔 "efYd 는 본문 호출에서 동작하지 않으므로
    MST 만으로 버전을 고른다" 고 적어 두었으나 지금은 정반대다. 법제처가
    eflaw+MST 단독 조회를 거부하게 된 뒤로 과거본을 정확히 부르는 조합은
    eflaw+MST+efYd 하나뿐이다. 그래서 힌트에 mst 와 efYd 를 함께 싣는다.

    v2.13.1 — 판마다 현행 · 연혁 · 시행예정을 보인다. 목록은 시행일이 늦은 차례라 맨 위가 시행예정 판인
    일이 흔한데(소득세법 2026-10-29 실측: 위 8행이 시행예정 · 9행째가 현행), 표시 없이 첫 행을 안내하면
    아직 시행 전인 조문을 현행처럼 인용하게 된다. 안내는 이 쪽에 현행 판이 있으면 그 행을 가리킨다."""
    p = {"OC": get_oc(a.get("law_oc")), "target": "eflaw", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    note = ""
    if a.get("query"):
        q, note = resolve_law_name(a["query"])          # F2 — 약칭이면 정식 이름으로
        p["query"] = q or a["query"]
    fd, td = a.get("from_date"), a.get("to_date")
    fd, td = (_norm_date(fd) or fd) if fd else fd, (_norm_date(td) or td) if td else td
    if fd or td:
        p["efYd"] = "%s~%s" % (fd or "", td or "")
    total, page, items = parse_search(http_get("lawSearch.do", p))
    cnt = {}
    for d in items:
        st = (d.get("현행연혁코드") or "").strip()
        if st:
            d["판 상태"] = _VER_STATE.get(st, st)
            cnt[st] = cnt.get(st, 0) + 1
    out = fmt_search("법령 시행일 연혁", total, page, items, "get_law_article")
    if items:
        cur = next((d for d in items if (d.get("현행연혁코드") or "").strip() == "현행"), None)
        row = cur or items[0]
        m0, e0 = _num_id(pick(row, "법령일련번호")), _num_id(pick(row, "시행일자"))
        if m0 and e0:
            if cur:
                hint = ("➡ 지금 시행 중인 판(현행) 조문:  get_law_article(mst=\"%s\", efYd=\"%s\", jo=\"제N조\")"
                        % (m0, e0))
                hint += chr(10) + "   (지난 판 · 시행예정 판은 그 행의 MST 와 시행일자를 짝으로 넘길 것)"
            else:
                hint = ("➡ 그 시점 조문:  get_law_article(mst=\"%s\", efYd=\"%s\", jo=\"제N조\")"
                        % (m0, e0))
                hint += chr(10) + "   (다른 행을 볼 때도 그 행의 MST 와 시행일자를 짝으로 넘길 것)"
            out = re.sub(r"➡ 전문 조회:.*", lambda _m: hint, out)
    if cnt:
        line = "판 상태(이 쪽): " + " · ".join("%s %d" % (s, cnt[s]) for s in ("시행예정", "현행", "연혁")
                                               if cnt.get(s))
        if cnt.get("시행예정"):
            line += " — 시행예정 판은 아직 시행 전이니 현행으로 인용하지 말 것"
            if not cnt.get("현행"):
                line += ("\n※ 현행 판은 이 쪽 뒤에 있습니다 — page 를 넘기거나 "
                         "law_as_of(law_name, date) 로 그날 시행 판을 바로 보세요")
        head, _, rest = out.partition("\n")
        out = head + "\n" + line + "\n" + rest
    if note:
        out = note + "\n" + out
    return out + ("\n\n💡 특정 개정의 시행일 단서·적용례(부칙) 원문은 "
                  "get_law_addenda(mst=현행본MST, no=공포번호) 로 조회하세요 — "
                  "부칙은 현행본에 역대 공포번호별로 누적 수록됩니다. "
                  "(과거·시행예정본은 mst 와 그 행 시행일자를 efYd 로 함께 넘길 것)")


def jo_code(jo):
    """'제38조' / '38' / '제10조의2' / '§38' / '§10의2' / '10의2' -> 6자리 AAAABB. 이미 6자리면 그대로."""
    jo = str(jo).strip()
    if re.fullmatch(r"\d{6}", jo):
        return jo
    m = re.search(r"제?\s*(\d+)\s*조(?:\s*의\s*(\d+))?", jo)
    if m:
        return "%04d%02d" % (int(m.group(1)), int(m.group(2) or 0))
    if jo.isdigit():
        return "%04d00" % int(jo)
    m = re.fullmatch(r"§?\s*(\d+)(?:\s*의\s*(\d+))?\s*(?:[%s].*)?" % _CIRC, jo)    # §38 · §10의2 · 10의2 · §89①
    if m:
        return "%04d%02d" % (int(m.group(1)), int(m.group(2) or 0))
    return jo


def _collect_articles(obj, acc):
    if isinstance(obj, dict):
        title = obj.get("조문제목") or obj.get("조문번호")
        body = obj.get("조문내용")
        if title and isinstance(title, str):
            label = str(title).strip()
            if isinstance(body, str) and body.strip():
                acc.append(("【%s】" % label, body))
            else:
                acc.append(("【%s】" % label, ""))
        for k, v in obj.items():
            if k in ("조문제목", "조문내용", "조문번호"):
                continue
            _collect_articles(v, acc)
    elif isinstance(obj, list):
        for it in obj:
            _collect_articles(it, acc)


# =============================================================================
# 행정규칙(훈령·예규·고시) — 국세청 예규·해석의 실제 경로 (target=admrul)
#   국세청 소관부처코드 org=1210000 (라이브 확인). expc(법령해석례)는 회신기관이
#   대부분 '법제처'라 국세청 자체 예규를 담지 않으므로 admrul 이 정답.
# =============================================================================
def tool_search_admin_rule(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "admrul", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("search"):
        p["search"] = str(a["search"])
    if a.get("org"):
        p["org"] = str(a["org"])      # 소관부처코드(국세청=1210000)
    if a.get("knd"):
        p["knd"] = str(a["knd"])      # 종류(불확실 — 생략 권장)
    if a.get("nw"):
        p["nw"] = str(a["nw"])        # 1=현행 2=연혁
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("행정규칙(훈령·예규·고시) 검색결과", total, page, items, "get_admin_rule")


def _admrul_article(text, jo):
    """행정규칙 JSON 의 조문내용(문자열 리스트)에서 특정 조만 골라낸다.

    조문내용은 "제12조(제목) 본문…" 형태의 평문이라 조 번호를 정규식으로 읽는다.
    가지번호(제12조의3)도 구분한다. 인식 실패 시 빈 문자열을 돌려 호출부가 전체
    응답으로 떨어지게 한다."""
    m = re.match(r"\s*제?\s*(\d+)\s*조(?:\s*의\s*(\d+))?", jo)
    if not m:
        return ""
    want = (m.group(1), m.group(2) or "")
    try:
        data = json.loads(text)
    except Exception:
        return ""
    node = data.get("AdmRulService") or (next(iter(data.values())) if len(data) == 1 else {})
    if not isinstance(node, dict):
        return ""
    arts = node.get("조문내용") or []
    if isinstance(arts, str):
        arts = [arts]
    name = ((node.get("행정규칙기본정보") or {}).get("행정규칙명") or "").strip()
    hit = []
    for t in arts:
        if not isinstance(t, str):
            continue
        mm = re.match(r"\s*제\s*(\d+)\s*조(?:\s*의\s*(\d+))?", t)
        if mm and (mm.group(1), mm.group(2) or "") == want:
            hit.append(t.strip())
    if not hit:
        return ("[조문 없음] %s %s — 이 행정규칙에 해당 조문이 없습니다"
                "(조번호 오기·개정 삭제 가능). jo 를 빼고 호출하면 전체를 볼 수 있습니다."
                % (name or "행정규칙", jo))
    return "=== %s %s ===\n\n%s" % (name or "행정규칙", jo, "\n".join(hit))


def tool_get_admin_rule(a):
    """행정규칙 전문. jo 를 주면 그 조문만 추린다.

    행정규칙은 조문이 매우 많다(법인세 사무처리규정 = 249개, 약 70KB). 전체를
    돌려주면 출력 한도에서 잘려 뒤쪽 조문을 아예 못 본다 — 특정 조를 찾는
    실사용에서는 jo 로 좁히는 편이 정확하다."""
    p = {"OC": get_oc(a.get("law_oc")), "target": "admrul", "type": "JSON", "ID": str(a["id"])}
    if a.get("ruleName"):
        p["LM"] = a["ruleName"]
    text = http_get("lawService.do", p)
    jo = str(a.get("jo") or "").strip()
    if jo:
        body = _admrul_article(text, jo)
        if body:
            return cap(body, MAX_TEXT)
    return _detail("행정규칙 전문", "행정규칙", a.get("id", ""), text)


# =============================================================================
# 인용 검증 (anti-hallucination 핵심) — verify_citation
#   법제처 사건번호는 목록에 '대법원-2017-두-38249' 형식으로 저장되나 검색은 압축형
#   '2017두38249' 으로 매칭된다(라이브 확인). 입력/결과를 모두 정규화해 '정확매칭'만
#   verified=true. 검색만으로는 '유사'에 불과하므로 정규화 동치 비교가 검증의 핵심.
# =============================================================================
CASE_RE = re.compile(r"(\d{2,4})\s*-?\s*([가-힣]{1,3})\s*-?\s*(\d{1,6})")
TRIB_RE = re.compile(r"(?:조심|국심|조세심판)\s*(\d{4})\s*-?\s*([가-힣]{1,3})\s*-?\s*(\d{1,6})")
HEONJAE_RE = re.compile(r"\d{2,4}\s*-?\s*헌[가-힣]\s*-?\s*\d+")   # 2022헌바189 등(헌가·헌바·헌마…)
LAWART_RE = re.compile(r"(.*?(?:법|령|규칙|예규|고시|훈령))\s*(제\s*\d+\s*조(?:\s*의\s*\d+)?)")

LAW_ALIASES = {
    "상증세법": "상속세 및 증여세법", "상증법": "상속세 및 증여세법",
    "소세법": "소득세법", "법세법": "법인세법", "부가세법": "부가가치세법",
    "국기법": "국세기본법", "국징법": "국세징수법", "조특법": "조세특례제한법",
    "지기법": "지방세기본법", "지특법": "지방세특례제한법",
}


def _norm_caseno(s):
    """'대법원-2017-두-38249' / '2017두38249' / '2017 두 38249' -> '2017두38249'."""
    m = CASE_RE.search(s or "")
    return (m.group(1) + m.group(2) + m.group(3)) if m else ""


def _classify(cit, hint):
    if hint and hint != "auto":
        return hint
    if "조심" in cit or "국심" in cit or TRIB_RE.search(cit):
        return "tax_tribunal"
    if HEONJAE_RE.search(cit):           # 헌재 사건번호(precedent 보다 먼저)
        return "constitutional"
    if LAWART_RE.search(cit):
        return "law_article"
    if CASE_RE.search(cit):
        return "precedent"
    return "interpretation"


def _verdict(ok, kind, d=None, idv="", follow="", want="", reason="",
             note="", candidates=None, extra=None, echo=""):
    lines = ["VERIFIED: %s" % ("true" if ok else "false"), "종류: %s" % kind]
    if want:
        lines.append("대상: %s" % want)
    if ok and d is not None:
        for label in ("사건번호", "청구번호", "안건번호", "법원명", "사건종류명", "처분청", "재결청",
                      "선고일자", "의결일자", "회신일자", "법령명한글", "법령명",
                      "시행일자", "공포일자", "세목", "회신기관명", "데이터출처명"):
            v = pick(d, label)
            if v:
                lines.append("%s: %s" % (label, cap(clean_text(v), 200)))
        name = pick(d, *NAME_KEYS)
        if name:
            lines.append("명칭: %s" % cap(clean_text(name), 200))
        if extra:
            for k, v in extra.items():
                lines.append("%s: %s" % (k, v))
        if idv:
            lines.append("일련번호(ID): %s" % idv)
            if follow:
                param = "mst" if follow == "get_law_article" else "id"
                lines.append('➡ 후속 조회: %s(%s="%s")' % (follow, param, idv))
        if note:
            lines.append("⚠ %s" % note)
    else:
        if reason:
            lines.append("사유: %s" % reason)
        if echo:
            lines.append("입력: %s" % echo)
        lines.append("⛔ 이 인용을 사용하지 마세요. 법제처 공식 API에서 정확히 일치하는 항목을 "
                     "확인하지 못했습니다. 추측·생성 금지 — search_* 로 재검색 후 일련번호로 재검증하세요.")
    if candidates:
        lines.append("\n유사 후보(참고용 — 자동 채택 금지):")
        for c in candidates[:5]:
            lines.append("  · [%s] %s | %s" % (
                id_of(c), pick(c, *NAME_KEYS),
                pick(c, "사건번호", "청구번호", "안건번호", "법령명한글")))
    return "\n".join(lines)


def _verify_precedent(a, cit):
    want = _norm_caseno(a.get("case_no") or cit)
    if not want:
        return _verdict(False, "판례", reason="사건번호 형식을 인식할 수 없음", echo=cit)
    p = {"OC": get_oc(a.get("law_oc")), "target": "prec", "type": "XML",
         "display": str(VERIFY_DISPLAY), "query": want}
    _, _, items = parse_search(http_get("lawSearch.do", p))
    exact = [d for d in items if _norm_caseno(pick(d, "사건번호", "사건명", "판례명")) == want]
    if not exact:                       # 판례명 검색 실패 시 본문검색 폴백
        p["search"] = "2"
        _, _, items2 = parse_search(http_get("lawSearch.do", p))
        exact = [d for d in items2 if _norm_caseno(pick(d, "사건번호", "사건명", "판례명")) == want]
        items = items or items2
    if exact:
        exact.sort(key=lambda d: pick(d, "선고일자"), reverse=True)
        exact.sort(key=lambda d: 0 if "대법원" in pick(d, "사건번호", "법원명") else 1)
        d = exact[0]
        notes = []
        if len(exact) > 1:
            notes.append("동일 사건번호 %d건 — 법원·선고일자로 확정하세요" % len(exact))
        src, jong = pick(d, "데이터출처명"), pick(d, "사건종류명")
        # 법제처 lawService 는 법원(대법원) 출처만 전문 제공. 국세법령정보시스템 출처
        # (=대개 '일반행정'으로 분류된 조세행정 판례)는 전문 미제공 — 둘 중 하나만 걸려도 경고.
        if "국세법령정보" in src or "일반행정" in jong:
            notes.append("출처=%s·종류=%s → get_precedent 전문 미제공 가능"
                         "(법제처는 법원 출처만 전문 제공; 사건명·요지를 활용하거나 상고심을 확인)"
                         % (src or "?", jong or "?"))
        return _verdict(True, "판례", d, idv=id_of(d), follow="get_precedent",
                        want=want, note=" / ".join(notes),
                        candidates=(exact if len(exact) > 1 else None))
    return _verdict(False, "판례",
                    reason="법제처 판례 DB에 일치하는 사건번호 없음(미수록·오래된 판례 또는 번호 오기 가능)",
                    want=want, candidates=items[:5])


def _verify_tax_tribunal(a, cit):
    want = _norm_caseno(a.get("claim_no") or cit)
    if not want:
        return _verdict(False, "조세심판례", reason="청구번호 형식을 인식할 수 없음", echo=cit)
    p = {"OC": get_oc(a.get("law_oc")), "target": "ttSpecialDecc", "type": "XML",
         "display": str(VERIFY_DISPLAY), "query": want}
    _, _, items = parse_search(http_get("lawSearch.do", p))
    exact = [d for d in items if _norm_caseno(pick(d, "청구번호", "사건번호", "재결례명")) == want]
    if exact:
        d = exact[0]
        return _verdict(True, "조세심판례", d, idv=id_of(d), follow="get_tax_tribunal", want=want)
    return _verdict(False, "조세심판례",
                    reason="조세심판원 DB에 일치하는 청구번호 없음", want=want, candidates=items[:5])


def _verify_law_article(a, cit):
    m = LAWART_RE.search(cit)
    law_name = a.get("law_name") or (m.group(1).strip() if m else "")
    article = a.get("article") or (m.group(2).strip() if m else "")
    law_name = resolve_law_name(LAW_ALIASES.get(law_name, law_name))[0] or law_name   # F2 약칭 사전
    if not law_name:
        return _verdict(False, "법령조문", reason="법령명을 인식할 수 없음", echo=cit)
    sp = {"OC": get_oc(a.get("law_oc")), "target": "law", "type": "XML",
          "display": "20", "query": law_name}
    _, _, laws = parse_search(http_get("lawSearch.do", sp))
    exact = [d for d in laws if pick(d, "법령명한글", "법령명") == law_name]
    cand = exact or [d for d in laws if law_name in pick(d, "법령명한글", "법령명")]
    if not cand:
        return _verdict(False, "법령조문",
                        reason="법령명이 현행 법령에 없음(약칭/오기 가능)",
                        want=law_name, candidates=laws[:5])
    law = cand[0]
    mst = id_of(law)
    if not article:                     # 법령 자체만 검증
        return _verdict(True, "법령", law, idv=mst, follow="get_law_article", want=law_name)
    # ★eflaw+MST 직접 호출 금지. 법제처가 MST 단독 eflaw 조회를 거부하고 "미신청"
    #   안내를 돌려주므로(2026-08-29 확인) 실재 조문도 전부 false 가 났다.
    #   _fetch_full_body 의 복구 체인을 태우고 조문 선별은 로컬에서 한다
    #   (JO 를 API 에 넘기면 조 직속 표가 떨어지는 quirk 도 함께 피한다 — v2.2.4).
    # 본문 조회가 "실패" 한 것과 조문이 "없는" 것은 다르다. 둘을 뭉뚱그려 false 를
    # 내면 실재 조문을 없다고 보고하게 된다(2026-09-08 현장 오판). 조회 실패는
    # 검증 불가로 분리해 돌려준다.
    acc = []
    fetch_failed = ""
    try:
        gtext, gp = _fetch_full_body({"mst": mst}, get_oc(a.get("law_oc")))
        if _looks_unsubscribed(gtext) or _looks_empty_detail(gtext):
            fetch_failed = "법령 본문을 가져오지 못함(활용신청·식별자·조합 문제)"
        else:
            gdata = http_get_json("lawService.do", gp, gtext)        # 파싱 캐시 공유
            body = _format_law_body(gdata, only_jo=article)
            if body and not body.startswith("[조문 없음]"):
                acc = [(article, body)]
    except Exception as e:
        fetch_failed = "본문 조회 중 오류: %s" % str(e).splitlines()[0][:80]
    if not acc and fetch_failed:
        return _verdict(False, "법령조문", law, idv=mst,
                        reason=("검증 불가 — %s. 조문이 없다는 뜻이 아니다. "
                                "get_law_article 로 직접 조회해 확인할 것." % fetch_failed),
                        want="%s %s" % (law_name, article))
    if acc and any(clean_text(v) for _, v in acc):
        title = acc[0][0] if acc else ""
        return _verdict(True, "법령조문", law, idv=mst, follow="get_law_article",
                        want="%s %s" % (law_name, article),
                        extra={"조문": "%s %s" % (article, title), "JO": jo_code(article)})
    return _verdict(False, "법령조문", law, idv=mst,
                    reason="법령은 존재하나 해당 조문이 없음(폐지·조번호 오기 가능)",
                    want="%s %s" % (law_name, article))


def _verify_constitutional(a, cit):
    want = _norm_caseno(a.get("case_no") or cit)
    if not want:
        return _verdict(False, "헌재결정례", reason="헌재 사건번호 형식을 인식할 수 없음", echo=cit)
    p = {"OC": get_oc(a.get("law_oc")), "target": "detc", "type": "XML",
         "display": str(VERIFY_DISPLAY), "query": want}
    _, _, items = parse_search(http_get("lawSearch.do", p))
    exact = [d for d in items if _norm_caseno(pick(d, "사건번호", "사건명")) == want]
    if exact:
        d = exact[0]
        return _verdict(True, "헌재결정례", d, idv=id_of(d), follow="get_constitutional", want=want)
    return _verdict(False, "헌재결정례",
                    reason="헌재 DB에 일치하는 사건번호 없음", want=want, candidates=items[:5])


def _verify_interpretation(a, cit):
    p = {"OC": get_oc(a.get("law_oc")), "target": "expc", "type": "XML",
         "display": "20", "query": cit}
    _, _, items = parse_search(http_get("lawSearch.do", p))
    if items:
        return _verdict(True, "법령해석례", items[0], idv=id_of(items[0]),
                        follow="get_interpretation", want=cit,
                        note="제목 기반 매칭 — 안건번호·회신일자로 최종 확인 권장",
                        candidates=(items[:5] if len(items) > 1 else None))
    return _verdict(False, "법령해석례",
                    reason="법령해석례 DB에서 검색되지 않음(키워드/안건번호 확인)", want=cit)


def tool_verify_citation(a):
    cit = (a.get("citation") or "").strip()
    if not cit:
        cit = (a.get("case_no") or a.get("claim_no") or a.get("law_name") or "").strip()
    if not cit:
        return _verdict(False, "미상", reason="검증할 인용이 비어 있습니다")
    kind = _classify(cit, a.get("kind"))
    if kind == "precedent":
        return _verify_precedent(a, cit)
    if kind == "law_article":
        return _verify_law_article(a, cit)
    if kind == "tax_tribunal":
        return _verify_tax_tribunal(a, cit)
    if kind == "constitutional":
        return _verify_constitutional(a, cit)
    return _verify_interpretation(a, cit)


# =============================================================================
# 추가 도메인 (Phase 3) — 헌재결정례·행정심판 재결례·자치법규·영문법령
#   모두 동일 엔드포인트/파서 재사용. 상세 id 파라미터(라이브 확인):
#   detc=ID, decc=ID, ordin=MST, elaw=MST.
# =============================================================================
def tool_search_constitutional(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "detc", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("search"):
        p["search"] = str(a["search"])
    if a.get("edYd"):
        p["edYd"] = a["edYd"]          # 종국일자 범위 YYYYMMDD~YYYYMMDD
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("헌법재판소 결정례 검색결과", total, page, items, "get_constitutional")


def tool_get_constitutional(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "detc", "type": "JSON", "ID": str(a["id"])}
    return _detail("헌재 결정례 전문", "결정례", a.get("id", ""), http_get("lawService.do", p))


def tool_search_admin_appeal(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "decc", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("search"):
        p["search"] = str(a["search"])
    if a.get("rslYd"):
        p["rslYd"] = a["rslYd"]        # 의결일자 범위
    if a.get("dpaYd"):
        p["dpaYd"] = a["dpaYd"]        # 처분일자 범위
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("행정심판 재결례 검색결과", total, page, items, "get_admin_appeal")


def tool_get_admin_appeal(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "decc", "type": "JSON", "ID": str(a["id"])}
    return _detail("행정심판 재결례 전문", "재결례", a.get("id", ""), http_get("lawService.do", p))


def tool_search_ordinance(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "ordin", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("org"):
        p["org"] = str(a["org"])       # 시·도 코드
    if a.get("sborg"):
        p["sborg"] = str(a["sborg"])   # 시·군·구 코드
    if a.get("knd"):
        p["knd"] = str(a["knd"])       # 30001=조례 30002=규칙
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("자치법규(조례·규칙) 검색결과", total, page, items, "get_ordinance")


def _ordin_code(u):
    """자치법규 조 단위 → 6자리 조문 번호('000602' = 제6조의2). 조문번호 칸에는 같은 값 두 개가 목록으로 온다(실측) —
    없으면 조내용 머리('제6조의2(…)')에서 읽는다."""
    for x in _as_list(u.get("조문번호")):
        s = re.sub(r"\D", "", str(x or ""))
        if len(s) == 6:
            return s
    m = re.match(r"\s*제\s*(\d+)\s*조(?:\s*의\s*(\d+))?", str(u.get("조내용") or ""))
    return "%04d%02d" % (int(m.group(1)), int(m.group(2) or 0)) if m else ""


def _ordinance_article(text, code, mst):
    """자치법규 전문 JSON 에서 한 조만 고른다(v2.11.3). 법제처 자치법규 본문 조회(공식 ordinInfoGuide)에는 조문 변수가 없어
    JO 를 넘겨도 전문이 그대로 온다 — 2026-10-13 실측: 가평군 군세 감면 조례(MST 2124627) JO 있음 · 없음 모두 8,415자로 같음.
    그래서 전문을 받아 여기서 고른다. JSON 이 아니거나 조 단위가 없으면 None(→ 전문 안내 파이프로 넘김)."""
    try:
        svc = (json.loads(text) or {}).get("LawService") or {}
    except Exception:
        return None
    units = [u for u in _as_list((svc.get("조문") or {}).get("조")) if isinstance(u, dict)]
    arts = [u for u in units if str(u.get("조문여부") or "Y").upper() == "Y"]      # N = 장 · 절 머리
    if not arts:
        return None
    info = svc.get("자치법규기본정보") or {}
    name = pick(info, "자치법규명") or "자치법규"
    label = _jo_label(_digits(code[:4]), _digits(code[4:]))
    tail = "➡ 전문: get_ordinance(mst=\"%s\")" % mst
    hit = next((u for u in arts if _ordin_code(u) == code), None)
    if hit is None:
        codes = [c for c in (_ordin_code(u) for u in arts) if c]
        span = (" · 이 자치법규 조문 범위 %s ~ %s" % (_jo_label(_digits(codes[0][:4]), _digits(codes[0][4:])),
                                               _jo_label(_digits(codes[-1][:4]), _digits(codes[-1][4:])))
                if codes else "")
        return "[조문 없음] %s — %s 없음%s\n%s" % (name, label, span, tail)
    day = pick(info, "시행일자")
    meta = " · ".join(x for x in (pick(info, "지자체기관명"), ("시행 " + _fmt_d(day)) if day else "",
                                   "자치법규일련번호 " + mst) if x)
    return "\n".join(["=== %s %s ===" % (name, label), meta, "", clean_text(hit.get("조내용")), "", tail])


def tool_get_ordinance(a):
    if not (a.get("mst") or a.get("id")):
        return "[입력 오류] mst(자치법규일련번호)가 필요합니다 — search_ordinance 로 먼저 MST 를 얻으세요."
    mst = str(a.get("mst") or a.get("id"))
    code = jo_code(a["jo"]) if a.get("jo") else ""
    if a.get("jo") and not re.fullmatch(r"\d{6}", code):
        return "[입력 오류] jo 꼴을 알 수 없습니다 — 예 '제3조', '제6조의2', '§10의2', 6자리 '000602'."
    text = http_get("lawService.do", {"OC": get_oc(a.get("law_oc")), "target": "ordin", "type": "JSON", "MST": mst})
    if code:
        one = _ordinance_article(text, code, mst)
        if one:
            return one
    # _detail 경유: 미신청/전문 미제공 응답을 구분 안내(다른 get_* 와 동일 파이프)
    return _detail("자치법규 전문", "자치법규", mst, text)


def tool_search_english_law(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "elaw", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("영문법령 검색결과", total, page, items, "get_english_law")


def tool_get_english_law(a):
    if not (a.get("mst") or a.get("id")):
        return "[입력 오류] mst(법령일련번호)가 필요합니다 — search_english_law 로 먼저 MST 를 얻으세요."
    p = {"OC": get_oc(a.get("law_oc")), "target": "elaw", "type": "JSON",
         "MST": str(a.get("mst") or a.get("id"))}
    # _detail 경유: 미신청/전문 미제공 응답을 구분 안내(다른 get_* 와 동일 파이프)
    return _detail("영문법령 전문", "영문법령", str(a.get("mst") or a.get("id") or ""),
                   http_get("lawService.do", p))


# =============================================================================
# 법령 체계도(시행령·시행규칙 연계) + 별표/서식  (Phase 6)
#   lsStmd 의 법령체계도는 하위 법령명+MST 를 노출(라이브 확인) → 시행령/규칙 연계 가능.
#   별표/서식은 eflaw 본문에 없고 licbyl 로만 제공(파일/PDF 링크).
# =============================================================================
def _collect_related_laws(obj, acc, seen):
    if isinstance(obj, dict):
        name = obj.get("법령명") or obj.get("법령명한글")
        mst = obj.get("법령일련번호")
        if name and mst and mst not in seen:
            seen.add(mst)
            acc.append((str(name).strip(), str(mst).strip()))
        for v in obj.values():
            _collect_related_laws(v, acc, seen)
    elif isinstance(obj, list):
        for x in obj:
            _collect_related_laws(x, acc, seen)


def tool_get_law_structure(a):
    if not (a.get("mst") or a.get("id")):
        return "[입력 오류] mst(법령일련번호)가 필요합니다 — search_law 로 먼저 MST 를 얻으세요."
    p = {"OC": get_oc(a.get("law_oc")), "target": "lsStmd", "type": "JSON",
         "MST": str(a.get("mst") or a.get("id"))}
    raw = http_get("lawService.do", p)
    if _looks_empty_detail(raw):
        return "[체계도 없음] 해당 법령의 체계도를 찾지 못했습니다(mst 확인)."
    try:
        data = http_get_json("lawService.do", p, raw)   # 파싱 캐시(재파싱 방지)
    except Exception:
        return fmt_detail("법령 체계도", raw)
    acc = []
    _collect_related_laws(data.get("법령체계도", data), acc, set())
    if not acc:
        return fmt_detail("법령 체계도", raw)
    lines = ["=== 법령 체계도 (관련 법령 + 시행령·시행규칙) ==="]
    for name, mst in acc:
        lines.append("  · %s  [MST=%s]" % (name, mst))
    lines.append('\n➡ 각 법령 조문 조회: get_law_article(mst="<MST>", jo="제N조")')
    return "\n".join(lines)


def tool_search_law_appendix(a):
    p = {"OC": get_oc(a.get("law_oc")), "target": "licbyl", "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("knd"):
        p["knd"] = str(a["knd"])      # 1별표 2서식 3별지 4별도 5부록
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    return fmt_search("별표·서식 목록(파일/PDF 링크 포함)", total, page, items, None)


# =============================================================================
# 국세청·기재부·관세청 세법해석(법령해석·질의회신)  (Phase 7)
#   expc(법제처)와 별개의 cgmExpc 계열 target(라이브 확인). 검색은 즉시 가능,
#   본문(질의요지·회답·이유)은 해당 API 활용신청 후 활성화(미신청 시 안내).
# =============================================================================
_CGM_TARGETS = {"nts": "ntsCgmExpc", "moef": "moefCgmExpc", "customs": "kcsCgmExpc"}
_CGM_LABEL = {"nts": "국세청", "moef": "기획재정부", "customs": "관세청"}
# 본문(lawService) 미제공 기관 — 공식 가이드 표·라이브 확인(국세청·기재부는 목록만,
# 관세청은 본문 제공). 활용신청과 무관하게 본문 서비스 자체가 없음.
_CGM_NO_BODY = {"nts", "moef"}


# -----------------------------------------------------------------------------
# 국세법령정보시스템(taxlaw.nts.go.kr) 본문 폴백
#   법제처 OPEN API 가 국세청·기재부 세법해석의 '본문'을 주지 않으므로, 검색결과의
#   법령해석상세링크에 들어 있는 ntstDcmId 로 국세법령정보시스템에 직접 질의한다.
#   ⚠️ 공식 OPEN API 가 아니라 공개 웹페이지의 내부 호출이다 — 사이트 개편 시 깨질 수
#      있고, 결과에는 항상 출처를 명시한다. LAW_TAXLAW_FALLBACK=0 으로 끌 수 있다.
#   구현 메모(실측 2026-08-01): 세션·쿠키·로그인이 전혀 필요 없고 POST 1회면 끝난다.
#   단 Referer 를 taxlaw.nts.go.kr 이외의 호스트로 주면 404 페이지로 차단되므로,
#   법제처용 HEADERS(Referer=law.go.kr)를 그대로 재사용해서는 안 된다.
# -----------------------------------------------------------------------------
TAXLAW_HOST = "https://taxlaw.nts.go.kr"
TAXLAW_ACTION = TAXLAW_HOST + "/action.do"
TAXLAW_DETAIL = TAXLAW_HOST + "/qt/USEQTA002P.do?ntstDcmId=%s"
TAXLAW_ACTION_ID = "ASIQTB002PR01"
TAXLAW_ENABLED = os.environ.get("LAW_TAXLAW_FALLBACK", "1").strip().lower() not in ("0", "false", "no")
TAXLAW_TIMEOUT = int(os.environ.get("LAW_TAXLAW_TIMEOUT", "20"))
# 응답에 관련조문 목록(trilPsagList)이 딸려와 2MB 안팎이다 — 폭주 방지 상한.
TAXLAW_MAX_BYTES = int(os.environ.get("LAW_TAXLAW_MAX_BYTES", str(12 * 1024 * 1024)))
TAXLAW_MIN_INTERVAL = float(os.environ.get("LAW_TAXLAW_MIN_INTERVAL", "0.4"))  # 연속 호출 예의
_NTST_RE = re.compile(r"ntstDcmId=(\d{10,20})")
_NTST_ID_RE = re.compile(r"^\d{18}$")
_taxlaw_gate = threading.Lock()
_taxlaw_last = [0.0]


def ntst_id_from(text):
    """법령해석상세링크(또는 그 링크를 포함한 아무 텍스트)에서 ntstDcmId 를 뽑는다."""
    m = _NTST_RE.search(text or "")
    return m.group(1) if m else ""


_ZW_RE = re.compile("[​‌‍⁠﻿]")   # 폭 없는 빈칸·BOM — 국세법령정보시스템 글에 섞여 온다


def _one_line(s):
    """제목·문서번호 — 폭 없는 빈칸을 빼고 줄바꿈을 한 칸으로(제목 끝에 '\\r\\n\\r\\n\\u200b' 가 붙어 온다 — 실측)."""
    return re.sub(r"\s+", " ", _ZW_RE.sub("", str(s or ""))).strip()


# 국세법령정보시스템 본문 HTML → 평문 (2026-10-13 새로 짬 — 클린룸 점검 C2).
#  줄을 바꿀 요소는 실측으로 정했다: 해석 문서 14건(질의회신 4 · 사전답변 4 · 세법해석정비 2 · 표본 4 — 035694 ·
#  149597 · 504966 · 078704)의 본문 · 요지 · 회신 HTML 에 실제로 나온 끝 태그는 span 1507 · p 913 · td 130 · a 129 ·
#  tr 30 · div 6 · table 6 · tbody 6 · sup 2 였다(br 은 0). 그래서 문단(p) · 표 행(tr) · 구역(div) · 표(table)가 끝나면
#  줄을 바꾸고, 표 칸(td · th)이 끝나면 탭을 둔다. br 은 표본에 없지만 HTML 의 줄바꿈이라 따른다.
#  script · style 은 내용째 버린다. 엔티티는 표준 라이브러리 HTML 파서가 풀어 준다.
_NTS_NEWLINE_AFTER = frozenset(("p", "tr", "div", "table"))      # 실측 빈도 차례
_NTS_TAB_AFTER = frozenset(("td", "th"))
_NTS_HIDDEN = frozenset(("script", "style"))


class _NtsTextParser(html.parser.HTMLParser):
    """태그 사건을 받아 평문 조각을 모은다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in _NTS_HIDDEN:
            self.hidden += 1
        elif tag == "br" and not self.hidden:
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in _NTS_HIDDEN:
            self.hidden = max(0, self.hidden - 1)
        elif not self.hidden:
            if tag in _NTS_TAB_AFTER:
                self.chunks.append("\t")
            elif tag in _NTS_NEWLINE_AFTER:
                self.chunks.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.chunks.append(data)


def html_to_text(raw):
    """국세법령정보시스템 본문 HTML -> 평문. 표는 칸 사이 탭 · 행 끝 줄바꿈으로 남긴다."""
    reader = _NtsTextParser()
    reader.feed(raw or "")
    reader.close()
    text = _ZW_RE.sub("", "".join(reader.chunks))
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    rows = [re.sub(" {2,}", " ", row).rstrip(" \t") for row in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(rows)).strip()


# -----------------------------------------------------------------------------
# HTTPS 인증서 — Windows 루트 인증서 '필요할 때 내려받기'와 맞물린 실패 대응
#   (2026-10-13 PC3 실측, taxlaw_mcp_server.py v2.0.1 과 같은 코드)
#   국세법령정보시스템은 Sectigo Public Server Authentication Root R46 으로 끝나는 사슬을
#   보낸다. 새로 설치한 Windows 에는 이 루트가 없고, Windows 는 Edge·PowerShell 같은
#   CryptoAPI 프로그램이 처음 필요로 할 때에야 받아 넣는다. 파이썬(OpenSSL)은 그 내려받기를
#   일으키지 못해 'self-signed certificate in certificate chain' 으로 실패한다. 게다가
#   urllib 기본 오프너는 첫 호출 때 만든 인증서 목록을 프로세스가 끝날 때까지 다시 써서,
#   루트가 들어온 뒤에도 앱을 다시 켤 때까지 계속 실패했다.
#   → 검증이 실패하면 ① CryptoAPI 로 같은 인증서의 사슬을 한 번 만들게 해 Windows 가 빠진
#     루트를 받아 오게 하고 ② 저장소를 다시 읽은 새 컨텍스트로 1회 재시도한다.
#     검증을 끄는 일은 없다. (법제처 http_get 은 호출마다 새 컨텍스트 + HTTP 폴백이라 해당 없음)
# -----------------------------------------------------------------------------
_tls_lock = threading.Lock()          # 컨텍스트 교체
_tls_repair_lock = threading.Lock()   # 동시 실패 시 복구는 한 스레드만
_tls_ctx = [None]


class TLSVerifyError(Exception):
    """인증서 검증이 복구 후에도 실패 — 같은 호출을 되풀이해도 같으므로 바로 사유를 보고한다."""


def _new_tls_context():
    return ssl.create_default_context()   # Windows 인증서 저장소를 이때 읽는다


def _tls_context(refresh=False):
    with _tls_lock:
        if refresh or _tls_ctx[0] is None:
            _tls_ctx[0] = _new_tls_context()
        return _tls_ctx[0]


def _is_cert_error(e):
    return isinstance(e, ssl.SSLCertVerificationError) or \
        isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError)


def _peer_cert_der(host, port=443):
    """검증 없이 핸드셰이크만 해서 상대 인증서(DER)를 받는다 — 진단·루트 갱신용(요청은 보내지 않음)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=TAXLAW_TIMEOUT) as s:
        with ctx.wrap_socket(s, server_hostname=host) as t:
            return t.getpeercert(binary_form=True)


def _cert_issuer(der):
    """DER 인증서의 발급자 이름(진단용). 못 읽으면 '?'."""
    try:
        fd, path = tempfile.mkstemp(suffix=".pem")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(ssl.DER_cert_to_PEM_cert(der))
            info = ssl._ssl._test_decode_cert(path)
        finally:
            os.remove(path)
        return ", ".join("%s=%s" % kv for rdn in info.get("issuer", ()) for kv in rdn) or "?"
    except Exception:
        return "?"


def _windows_build_chain(der):
    """Windows CryptoAPI 로 이 인증서의 사슬을 만든다. 이 과정에서 Windows 가 빠진 중간·루트
    인증서를 받아 온다(AIA·자동 루트 갱신). -> 사슬 오류 비트(0 = 정상) / None(Windows 아님·실패)."""
    if os.name != "nt" or not der:
        return None
    try:
        import ctypes
        from ctypes import wintypes as wt

        class CTL_USAGE(ctypes.Structure):
            _fields_ = [("cUsageIdentifier", wt.DWORD),
                        ("rgpszUsageIdentifier", ctypes.POINTER(ctypes.c_char_p))]

        class CERT_USAGE_MATCH(ctypes.Structure):
            _fields_ = [("dwType", wt.DWORD), ("Usage", CTL_USAGE)]

        class CERT_CHAIN_PARA(ctypes.Structure):
            _fields_ = [("cbSize", wt.DWORD), ("RequestedUsage", CERT_USAGE_MATCH)]

        class CERT_CHAIN_HEAD(ctypes.Structure):     # CERT_CHAIN_CONTEXT 의 앞부분(cbSize·TrustStatus)
            _fields_ = [("cbSize", wt.DWORD), ("dwErrorStatus", wt.DWORD), ("dwInfoStatus", wt.DWORD)]

        c32 = ctypes.WinDLL("crypt32")
        c32.CertCreateCertificateContext.restype = ctypes.c_void_p
        c32.CertCreateCertificateContext.argtypes = [wt.DWORD, ctypes.c_char_p, wt.DWORD]
        c32.CertGetCertificateChain.restype = wt.BOOL
        c32.CertGetCertificateChain.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(CERT_CHAIN_PARA), wt.DWORD, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
        c32.CertFreeCertificateChain.argtypes = [ctypes.c_void_p]
        c32.CertFreeCertificateContext.argtypes = [ctypes.c_void_p]

        cert = c32.CertCreateCertificateContext(0x00010001, der, len(der))   # X509_ASN | PKCS_7_ASN
        if not cert:
            return None
        try:
            oids = (ctypes.c_char_p * 1)(b"1.3.6.1.5.5.7.3.1")               # 서버 인증 용도
            para = CERT_CHAIN_PARA()
            para.cbSize = ctypes.sizeof(CERT_CHAIN_PARA)
            para.RequestedUsage.dwType = 0                                       # USAGE_MATCH_TYPE_AND
            para.RequestedUsage.Usage.cUsageIdentifier = 1
            para.RequestedUsage.Usage.rgpszUsageIdentifier = ctypes.cast(oids, ctypes.POINTER(ctypes.c_char_p))
            chain = ctypes.c_void_p()
            if not c32.CertGetCertificateChain(None, cert, None, None, ctypes.byref(para), 0, None,
                                               ctypes.byref(chain)):
                return None
            try:
                return ctypes.cast(chain, ctypes.POINTER(CERT_CHAIN_HEAD)).contents.dwErrorStatus
            finally:
                c32.CertFreeCertificateChain(chain)
        finally:
            c32.CertFreeCertificateContext(cert)
    except Exception as e:
        LOG.warning("Windows 인증서 사슬 확인 실패: %s", e)
        return None


def urlopen_tls(req, timeout):
    """urllib.request.urlopen 대신. 인증서 검증이 실패하면 Windows 가 루트를 받아 오게 한 뒤
    저장소를 다시 읽은 컨텍스트로 1회 재시도한다. 그래도 실패하면 TLSVerifyError(사유 포함)."""
    ctx = _tls_context()
    try:
        return urllib.request.urlopen(req, timeout=timeout, context=ctx)
    except Exception as e:
        if not _is_cert_error(e):
            raise
        LOG.warning("HTTPS 인증서 검증 실패 — 복구 시도: %s", getattr(e, "reason", e))
    u = urllib.parse.urlsplit(req.full_url)
    host, port = u.hostname, u.port or 443
    der, status, repaired = None, None, False
    with _tls_repair_lock:
        if _tls_ctx[0] is ctx:                 # 다른 스레드가 이미 고쳤으면 다시 하지 않는다
            try:
                der = _peer_cert_der(host, port)
            except Exception as e:
                LOG.warning("인증서 확인용 접속 실패: %s", e)
            status = _windows_build_chain(der)
            _tls_context(refresh=True)
            repaired = True
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=_tls_context())
    except Exception as e:
        if not _is_cert_error(e):
            raise
        if der is None:
            try:
                der = _peer_cert_der(host, port)
            except Exception:
                pass
        why = getattr(getattr(e, "reason", e), "verify_message", "") or str(e)
        raise TLSVerifyError(
            "HTTPS 인증서 검증 실패: %s · 받은 인증서 발급자: %s · Windows 사슬 확인: %s. "
            "Windows 가 이 사이트의 루트 인증서를 받지 못했거나(자동 루트 갱신 차단) 보안 "
            "프로그램이 접속을 가로채는 경우입니다. Edge 로 https://%s 를 한 번 연 뒤 다시 시도하세요."
            % (why, _cert_issuer(der) if der else "?",
               "확인 못 함" if status is None else ("정상" if status == 0 else "오류 0x%X" % status), host))
    if repaired:
        LOG.warning("HTTPS 인증서: Windows 사슬 확인(%s) 후 저장소를 다시 읽어 통과",
                    "확인 못 함" if status is None else "0x%X" % status)
    return resp


def taxlaw_fetch(ntst):
    """ntstDcmId -> (문서 노드 dict 또는 None, 실패 사유). 예외를 밖으로 던지지 않는다."""
    body = urllib.parse.urlencode({
        "actionId": TAXLAW_ACTION_ID,
        "paramData": json.dumps({"dcmDVO": {"ntstDcmId": ntst}}, ensure_ascii=False),
    }, encoding="utf-8").encode("utf-8")
    req = urllib.request.Request(TAXLAW_ACTION, data=body, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": UA,
        "Origin": TAXLAW_HOST,
        "Referer": TAXLAW_DETAIL % ntst,     # ★타 호스트 Referer 는 차단 트리거
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
        "Connection": "close",
    })
    with _taxlaw_gate:                        # 공개 웹페이지이므로 연속 호출 간격을 둔다
        gap = TAXLAW_MIN_INTERVAL - (time.monotonic() - _taxlaw_last[0])
        if gap > 0:
            time.sleep(gap)
        _taxlaw_last[0] = time.monotonic()
    why = "네트워크·차단"
    for attempt in range(2):                  # 재시도는 1회까지만(공식 API 가 아님)
        try:
            with urlopen_tls(req, TAXLAW_TIMEOUT) as resp:
                raw = resp.read(TAXLAW_MAX_BYTES + 1)
            if len(raw) > TAXLAW_MAX_BYTES:
                LOG.warning("taxlaw 응답 과대(%d bytes) — 중단", len(raw))
                return None, "응답 과대"
            data = json.loads(raw.decode("utf-8", "replace"))
            node = (data.get("data") or {}).get(TAXLAW_ACTION_ID)
            return (node, "") if isinstance(node, dict) else (None, "응답에 문서 정보 없음")
        except TLSVerifyError as e:               # 되풀이해도 같다 — 사유를 그대로 보고
            LOG.warning("taxlaw 실패 %s: %s", ntst, e)
            return None, str(e)
        except Exception as e:
            LOG.warning("taxlaw 실패(%d) %s: %s", attempt, ntst, e)
            why = "네트워크·차단 — %s" % str(getattr(e, "reason", None) or e)[:160]
            if attempt == 0:
                time.sleep(1.0)
    return None, why


# 국세청 · 기재부 해석 문서 노드 다루기 (2026-10-13 새로 짬 — 클린룸 점검 C3). 근거는 실측(해석 문서 14건):
#  · '없는 문서' 문턱 — 없는 ID(010000000000000000)와 세법해석정비 문서 2건은 요지 · 회신 · 본문의 낱자 · 숫자가 0,
#    해석 문서 12건 가운데 가장 짧은 것도 466자였다 → 10자 밑이면 없는 문서(ID 오류 · 비공개)로 본다.
#  · 문서번호 — 12건(질의회신 · 사전답변 · 서면 · 기재부) 모두 ntstDcmDscmCntn 칸에 있었고 다른 번호 칸은 비어 있어 이 칸만 쓴다.
_NTS_MIN_LETTERS = 10


def _nts_sections(node):
    """문서 노드 → (dcmDVO, [(구획, 평문) …]) — 요지 · 회신 · 본문 차례, 글이 없는 구획은 뺀다.
    본문은 편집기 조각(dcmHwpEditorDVOList) 가운데 가장 긴 것이다(첫 조각이 빈 문서가 있다)."""
    dcm = node.get("dcmDVO") or {}
    pieces = [(e or {}).get("dcmFleByte") or "" for e in (node.get("dcmHwpEditorDVOList") or [])]
    named = (("요지", dcm.get("ntstDcmGistCntn")), ("회신", dcm.get("ntstDcmCntn")),
             ("본문", max(pieces, key=len, default="")))
    return dcm, [(name, txt) for name, txt in ((n, html_to_text(h or "")) for n, h in named) if txt]


def _nts_letters(sections):
    return sum(ch.isalnum() for _, txt in sections for ch in txt)


def _nts_day(v):
    """생산일자 — 8자리 숫자면 YYYY.MM.DD, 아니면 받은 그대로."""
    v = str(v or "").strip()
    return "%s.%s.%s" % (v[:4], v[4:6], v[6:]) if len(v) == 8 and v.isdigit() else v


# 판례 · 결정례의 결과 구분 = 국세법령정보시스템 공통코드 19375 「국세법령문서결정구분코드」(ACMCMA001MR01 · 2026-10-26 실측).
#  검색 줄에는 이름 칸(NTST_DCM_DCS_CL_NM — 예 '국승')이 함께 오지만, 상세(dcmDVO)에는 코드(ntstDcmDcsClCd)만 온다.
#  ZZ(해당없음 — 해석 문서)는 내지 않는다.
_NTS_DCS = {"01": "각하", "02": "채택", "03": "불채택", "04": "일부채택", "05": "기각", "06": "경정", "07": "인용",
            "08": "일부인용", "09": "재조사", "10": "국승", "11": "국패", "12": "일부국패", "13": "일부국승",
            "14": "합헌", "15": "위헌", "16": "헌법불합치", "19": "수범", "20": "지적", "22": "유죄",
            "23": "일부유죄", "24": "무죄", "99": "기타"}


def _nts_outcome(code=None, name=None):
    """결과 구분 이름 — 이름 칸이 있으면 그것, 없으면 코드표로. 해당없음 · 빈 값은 ''."""
    n = _one_line(name)
    if n and n != "해당없음":
        return n
    return _NTS_DCS.get(str(code or "").strip(), "")


def _nts_kind(docno):
    """문서번호 꼴로 판례 · 결정례의 갈래를 고른다(해석 문서는 None). 실측 꼴(10-26): 조심-2019-서-4288 · 이의-대전청-2025-0062 ·
    서울청이의2005-0341 · 심사-부가-2024-0040 · 심사양도1999-… · 적부-국세청-2020-0093 · 대법원-2022-두-42020 · 서울행정법원-…"""
    d = _one_line(docno)
    if d.startswith(("조심", "국심")):
        return "조세심판"
    if d.startswith("이의") or "청이의" in d[:6]:
        return "이의신청"
    if d.startswith("심사"):
        return "심사청구"
    if d.startswith("적부"):
        return "과세전적부심사"
    if d.startswith("헌재") or "헌법재판소" in d[:8]:
        return "헌재 결정"
    if "법원" in d.split("-")[0]:
        return "판례"
    return None


_HEAD_MARK = re.compile(r"^(?:\(?\d{1,2}\)|\d{1,2}\.|\(?[가-하][.)]|[①-⑳]|[【\[〔])")


def _find_head(body, word):
    """찾을 말의 '머리 줄' 시작 자리 — ① 번호를 뗀 줄 글이 찾을 말과 꼭 같은 줄('라. 판단' · '(2) 판단' · '【판단】')
    ② 찾을 말이 든 짧은 줄('4. 심리 및 판단') ③ 글 속 첫 자리 차례로 보고, 없으면 -1.
    실측(적부-국세청-2020-0093): 「판단」 은 2,728자째 글 속 · 6,307자째 「4. 심리 및 판단」(쟁점 · 관련법령 · 사실관계를
    아우르는 큰 머리) · 36,793자째 「라. 판단」 에 있다 — 찾는 사람이 바라는 것은 「라. 판단」 이라 ① 을 먼저 본다."""
    w = re.sub(r"\s+", "", str(word or ""))
    if not w:
        return -1
    near = -1
    pos = 0
    for line in body.splitlines(True):
        bare = re.sub(r"\s+", "", line)
        if w in bare and len(bare) <= len(w) + 14:
            if _HEAD_MARK.sub("", bare).rstrip("】]〕:：") == w:
                return pos
            if near < 0:
                near = pos
        pos += len(line)
    return near if near >= 0 else body.find(str(word).strip())


def _nts_slice(body, budget, offset=0, find=None, more=None):
    """긴 본문을 잘라 버리지 않는다 — 이 쪽 조각 + 이어 볼 자리(글자 위치) 안내. more(끝 자리) → 다음 부를 꼴."""
    total = len(body)
    start, lead = 0, ""
    if find:
        i = _find_head(body, find)
        if i >= 0:
            start = body.rfind("\n", 0, i) + 1                 # 그 줄 머리부터
            lead = "(「%s」 줄부터 — 본문 %d자 가운데 %d자째)\n" % (find, total, start)
        else:
            lead = "(본문에 「%s」 가 없어 처음부터 — offset 으로 넘기세요)\n" % find
    elif offset:
        start = max(0, min(int(offset), total))
        lead = "(본문 %d자 가운데 %d자째부터)\n" % (total, start)
    budget = max(1000, budget)
    end = min(total, start + budget)
    if end < total:                                            # 줄 끝에서 끊어 다음 쪽이 줄 머리에서 열리게
        nl = body.rfind("\n", start + budget // 2, end)
        if nl > start:
            end = nl + 1
    tail = ""
    if end < total:
        tail = "\n\n…(이어짐 — 본문 %d자 가운데 %d~%d자. 다음 쪽: %s)" % (total, start, end, more(end) if more else "offset=%d" % end)
    elif start > 0:
        tail = "\n\n(본문 끝 — %d자)" % total
    return lead + body[start:end] + tail


def taxlaw_format(node, ntst, label, offset=0, find=None):
    """문서 노드 -> 사람이 읽는 전문 텍스트. 글이 거의 없으면(없는 ID · 비공개) None.
    v2.13.0 — 판례 · 결정례(법원 · 조심 · 이의 · 심사 · 적부)는 갈래와 결과 구분(국승 · 기각 …)을 머리에 적는다.
    긴 본문은 잘라 버리지 않고 offset(글자 위치) · find(머리 줄 — 예 '판단')로 이어 보게 한다(세무자문 좌석 10-25 요청)."""
    dcm, sections = _nts_sections(node)
    if _nts_letters(sections) < _NTS_MIN_LETTERS:
        return None
    docno, day = _one_line(dcm.get("ntstDcmDscmCntn")), _nts_day(dcm.get("ntstDcmRgtDt"))
    kind = _nts_kind(docno)
    if kind:   # 판결 · 결정의 '회신' 칸은 「판결 내용은 붙임과 같습니다.」 같은 한 줄뿐이라 뺀다(실측)
        sections = [(n, t) for n, t in sections if not (n == "회신" and len(t) < 40 and ("붙임" in t or "상세내용" in t))]
        head = ["【국세법령정보시스템 %s 전문】 %s" % (kind, _one_line(dcm.get("ntstDcmTtl")) or ntst)]
    else:
        head = ["【%s 세법해석 전문】 %s" % (label, _one_line(dcm.get("ntstDcmTtl")) or ntst)]
    head += ["문서번호: " + docno] if docno else []
    head += ["생산일자: " + day] if day else []
    result = _nts_outcome(dcm.get("ntstDcmDcsClCd")) if kind else ""
    head += ["결과: " + result] if result else []
    head += ["출처: 국세법령정보시스템 %s" % (TAXLAW_DETAIL % ntst),
             "⚠️ 법제처 OPEN API 가 아닌 국세법령정보시스템 공개 페이지에서 가져온 본문입니다. "
             "인용 전 원문 링크로 대조하세요."]
    top = "\n".join(head) + "\n"
    body = "\n".join("\n■ %s\n%s" % sec for sec in sections)
    return top + _nts_slice(body, MAX_TEXT - len(top) - 250, offset, find,
                            lambda end: 'get_tax_interpretation(id="%s", offset=%d) · 판단 부분은 find="판단"' % (ntst, end))


def tool_search_tax_interpretation(a):
    src = (a.get("source") or "nts").lower()
    target = _CGM_TARGETS.get(src, "ntsCgmExpc")
    p = {"OC": get_oc(a.get("law_oc")), "target": target, "type": "XML",
         "display": clamp_display(a.get("display")), "page": str(a.get("page", 1))}
    if a.get("query"):
        p["query"] = a["query"]
    if a.get("search"):
        p["search"] = str(a["search"])
    if a.get("explYd"):
        p["explYd"] = a["explYd"]      # 해석일자 범위 YYYYMMDD~YYYYMMDD
    if a.get("sort"):
        p["sort"] = a["sort"]
    total, page, items = parse_search(http_get("lawSearch.do", p))
    text = fmt_search("%s 세법해석례 검색결과" % _CGM_LABEL.get(src, src),
                      total, page, items, "get_tax_interpretation")
    if src in _CGM_NO_BODY and items:
        # 국세청·기재부는 법제처 일련번호로 본문을 못 받는다. 전문은 상세링크 안의
        # ntstDcmId 로만 받을 수 있으므로, 힌트를 그 ID 로 바꿔 준다(모델이 그대로 따라 함).
        ntst = ntst_id_from(items[0].get("법령해석상세링크", ""))
        if ntst and TAXLAW_ENABLED:
            text = re.sub(r'➡ 전문 조회:.*',
                          '➡ 전문 조회:  get_tax_interpretation(id="%s", source="%s")\n'
                          '   (국세청·기재부는 법제처 일련번호가 아니라 위 상세링크의 '
                          'ntstDcmId 를 id 로 넘겨야 전문이 옵니다.)' % (ntst, src), text)
    return text


def _taxlaw_doc(ntst):
    """문서 노드를 본문 조각 하나만 남긴 가벼운 꼴로 1시간 기억한다 — 긴 판결을 쪽으로 넘길 때마다
    2MB 안팎의 응답(관련조문 목록 포함)을 다시 받지 않게(v2.13.0)."""
    key = "taxlawdoc|" + ntst
    hit = _cache_get(key)
    if hit is not None:
        return json.loads(hit), ""
    node, why = taxlaw_fetch(ntst)
    if node is None:
        return None, why
    pieces = [(e or {}).get("dcmFleByte") or "" for e in (node.get("dcmHwpEditorDVOList") or [])]
    slim = {"dcmDVO": node.get("dcmDVO") or {},
            "dcmHwpEditorDVOList": [{"dcmFleByte": max(pieces, key=len, default="")}]}
    _cache_put(key, json.dumps(slim, ensure_ascii=False))
    return slim, ""


def _int_arg(v, default=0):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return default


def tool_get_tax_interpretation(a):
    src = (a.get("source") or "nts").lower()
    target = _CGM_TARGETS.get(src, "ntsCgmExpc")
    label = _CGM_LABEL.get(src, src)
    idv = str(a.get("id") or "").strip()
    # 국세법령정보시스템 문서ID(18자리)를 받으면 기관과 무관하게 그쪽 본문을 우선한다(판례 · 결정례 문서ID 도 같은 길).
    if TAXLAW_ENABLED and _NTST_ID_RE.match(idv):
        node, why = _taxlaw_doc(idv)
        if node is not None:
            body = taxlaw_format(node, idv, label, offset=_int_arg(a.get("offset")),
                                 find=str(a.get("find") or "").strip() or None)
            if body:
                return body
            return ("[문서 없음] 국세법령정보시스템에 문서ID %s 의 본문이 없습니다"
                    "(ID 오타이거나 비공개 문서).\n"
                    "→ search_tax_interpretation 결과의 '법령해석상세링크' 에 있는 "
                    "ntstDcmId 를 그대로 사용했는지 확인하세요." % idv)
        return ("[본문 조회 실패] 국세법령정보시스템(taxlaw.nts.go.kr)에 연결하지 못했습니다.\n"
                "→ 사유: %s\n"
                "→ 원문: %s\n"
                "→ 인용은 검색결과의 안건명·안건번호·해석일자로도 충분합니다."
                % (why, TAXLAW_DETAIL % idv))
    if src in _CGM_NO_BODY:
        hint = ("→ 전문을 보려면 search_tax_interpretation 결과의 '법령해석상세링크' 에 있는 "
                "ntstDcmId(18자리)를 id 로 넘기세요 — 국세법령정보시스템 본문이 반환됩니다.\n"
                if TAXLAW_ENABLED else
                "→ 전문은 검색결과의 '법령해석상세링크'(국세법령정보시스템)에서 직접 확인하세요.\n")
        return ("[본문 미제공] %s 세법해석은 법제처 OPEN API 가 '목록'만 제공하고 '본문'은 "
                "제공하지 않습니다(공식 가이드 기준 — 세법해석 중 본문은 관세청만 제공).\n"
                "%s"
                "→ 인용은 검색결과의 안건명·안건번호·해석일자로 충분합니다. 같은 ID 재호출 불필요."
                % (label, hint))
    p = {"OC": get_oc(a.get("law_oc")), "target": target, "type": "JSON", "ID": idv}
    return _detail("%s 세법해석례 전문" % label, "세법해석례", idv,
                   http_get("lawService.do", p))


# =============================================================================
# v2.9 업그레이드 (2026-10) — PC5 본부 기능정의서 v1 · 착상 참고: chrisryugj/korean-law-mcp (MIT)
#   코드는 정의서와 법제처 공식 안내만 보고 새로 짰다(클린룸 — 저쪽 코드 줄은 옮기지 않음).
#   F2 법령 이름 풀기(세법 약칭 사전) · F4 별표·서식(긴 표 쪽 나눔·행 고르기)
#   · F1 인용 검증(글 통째로) · F3 행위시법 한 번에.
#   ★판 고르기 = eflaw 검색의 LID(법령ID) + efYd 범위 (실측 2026-10-13)
#     · 결과는 시행일 내림차순, 같은 시행일이면 공포일 내림차순 — 첫 줄이 그날 시행 판이다
#       (조특법 @2024-01-01 → MST 257993 · 제19936호, 그 뒤 27 · 시행예정 9 = 견줌 값과 같음)
#     · LID 는 제명이 바뀌어도 이어진다(임대주택법 → 민간임대주택에 관한 특별법 확인)
#     · query(이름) 검색은 '…법 시행령' 까지 섞이고 옛 이름 판을 놓친다 — 판 고르기에 쓰지 않는다
# =============================================================================
# ---- F2 법령 이름 풀기 ------------------------------------------------------
# (약칭, 정식 법령명, 출처)
#   국세청 = 국세청 『2026 주택과 세금』 일러두기 「법령 표기방식」(인쇄 3쪽)
#   정의서 = PC5 본부 기능정의서 v1 §3 첫 판 목록 · 볼트 = 볼트 R 노트 공통 약칭표(R노트공통.py)
#   관용 = 세무 실무에서 흔히 쓰는 꼴(옛 verify_citation 약칭표 포함)
#   ※ 뜻이 둘인 말(부령=部令 · 법령 · 부칙=附則)은 넣지 않는다.
#   ※ 사람이 더할 것은 이 파일 옆 law_alias.json([{"약칭":…, "정식명":…, "출처":…}])에 — 코드보다 먼저 읽힌다.
_ALIAS_ROWS = (
    ("지방법", "지방세법", "국세청"), ("지방령", "지방세법 시행령", "국세청"),
    ("지특법", "지방세특례제한법", "국세청"),
    ("종부법", "종합부동산세법", "국세청"), ("종부령", "종합부동산세법 시행령", "국세청"),
    ("소득법", "소득세법", "국세청"), ("소득령", "소득세법 시행령", "국세청"),
    ("조특법", "조세특례제한법", "국세청"), ("조특령", "조세특례제한법 시행령", "국세청"),
    ("상증법", "상속세 및 증여세법", "국세청"), ("상증령", "상속세 및 증여세법 시행령", "국세청"),
    ("부동산거래신고법", "부동산 거래신고 등에 관한 법률", "국세청"),
    ("부동산거래신고령", "부동산 거래신고 등에 관한 법률 시행령", "국세청"),
    ("지방칙", "지방세법 시행규칙", "정의서"),
    ("지특령", "지방세특례제한법 시행령", "정의서"), ("지특칙", "지방세특례제한법 시행규칙", "정의서"),
    ("종부칙", "종합부동산세법 시행규칙", "정의서"),
    ("소법", "소득세법", "정의서"), ("소득칙", "소득세법 시행규칙", "정의서"),
    ("조특칙", "조세특례제한법 시행규칙", "정의서"), ("상증칙", "상속세 및 증여세법 시행규칙", "정의서"),
    ("법인법", "법인세법", "정의서"), ("법법", "법인세법", "정의서"),
    ("법인령", "법인세법 시행령", "정의서"), ("법인칙", "법인세법 시행규칙", "정의서"),
    ("부가법", "부가가치세법", "정의서"), ("부가령", "부가가치세법 시행령", "정의서"),
    ("부가칙", "부가가치세법 시행규칙", "정의서"),
    ("국기법", "국세기본법", "정의서"), ("국기령", "국세기본법 시행령", "정의서"),
    ("국기칙", "국세기본법 시행규칙", "정의서"),
    ("국징법", "국세징수법", "정의서"), ("국징령", "국세징수법 시행령", "정의서"),
    ("국징칙", "국세징수법 시행규칙", "정의서"),
    ("지기법", "지방세기본법", "정의서"), ("지기령", "지방세기본법 시행령", "정의서"),
    ("지기칙", "지방세기본법 시행규칙", "정의서"),
    ("개소법", "개별소비세법", "정의서"), ("개소령", "개별소비세법 시행령", "정의서"),
    ("개소칙", "개별소비세법 시행규칙", "정의서"),
    ("농특세법", "농어촌특별세법", "정의서"), ("농특법", "농어촌특별세법", "관용"),
    ("농특령", "농어촌특별세법 시행령", "정의서"), ("농특칙", "농어촌특별세법 시행규칙", "정의서"),
    ("국조법", "국제조세조정에 관한 법률", "정의서"), ("국조령", "국제조세조정에 관한 법률 시행령", "정의서"),
    ("국조칙", "국제조세조정에 관한 법률 시행규칙", "정의서"),
    ("부동산거래신고칙", "부동산 거래신고 등에 관한 법률 시행규칙", "정의서"),
    ("민특법", "민간임대주택에 관한 특별법", "정의서"), ("민간임대주택법", "민간임대주택에 관한 특별법", "정의서"),
    ("민특령", "민간임대주택에 관한 특별법 시행령", "정의서"),
    ("민특칙", "민간임대주택에 관한 특별법 시행규칙", "정의서"),
    ("도정법", "도시 및 주거환경정비법", "정의서"), ("도정령", "도시 및 주거환경정비법 시행령", "정의서"),
    ("도정칙", "도시 및 주거환경정비법 시행규칙", "정의서"),
    ("소규모주택정비법", "빈집 및 소규모주택 정비에 관한 특례법", "정의서"),
    ("공익법인법", "공익법인의 설립ㆍ운영에 관한 법률", "정의서"),
    ("외감법", "주식회사 등의 외부감사에 관한 법률", "정의서"),
    ("외감령", "주식회사 등의 외부감사에 관한 법률 시행령", "정의서"),
    ("자본시장법", "자본시장과 금융투자업에 관한 법률", "정의서"),
    ("상증세법", "상속세 및 증여세법", "볼트"), ("상증규칙", "상속세 및 증여세법 시행규칙", "볼트"),
    ("법칙", "법인세법 시행규칙", "볼트"), ("법규칙", "법인세법 시행규칙", "볼트"),
    ("부법", "부가가치세법", "볼트"),
    ("종부세법", "종합부동산세법", "볼트"), ("종부세령", "종합부동산세법 시행령", "볼트"),
    ("부동산거래법", "부동산 거래신고 등에 관한 법률", "볼트"),
    ("민간임대주택특별법", "민간임대주택에 관한 특별법", "볼트"),
    ("공공주택법", "공공주택 특별법", "볼트"), ("공공주택특별법", "공공주택 특별법", "볼트"),
    ("국토계획법", "국토의 계획 및 이용에 관한 법률", "볼트"),
    ("국민기초생활보장법", "국민기초생활 보장법", "볼트"),
    ("소세법", "소득세법", "관용"), ("법세법", "법인세법", "관용"), ("부가세법", "부가가치세법", "관용"),
    ("조특규칙", "조세특례제한법 시행규칙", "관용"), ("소득규칙", "소득세법 시행규칙", "관용"),
    # 법제처 정식명은 「대한민국헌법」 — 「헌법」 은 이름 검색에서 정확히 맞는 줄이 없어(헌법재판소 규칙들이 앞에 옴 · 10-13 실측)
    # 인용 검증 · 행위시법에서 못 찾았다. 조세법률주의(제38조 · 제59조) 인용이 잦아 넣는다(PC5 본부 10-13 회신의 곁 제보).
    ("헌법", "대한민국헌법", "관용"),
)
_DOTS = "·･‧・•"        # 법제처 법령명의 가운뎃점은 'ㆍ'(U+318D) 하나로 쓴다


def _clean_law_name(raw):
    """법령 이름 정리 — 낫표·따옴표를 벗기고 가운뎃점을 'ㆍ' 로, 빈칸을 하나로."""
    s = str(raw or "").strip().strip("「」『』\"'“”‘’ ")
    s = re.sub("[%s]" % _DOTS, "ㆍ", s)
    return re.sub(r"\s+", " ", s).strip()


def _name_key(s):
    """비교 열쇠 — 빈칸·가운뎃점 꼴을 무시(「상속세및증여세법」 = 「상속세 및 증여세법」)."""
    return re.sub(r"[\sㆍ%s]" % _DOTS, "", str(s or ""))


def _load_alias_file():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "law_alias.json")
    rows = []
    if not os.path.exists(path):
        return rows
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
        for r in (data if isinstance(data, list) else data.get("약칭") or []):
            if isinstance(r, dict) and r.get("약칭") and r.get("정식명"):
                rows.append((str(r["약칭"]).strip(), _clean_law_name(r["정식명"]),
                             str(r.get("출처") or "law_alias.json")))
    except Exception as e:
        LOG.warning("law_alias.json 을 읽지 못함(무시): %s", e)
    return rows


_ALIAS = {}       # 비교 열쇠(약칭) -> (정식명, 출처)
_ALIAS_OF = {}    # 비교 열쇠(정식명) -> [약칭…] — search_law 결과에 함께 보임
for _a, _full, _src in tuple(_load_alias_file()) + _ALIAS_ROWS:   # 파일이 먼저(사람이 고친 것 우선)
    _ALIAS.setdefault(_name_key(_a), (_full, _src))
    if _a not in _ALIAS_OF.setdefault(_name_key(_full), []):
        _ALIAS_OF[_name_key(_full)].append(_a)
_KNOWN = {_name_key(v[0]): v[0] for v in _ALIAS.values()}          # 표에 오른 정식명
_KNOWN.update({_name_key(re.sub(r" 시행(령|규칙)$", "", v)): re.sub(r" 시행(령|규칙)$", "", v)
               for v in list(_KNOWN.values())})


def _alias_lookup(name):
    """약칭 → (정식명, 출처). '조특법 시행령' 처럼 뒤에 시행령·시행규칙이 붙은 꼴도 푼다."""
    hit = _ALIAS.get(_name_key(name))
    if hit:
        return hit
    m = re.fullmatch(r"(.+?)\s*(시행령|시행규칙)", name or "")
    if m:
        base = _ALIAS.get(_name_key(m.group(1)))
        if base and not re.search(r"시행(령|규칙)$", base[0]):
            return base[0] + " " + m.group(2), base[1]
    return "", ""


def resolve_law_name(raw):
    """법령 이름(네트워크 없이) → (찾을 이름, 머리 안내). 약칭이면 정식명으로 바꾸고 안내를 단다."""
    name = _clean_law_name(raw)
    if not name:
        return "", ""
    full, _ = _alias_lookup(name)
    if full and _name_key(full) != _name_key(name):
        return full, "'%s' → %s 으로 찾음" % (name, full)
    return name, ""


_LAW_MEMO = {}
_LAW_MEMO_LOCK = threading.Lock()


def _law_lookup(name, oc):
    """정식명(또는 옛 이름) → {name, id, state, mst, efyd, cur_name} / None.
    현행 목록(target=law)에서 이름이 정확히 같은 것 → 없으면 연혁(eflaw)에서. 결과는 프로세스 동안 기억."""
    name = _clean_law_name(name)
    k = _name_key(name)
    if not k:
        return None
    today = _today()
    with _LAW_MEMO_LOCK:
        hit = _LAW_MEMO.get(k)
        if hit and hit[0] == today:                 # 날이 바뀌면 다시(그날 현행·폐지 상태가 바뀔 수 있음)
            return hit[1]
    res = None
    p = {"OC": oc, "target": "law", "type": "XML", "display": "50", "query": name}
    _, _, items = parse_search(http_get("lawSearch.do", p))
    ex = [d for d in items if _name_key(pick(d, "법령명한글", "법령명")) == k]
    if ex:
        d = ex[0]
        res = {"name": pick(d, "법령명한글", "법령명"), "id": _num_id(d.get("법령ID")), "state": "현행",
               "mst": _num_id(d.get("법령일련번호")), "efyd": _num_id(d.get("시행일자")),
               "cur_name": pick(d, "법령명한글", "법령명")}
    else:
        p = {"OC": oc, "target": "eflaw", "type": "XML", "display": "100", "query": name}
        _, _, items = parse_search(http_get("lawSearch.do", p))
        ex = sorted((d for d in items if _name_key(pick(d, "법령명한글", "법령명")) == k),
                    key=_ver_sort_key, reverse=True)
        if ex:
            lid = _num_id(ex[0].get("법령ID"))
            res = {"name": pick(ex[0], "법령명한글", "법령명"), "id": lid, "state": "폐지",
                   "mst": "", "efyd": "", "cur_name": ""}
            _, rows = _ver_rows(lid, oc, to=_today(), display=5)
            if rows and (rows[0].get("현행연혁코드") or "") == "현행":
                res.update(state="이름바뀜", cur_name=pick(rows[0], "법령명한글", "법령명"),
                           mst=_num_id(rows[0].get("법령일련번호")), efyd=_num_id(rows[0].get("시행일자")))
    with _LAW_MEMO_LOCK:
        _LAW_MEMO[k] = (today, res)
    return res


def _find_law(raw, oc):
    """사용자가 준 법령 이름(약칭·붙여 쓴 이름 됨) → (법령 정보 dict | None, 머리 안내)."""
    name, note = resolve_law_name(raw)
    if not name:
        return None, ""
    info = _law_lookup(name, oc)
    if info is None and re.search(r"\S(시행령|시행규칙)$", name):          # '소득세법시행령'
        name2 = re.sub(r"(시행령|시행규칙)$", r" \1", name)
        info = _law_lookup(name2, oc)
    if info and not note and _clean_law_name(raw) != info["name"]:
        note = "'%s' → %s 으로 찾음" % (_clean_law_name(raw), info["name"])
    if info and info["state"] == "이름바뀜":
        note = (note + " · " if note else "") + "지금 이름: %s" % info["cur_name"]
    return info, note


def _law_not_found(raw, oc):
    name, _ = resolve_law_name(raw)
    p = {"OC": oc, "target": "law", "type": "XML", "display": "5", "query": name or str(raw)}
    try:
        _, _, items = parse_search(http_get("lawSearch.do", p))
    except Exception:
        items = []
    cands = ", ".join(pick(d, "법령명한글", "법령명") for d in items[:5])
    return ("[법령 없음] '%s' 와 이름이 같은 법령을 찾지 못했습니다(약칭 사전에도 없음)."
            "%s\n➡ search_law 로 정식 이름을 확인해 다시 넘기세요."
            % (_clean_law_name(raw), (" 비슷한 이름: " + cands) if cands else ""))


# ---- 날짜 · 조문 번호 받기 ---------------------------------------------------
def _norm_date(v):
    """'2024-01-01' · '20240101' · '2024.01.01' · '2024. 1. 1.' · '2024년 1월 1일' → 'YYYYMMDD' (틀리면 '')."""
    s = str(v or "").strip()
    m = re.fullmatch(r"(\d{4})\s*[-./년]?\s*(\d{1,2})\s*[-./월]?\s*(\d{1,2})\s*[.일]?", s)
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return "%04d%02d%02d" % (y, mo, d)


def _today():
    return time.strftime("%Y%m%d")


def _next_day(d8):
    import datetime as _dt
    return (_dt.date(int(d8[:4]), int(d8[4:6]), int(d8[6:8])) + _dt.timedelta(days=1)).strftime("%Y%m%d")


def _fmt_d(d8):
    d8 = _num_id(d8)
    return "%s.%s.%s" % (d8[:4], d8[4:6], d8[6:8]) if len(d8) == 8 else (d8 or "?")


def _jo_label(n, b):
    return "제%d조%s" % (n, ("의%d" % b) if b else "")


_CIRCLED = {chr(0x2460 + i): i + 1 for i in range(20)}             # ①~⑳
_CIRCLED.update({chr(0x3251 + i): i + 21 for i in range(15)})      # ㉑~㉟
_CIRCLED.update({chr(0x32B1 + i): i + 36 for i in range(15)})      # ㊱~㊿
_CIRC = "".join(_CIRCLED)


def _ho_key(v):
    """호번호 '3.' · '3의2.' · '제3호의2' → '3' · '3의2'."""
    m = re.search(r"(\d+)\s*(?:호)?\s*(?:의\s*(\d+))?", str(v or ""))
    return (m.group(1) + (("의" + m.group(2)) if m.group(2) else "")) if m else ""


# ---- 판(版) 고르기 — LID + efYd -----------------------------------------------
def _ver_sort_key(d):
    return (_num_id(d.get("시행일자")), _num_id(d.get("공포일자")), int(_num_id(d.get("공포번호")) or 0))


def _ver_rows(law_id, oc, frm="", to="", display=100, page=1):
    """법령ID 의 판 목록(시행일 내림차순). efYd 범위 = frm~to. -> (총건수, 행들)."""
    p = {"OC": oc, "target": "eflaw", "type": "XML", "LID": _num_id(law_id),
         "display": str(display), "page": str(page)}
    if frm or to:
        p["efYd"] = "%s~%s" % (frm or "19000101", to or "99991231")
    total, _, items = parse_search(http_get("lawSearch.do", p))
    try:
        total = int(total)
    except (TypeError, ValueError):
        total = len(items)
    items = [d for d in items if _num_id(d.get("법령ID")) == _num_id(law_id)]
    items.sort(key=_ver_sort_key, reverse=True)
    return total, items


def _version_at(law_id, date, oc):
    """그날 시행 판 = 시행일 ≤ 기준일 인 판 가운데 가장 늦은 판(같은 날이면 가장 늦게 공포된 판)."""
    _, rows = _ver_rows(law_id, oc, to=date, display=50)
    return rows[0] if rows else None


def _ver_label(row):
    return "시행 %s 판(공포 %s 제%s호 · MST %s)" % (
        _fmt_d(row.get("시행일자")), _fmt_d(row.get("공포일자")),
        int(_num_id(row.get("공포번호")) or 0), _num_id(row.get("법령일련번호")))


def _version_body(row, oc):
    """판 행 → (전체본 text, params) — MST+efYd 정확 조합(판 고정: 다른 판이면 쓰지 않음)."""
    mst, ef = _num_id(row.get("법령일련번호")), _num_id(row.get("시행일자"))
    text, p = _fetch_full_body({"mst": mst, "efYd": ef}, oc)
    if p.get("target") != "eflaw" or _num_id(p.get("efYd")) != ef or not text or \
            _looks_unsubscribed(text) or _looks_empty_detail(text):
        raise LookupError("판 본문을 받지 못함(%s)" % _ver_label(row))
    return text, p


_ART_INDEX = OrderedDict()             # (MST, 시행일) -> 조문 목록 — 판은 바뀌지 않으므로 기한 없음(LRU)
_ART_INDEX_LOCK = threading.Lock()
ART_INDEX_MAX = max(4, int(os.environ.get("LAW_ART_INDEX_MAX", "24")))


def _article_index(row, oc):
    """판의 조문 목록 {(조, 가지): {title, deleted, hangs{항: {호…}}}} + 범위·이름. 판마다 한 번만 받는다."""
    key = (_num_id(row.get("법령일련번호")), _num_id(row.get("시행일자")))
    with _ART_INDEX_LOCK:
        if key in _ART_INDEX:
            _ART_INDEX.move_to_end(key)
            return _ART_INDEX[key]
    text, p = _version_body(row, oc)
    data = http_get_json("lawService.do", p, text)
    law = (data or {}).get("법령") or {}
    jo = law.get("조문")
    units = _as_list(jo.get("조문단위")) if isinstance(jo, dict) else _as_list(jo)
    idx, order = {}, []
    for u in units:
        if not isinstance(u, dict) or (u.get("조문여부") or "").strip() != "조문":
            continue
        n, b = _digits(u.get("조문번호")), _digits(u.get("조문가지번호"))
        body = _text_of(u.get("조문내용"))
        hangs = {}
        for h in _as_list(u.get("항")):
            if not isinstance(h, dict):
                continue
            hn = _CIRCLED.get(str(h.get("항번호") or "").strip()[:1]) or _digits(h.get("항번호")) or 0
            hos = hangs.setdefault(hn, set())
            for ho in _as_list(h.get("호")):
                if isinstance(ho, dict) and _ho_key(ho.get("호번호")):
                    hos.add(_ho_key(ho.get("호번호")))
        deleted = (not hangs) and bool(re.match(r"\s*제\s*\d+\s*조(?:\s*의\s*\d+)?\s*삭제", body))
        idx[(n, b)] = {"title": clean_text(u.get("조문제목") or ""), "deleted": deleted, "hangs": hangs}
        order.append((n, b))
    bi = law.get("기본정보") or {}
    live = [k for k in order if not idx[k]["deleted"]] or order
    info = {"idx": idx, "first": min(live) if live else None, "last": max(live) if live else None,
            "name": clean_text(str(bi.get("법령명_한글") or bi.get("법령명한글") or "")), "row": row}
    with _ART_INDEX_LOCK:
        _ART_INDEX[key] = info
        _ART_INDEX.move_to_end(key)
        while len(_ART_INDEX) > ART_INDEX_MAX:
            _ART_INDEX.popitem(last=False)
    return info


# ---- F1 인용 뽑기 — 볼트 R 규칙 4절(열거·범위 펼침)과 맞춤 ---------------------
_ART_RE = re.compile(r"제\s*(\d+)\s*조(?:\s*의\s*(\d+))?|§\s*(\d+)(?:\s*의\s*(\d+))?")
_HANG_RE = re.compile(r"\s*(?:제\s*(\d+)\s*항|([%s]))" % _CIRC)
_HO_RE = re.compile(r"\s*제\s*(\d+)\s*호(?:\s*의\s*(\d+))?")
_HO_AFTER_CIRC = re.compile(r"(\d+)(?:\s*의\s*(\d+))?(?![\d조항호])")
_MOK_RE = re.compile(r"\s*([가-하])\s*목")
_TAIL_RE = re.compile(r"(?:\s*(?:[%s]|제\s*\d+\s*(?:항|호|목)(?:\s*의\s*\d+)?|[가-하]\s*목|본문|단서|전단|후단"
                      r"|각\s*호(?:\s*외의\s*부분)?|\((?!\s*§)[^()§\n]{1,30}\)))*" % _CIRC)
_SEP_RE = re.compile(r"\s*(?:[ㆍ·･,]|및|또는|와|과)\s*")
_NEXT_RE = re.compile(r"제\s*(\d+)\s*조(?:\s*의\s*(\d+))?|§\s*(\d+)(?:\s*의\s*(\d+))?")
_NEXT_BARE_RE = re.compile(r"§?\s*(\d+)(?:\s*의\s*(\d+))?(?![\d조항호])")      # 「§12·13」 의 13
_RANGE_RE = re.compile(r"\s*(?:부터|내지|[~∼〜])\s*(제\s*(\d+)\s*조(?:\s*의\s*(\d+))?|§\s*(\d+)(?:\s*의\s*(\d+))?)")
_UPTO_RE = re.compile(r"\s*까지")
_AMEND_TAIL = re.compile(r"\((?=[^()]*(?:법률\s*제|대통령령\s*제|부령\s*제|개정))[^()]{1,100}\)\s*$")
_SAME_RE = re.compile(r"(?:(같은\s*법|동\s*법)(?:\s*(시행령|시행규칙))?|(같은\s*영|동\s*령)|(같은\s*규칙|동\s*규칙))\s*$")
_BARE_RE = re.compile(r"(?:^|[^가-힣])(법|영|규칙)\s*$")
_RUN_RE = re.compile(r"[가-힣A-Za-z0-9ㆍ·･ ]+$")
_NAME_STOP = {"법", "령", "법률", "규칙", "시행령", "시행규칙", "세법", "방법", "위법", "적법", "불법", "합법",
              "편법", "입법", "사법", "특례법", "특별법", "기본법", "개별법", "관계법", "관련법", "해당법", "이법",
              "본법", "동법", "같은법", "부령", "법령", "부칙"}
_LINKERS = {"및", "관한", "등에", "등의", "대한", "위한", "의", "과", "와", "또는"}


def _nm4(g):
    return (int(g[0]), int(g[1] or 0)) if g[0] else (int(g[2]), int(g[3] or 0))


def _name_ok(cand, oc):
    """뽑은 이름 후보가 법령이면 정식명, 아니면 ''. 표에 있으면 네트워크 없이."""
    name = _clean_law_name(cand)
    k = _name_key(name)
    if not k or k in _NAME_STOP:
        return ""
    full, _ = _alias_lookup(name)
    if full:
        return full
    if k in _KNOWN:
        return _KNOWN[k]
    try:
        info = _law_lookup(name, oc)
    except Exception as e:
        LOG.warning("법령 이름 확인 실패(%s): %s", name, mask(str(e)))
        return ""
    return info["name"] if info else ""


def _law_before(text, start, prev, oc):
    """조문 표시 바로 앞의 법 이름 → (법령명, 이름 시작 자리, 갈래) / ('', -1, '')."""
    lo = max(0, start - 140)
    s = text[lo:start].rstrip()
    s = re.sub(r"\(\s*$", "", s).rstrip()                       # 「소득법(§12)」 꼴
    m = _AMEND_TAIL.search(s)
    if m:                                                        # 이름과 조 사이 개정 괄호는 건너뜀
        s = s[:m.start()].rstrip()
    if s.endswith("」"):
        k = s.rfind("「")
        if k >= 0:
            raw = s[k + 1:-1].strip()
            return (_name_ok(raw, oc) or _clean_law_name(raw)), lo + k, "낫표"
    m = _SAME_RE.search(s)
    if m:
        if not prev:
            return "", -1, ""
        root = re.sub(r" 시행(령|규칙)$", "", prev)
        if m.group(1):
            law = root + ((" " + m.group(2)) if m.group(2) else "")
        elif m.group(3):
            law = root + " 시행령"
        else:
            law = root + " 시행규칙"
        return law, lo + m.start(), re.sub(r"\s+", " ", m.group(0).strip())
    m = _BARE_RE.search(s)
    if m:
        if not prev:
            return "", -1, ""
        root = re.sub(r" 시행(령|규칙)$", "", prev)
        return ({"법": root, "영": root + " 시행령", "규칙": root + " 시행규칙"}[m.group(1)],
                lo + m.start(1), m.group(1))
    m = _RUN_RE.search(s)
    if not m:
        return "", -1, ""
    run = m.group(0)
    words = run.split()
    if not words or not re.search(r"(?:법|법률|령|규칙)$", words[-1]):
        return "", -1, ""
    found = None
    for k in range(1, min(9, len(words)) + 1):
        full = _name_ok(" ".join(words[-k:]), oc)
        if full:
            found = (full, k)
            if not (k < len(words) and words[-k - 1] in _LINKERS):
                break                      # 앞 낱말이 이음말(및·관한…)이면 더 긴 이름을 더 찾아 본다
    if not found:
        return "", -1, ""
    full, k = found
    pos = lo + m.start() + run.rfind(" ".join(words[-k:]))
    return full, pos, "이름"


def _parse_tail(text, pos):
    """조 뒤의 항·호·목 → (항, 호, 목, 끝 자리)."""
    hang = ho = mok = None
    circ = False
    m = _HANG_RE.match(text, pos)
    if m:
        hang = int(m.group(1)) if m.group(1) else _CIRCLED.get(m.group(2))
        circ = bool(m.group(2))
        pos = m.end()
    m = _HO_RE.match(text, pos)
    if not m and circ:
        m = _HO_AFTER_CIRC.match(text, pos)
    if m:
        ho = m.group(1) + (("의" + m.group(2)) if m.group(2) else "")
        pos = m.end()
    m = _MOK_RE.match(text, pos)
    if m:
        mok = m.group(1)
        pos = m.end()
    return hang, ho, mok, pos


def _cit(raw, law, n, b, hang=None, ho=None, mok=None, how=""):
    return {"raw": re.sub(r"\s+", " ", raw).strip(), "law": law, "n": n, "b": b,
            "hang": hang, "ho": ho, "mok": mok, "how": how}


def _expand(text, pos, law, last, out, consumed, sec_style):
    """R 규칙 — 열거(ㆍ·,및 또는 와 과)·범위(부터·내지·~ … 까지)를 이어 읽어 out 에 더한다.
    범위는 10 개 조 안이고 가지 조문이 아니면 사이 조를 모두, 아니면 두 끝만."""
    while True:
        pos = _TAIL_RE.match(text, pos).end()
        r = _RANGE_RE.match(text, pos)
        if r:
            n2, b2 = _nm4(r.groups()[1:5])
            a0 = last[0]
            mids = [] if (last[1] or b2 or n2 <= a0 or n2 - a0 + 1 > 10) else list(range(a0 + 1, n2))
            for k in mids:
                out.append(_cit("%s %s(범위)" % (law, _jo_label(k, 0)), law, k, 0, how="범위"))
            st = r.start(1)                                  # 범위 끝 조문 자리(「제」·「§」부터)
            consumed.add(st)
            out.append(_cit(text[st:r.end()], law, n2, b2, how="범위"))
            last = (n2, b2)
            pos = r.end()
            u = _UPTO_RE.match(text, pos)
            if u:
                pos = u.end()
            continue
        s = _SEP_RE.match(text, pos)
        if not s:
            return
        nx = _NEXT_RE.match(text, s.end())
        if not nx and sec_style:
            nx = _NEXT_BARE_RE.match(text, s.end())
            if nx:
                n2, b2 = int(nx.group(1)), int(nx.group(2) or 0)
                out.append(_cit(text[nx.start():nx.end()], law, n2, b2, how="열거"))
                last, pos = (n2, b2), nx.end()
                continue
        if not nx:
            return
        consumed.add(nx.start())
        n2, b2 = _nm4(nx.groups())
        hang, ho, mok, end = _parse_tail(text, nx.end())
        out.append(_cit(text[nx.start():end], law, n2, b2, hang, ho, mok, how="열거"))
        last, pos = (n2, b2), end


def extract_citations(text, oc, limit=300):
    """글 → 인용 목록(글 차례). 각 인용 = {raw, law, n, b, hang, ho, mok, how}."""
    text = re.sub(r"「[^「」]{1,80}」", lambda m: re.sub(r"\s+", " ", m.group(0)), str(text or ""))
    out, consumed, prev = [], set(), ""
    for m in _ART_RE.finditer(text):
        if m.start() in consumed:
            continue
        law, nstart, how = _law_before(text, m.start(), prev, oc)
        if not law:
            continue
        n, b = _nm4(m.groups())
        hang, ho, mok, end = _parse_tail(text, m.end())
        out.append(_cit(text[nstart:end], law, n, b, hang, ho, mok, how=how))
        prev = law
        _expand(text, end, law, (n, b), out, consumed, sec_style=bool(m.group(3)) and hang is None)
        if len(out) >= limit:
            break
    return out


def _cit_from_pair(s, oc):
    """'법령명|제N조(의M)[제N항][제N호]' 한 줄 → 인용."""
    if "|" not in str(s):
        got = extract_citations(s, oc, limit=1)
        return got[0] if got else _cit(str(s), "", 0, 0, how="못 읽음")
    name, art = str(s).split("|", 1)
    law = _name_ok(name, oc) or _clean_law_name(name)
    m = _ART_RE.search(art)
    if not m:
        return _cit(str(s), law, 0, 0, how="못 읽음")
    n, b = _nm4(m.groups())
    hang, ho, mok, _ = _parse_tail(art, m.end())
    return _cit(str(s), law, n, b, hang, ho, mok, how="목록")


def _cit_norm(c):
    t = "%s|%s" % (c["law"], _jo_label(c["n"], c["b"]))
    if c.get("hang"):
        t += " 제%d항" % c["hang"]
    if c.get("ho"):
        t += " 제%s호" % c["ho"]
    if c.get("mok"):
        t += " %s목" % c["mok"]
    return t


def _check_in_index(c, info):
    """판의 조문 목록에서 인용 확인 → (상태 기호, 설명)."""
    a = info["idx"].get((c["n"], c["b"]))
    rng = ""
    if info["first"] and info["last"]:
        rng = "이 판 조문 범위 %s ~ %s" % (_jo_label(*info["first"]), _jo_label(*info["last"]))
    if not a:
        return "✗", "없음" + (" · " + rng if rng else "")
    if a["deleted"]:
        return "⌛", "삭제된 조문"
    title = ("(%s)" % a["title"]) if a["title"] else ""
    if c.get("hang"):
        hangs = a["hangs"]
        if c["hang"] not in hangs:
            if set(hangs) <= {0} and c["hang"] == 1:
                return "⚠", "있음 %s — 이 조문은 항 번호가 없음(제1항 표기 확인)" % title
            nums = sorted(h for h in hangs if h)
            have = ("제1항~제%d항" % nums[-1]) if nums else "항 번호 없음"
            return "✗", "조문은 있으나 제%d항 없음 %s · 이 조문: %s" % (c["hang"], title, have)
        if c.get("ho") and c["ho"] not in a["hangs"][c["hang"]]:
            return "✗", "제%d항은 있으나 제%s호 없음 %s" % (c["hang"], c["ho"], title)
    elif c.get("ho"):
        allho = set().union(*a["hangs"].values()) if a["hangs"] else set()
        if c["ho"] not in allho:
            return "✗", "조문은 있으나 제%s호 없음 %s" % (c["ho"], title)
    return "✓", ("있음 " + title).strip()


def _future_note(c, law_id, oc, want_present=True):
    """현행에 없거나 삭제된 조문이 시행예정 판에 있는지 — 가까운 시행예정 판부터 3 판까지."""
    try:
        _, rows = _ver_rows(law_id, oc, frm=_next_day(_today()), display=20)
    except Exception:
        return ""
    for row in sorted(rows, key=_ver_sort_key)[:3]:
        try:
            info = _article_index(row, oc)
        except Exception:
            continue
        a = info["idx"].get((c["n"], c["b"]))
        if a and not a["deleted"]:
            return "시행예정 판(시행 %s · 제%s호)에 있음%s" % (
                _fmt_d(row.get("시행일자")), int(_num_id(row.get("공포번호")) or 0),
                (" (%s)" % a["title"]) if a["title"] else "")
    return ""


def tool_verify_citations(a):
    oc = get_oc(a.get("law_oc"))
    text = str(a.get("text") or "")
    lst = a.get("citations") or []
    if isinstance(lst, str):
        lst = [x for x in re.split(r"[\n;]+", lst) if x.strip()]
    if not text.strip() and not lst:
        return "[입력 오류] text(인용이 든 글) 또는 citations('법령명|제N조' 목록) 가운데 하나는 있어야 합니다."
    date = ""
    if a.get("date"):
        date = _norm_date(a.get("date"))
        if not date:
            return "[입력 오류] date 는 YYYY-MM-DD · YYYYMMDD · YYYY.MM.DD 꼴로 주세요."
    try:
        mx = max(1, min(200, int(a.get("max") or 30)))
    except (TypeError, ValueError):
        mx = 30
    t0 = time.monotonic()
    cits = [_cit_from_pair(s, oc) for s in lst] + (extract_citations(text, oc) if text.strip() else [])
    seen, uniq = set(), []
    for c in cits:
        k = (c["law"], c["n"], c["b"], c.get("hang"), c.get("ho"), c.get("mok"))
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    if not uniq:
        return ("인용 검증 — 글에서 법령 인용(법령명 + 제N조)을 찾지 못했습니다.\n"
                "➡ '소득세법 제89조' · '조특법 §104의5' · 「상속세 및 증여세법」 제18조의2 꼴인지 확인하세요.")
    over = max(0, len(uniq) - mx)
    uniq = uniq[:mx]
    # 법령 · 판을 먼저 정하고(이름당 한 번) 조문 목록은 판마다 한 번 — 병렬로 받는다
    laws = {}
    for c in uniq:
        if c["law"] and c["law"] not in laws:
            try:
                laws[c["law"]] = _law_lookup(c["law"], oc)
            except Exception as e:
                laws[c["law"]] = {"error": str(e)}
    rows = {}
    for nm, inf in laws.items():
        if not inf or inf.get("error") or inf["state"] == "폐지":
            continue
        try:
            rows[nm] = _version_at(inf["id"], date or _today(), oc)
        except Exception as e:
            rows[nm] = {"error": str(e)}
    todo = [r for r in rows.values() if r and not r.get("error")]
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda r: _safe_index(r, oc), todo))
    tally = {"✓": 0, "✗": 0, "⌛": 0, "⊘": 0, "⚠": 0}
    lines = []
    for c in uniq:
        sym, desc, ver = _verify_cit(c, laws, rows, date, oc)
        tally[sym] += 1
        lines.append("%s %s → %s · %s%s" % (sym, c["raw"], _cit_norm(c) if c["law"] else "?", desc,
                                            (" · " + ver) if ver else ""))
    head = ("인용 검증 — 인용 %d건 · ✓ %d · ✗ %d · ⌛ %d · ⊘ %d · ⚠ %d · 기준: %s · %.1f초"
            % (len(uniq), tally["✓"], tally["✗"], tally["⌛"], tally["⊘"], tally["⚠"],
               ("%s 시행 판" % _fmt_d(date)) if date else "현행(%s)" % _fmt_d(_today()),
               time.monotonic() - t0))
    tail = []
    if over:
        tail.append("※ 인용 %d건은 한도(max=%d)를 넘어 보지 않았습니다 — max 를 늘려 다시." % (over, mx))
    tail.append("➡ 조문 본문: get_law_article(law_name=\"법령명\", jo=\"제N조\") · 그날 판: law_as_of(law_name, date, article)")
    return cap(head + "\n" + "\n".join(lines) + "\n\n" + "\n".join(tail), MAX_TEXT)


def _safe_index(row, oc):
    try:
        return _article_index(row, oc)
    except Exception as e:
        LOG.warning("조문 목록 받기 실패(%s): %s", _ver_label(row), mask(str(e)))
        return None


def _verify_cit(c, laws, rows, date, oc):
    """인용 하나 → (기호, 설명, 판 표기)."""
    if not c["law"] or c.get("how") == "못 읽음":
        return "⚠", "인용 꼴을 읽지 못함", ""
    inf = laws.get(c["law"])
    if not inf:
        return "⚠", "법령 이름을 풀지 못함(약칭 사전·법제처 목록에 없음)", ""
    if inf.get("error"):
        return "⚠", "법령 확인 중 오류(%s)" % mask(inf["error"])[:60], ""
    if inf["state"] == "폐지":
        return "⊘", "폐지된 법령(지금 시행 판 없음)", ""
    row = rows.get(c["law"])
    if not row or row.get("error"):
        return "⚠", ("그날(%s) 시행 판 없음" % _fmt_d(date)) if date and not row else "판 확인 실패", ""
    info = _safe_index(row, oc)
    ver = "%s 제%s호" % ("시행 " + _fmt_d(row.get("시행일자")), int(_num_id(row.get("공포번호")) or 0))
    if not info:
        return "⚠", "조문 목록을 받지 못함(잠시 뒤 다시)", ver
    sym, desc = _check_in_index(c, info)
    if inf["state"] == "이름바뀜":
        desc += " · 지금 이름 %s" % inf["cur_name"]
    if sym in ("✗", "⌛") and not date and not c.get("hang"):
        fut = _future_note(c, inf["id"], oc)
        if fut:
            desc += " · 현행 %s · %s" % ("삭제" if sym == "⌛" else "없음", fut)
    return sym, desc, ver


# ---- F3 행위시법 한 번에 --------------------------------------------------------
def _eul(word):
    """목적격 조사 을/를 — 끝 글자 받침으로. 숫자는 읽는 소리로: 2·4·5·9(이·사·오·구)는 '를',
    0 은 십·백·천이라 '을'. 「제95조를」 · 「제18조의2를」 · 「제10조의10을」."""
    ch = str(word or "").rstrip()[-1:]
    if ch and ch in "0123456789":
        return "를" if ch in "2459" else "을"
    if ch and "가" <= ch <= "힣":
        return "을" if (ord(ch) - 0xAC00) % 28 else "를"
    return "을"


def _addenda_blocks(u):
    body = _text_of(u.get("부칙내용"))
    blocks = re.split(r"\n(?=제\s*\d+\s*조(?:\s*의\s*\d+)?\s*\()", "\n" + body)
    return [b.strip() for b in blocks if re.match(r"제\s*\d+\s*조", b.strip())]


def _addenda_excerpt(units, nos, art_label, limit_chars=4000):
    """부칙 가운데 공포번호가 nos 에 들고, 그 조문(제N조[의M])을 말하는 조(적용례·경과조치 등)만 — 정의서 F3 ⑤."""
    pat = re.compile(re.escape(art_label) + r"(?![의\d])")
    out, used = [], 0
    for u in sorted(units, key=lambda x: _digits(x.get("부칙공포번호")), reverse=True):
        no = _digits(u.get("부칙공포번호"))
        if no not in nos:
            continue
        hits = [b for b in _addenda_blocks(u) if pat.search(b)]
        if not hits:
            continue
        d = re.sub(r"\D", "", str(u.get("부칙공포일자") or ""))
        txt = "▸ 부칙 <제%d호, %s>\n%s" % (no, _fmt_d(d), "\n".join(hits))
        if used + len(txt) > limit_chars:
            out.append("…(부칙 발췌 길이 한도 — 나머지는 get_law_addenda(no=공포번호, query=\"%s\"))" % art_label)
            break
        out.append(txt)
        used += len(txt)
    return out


def _addenda_titles(units, nos):
    """그 조문을 말하는 부칙이 없을 때 — 그 판들의 적용례·경과조치·특례 조 제목만(놓치지 않게)."""
    out = []
    for u in sorted(units, key=lambda x: _digits(x.get("부칙공포번호")), reverse=True):
        no = _digits(u.get("부칙공포번호"))
        if no not in nos:
            continue
        ts = [re.match(r"(제\s*\d+\s*조(?:\s*의\s*\d+)?\s*\([^)]*\))", b).group(1)
              for b in _addenda_blocks(u)
              if re.match(r"제\s*\d+\s*조(?:\s*의\s*\d+)?\s*\([^)]*(적용례|경과조치|특례|적용\s*특례)[^)]*\)", b)]
        if ts:
            d = re.sub(r"\D", "", str(u.get("부칙공포일자") or ""))
            out.append("▸ 부칙 <제%d호, %s> %s" % (no, _fmt_d(d), " · ".join(ts)))
    return out


def _article_text_key(data, art):
    """조문 본문 비교 열쇠 — 머리 줄·빈칸·표 그림을 빼고 글자만."""
    body = _format_law_body(data, only_jo=art)
    if not body or body.startswith("[조문 없음]"):
        return ""
    body = "\n".join(ln for ln in body.split("\n") if not ln.startswith("=== "))
    return re.sub(r"[\s%s]" % _BOX, "", body)


def tool_law_as_of(a):
    oc = get_oc(a.get("law_oc"))
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨)이 필요합니다."
    date = _norm_date(a.get("date"))
    if not date:
        return "[입력 오류] date(기준일)가 필요합니다 — YYYY-MM-DD · YYYYMMDD · YYYY.MM.DD."
    inf, note = _find_law(a["law_name"], oc)
    if not inf:
        return _law_not_found(a["law_name"], oc)
    row = _version_at(inf["id"], date, oc)
    if not row:
        return ("[판 없음] %s 은 %s 에 시행 중인 판이 없습니다(아직 제정·시행 전)."
                % (inf["name"], _fmt_d(date)))
    today = _today()
    after_n, after_rows = (0, [])
    if date < today:
        after_n, after_rows = _ver_rows(inf["id"], oc, frm=_next_day(date), to=today, display=100)
    cur = _version_at(inf["id"], today, oc)
    fut_n, fut_rows = _ver_rows(inf["id"], oc, frm=_next_day(today), display=100)
    near = min(fut_rows, key=_ver_sort_key) if fut_rows else None
    when_name = pick(row, "법령명한글", "법령명")
    head = "행위시법 : %s @ %s → %s" % (inf["name"] if inf["state"] != "이름바뀜" else inf["cur_name"],
                                     "%s-%s-%s" % (date[:4], date[4:6], date[6:8]), _ver_label(row))
    if when_name and _name_key(when_name) != _name_key(inf.get("cur_name") or inf["name"]):
        head += " · 당시 이름 「%s」" % when_name
    if date < today:
        head += " · 그 뒤 %d 차례 개정" % after_n
        if cur and _ver_sort_key(cur) != _ver_sort_key(row):
            head += "(현행 시행 %s · 제%s호)" % (_fmt_d(cur.get("시행일자")), int(_num_id(cur.get("공포번호")) or 0))
        elif cur:
            head += "(이 판이 지금도 현행)"
    head += " · 시행예정 %d 건" % fut_n
    if near:
        head += "(가장 가까운 시행 %s · 제%s호)" % (_fmt_d(near.get("시행일자")), int(_num_id(near.get("공포번호")) or 0))
    out = ([note] if note else []) + [head]
    art = str(a.get("article") or a.get("jo") or "").strip()
    try:
        text, p = _version_body(row, oc)
        data = http_get_json("lawService.do", p, text)
    except Exception as e:
        return "\n".join(out + ["[조회 실패] 그 판 본문을 받지 못했습니다 — %s" % mask(str(e))[:120]])
    if art:
        body = _format_law_body(data, only_jo=art)
        out.append("")
        out.append(body or "[조문 없음] %s — 그 판에 해당 조문이 없습니다." % art)
        code = jo_code(art)
        label = _jo_label(_digits(code[:4]), _digits(code[4:]))
        # 부칙 발췌: 그 판과 그 뒤 판(현행까지)의 공포번호 — 부칙은 현행본에 누적 수록
        nos = {_digits(row.get("공포번호"))} | {_digits(r.get("공포번호")) for r in after_rows}
        units, cur_data = [], None
        try:
            src = cur or row
            t2, p2 = _version_body(src, oc)
            cur_data = http_get_json("lawService.do", p2, t2)
            units = _addenda_units(cur_data)
        except Exception as e:
            LOG.warning("부칙 받기 실패: %s", mask(str(e)))
        if cur and cur_data is not None and _ver_sort_key(cur) != _ver_sort_key(row) and body \
                and not body.startswith("[조문 없음]"):
            k_then, k_now = _article_text_key(data, art), _article_text_key(cur_data, art)
            out.append("")
            out.append("▶ 현행과 비교: " + ("같음(기준일 뒤 이 조문은 바뀌지 않음)" if k_then == k_now else
                                          ("다름 — 현행 조문은 get_law_article(law_name=\"%s\", jo=\"%s\")"
                                           % (inf.get("cur_name") or inf["name"], label)) if k_now else
                                          "현행 판에는 이 조문이 없음(삭제·이동 확인)"))
        ex = _addenda_excerpt(units, nos, label) if units else []
        out.append("")
        if ex:
            out.append("── 부칙 발췌(이 판·그 뒤 판에서 %s%s 말하는 조) ──" % (label, _eul(label)))
            out.extend(ex)
        else:
            out.append("── 부칙 발췌: 이 판·그 뒤 판 부칙에 %s%s 말하는 조는 없습니다." % (label, _eul(label)))
            titles = _addenda_titles(units, nos) if units else []
            if titles:
                out.append("   그 판들의 적용례·경과조치(제목만 — 사건에 걸리는지 확인):")
                out.extend(titles)
    else:
        out.append("➡ 조문을 보려면 article=\"제N조\" 를 함께 넘기세요.")
    out.append("")
    out.append("➡ 판 목록: list_law_history(query=\"%s\") · 그날 판과 현행 대조: compare_versions(law_name=\"%s\", "
               "article=\"제N조\", from=\"%s-%s-%s\")" % (inf.get("cur_name") or inf["name"], inf.get("cur_name") or inf["name"],
                                                       date[:4], date[4:6], date[6:8]))
    return cap("\n".join(out), MAX_TEXT)


# ---- F5 신구 조문 대조 --------------------------------------------------------
def _all_ver_rows(law_id, oc):
    rows = []
    for pg in range(1, HISTORY_MAX_PAGES + 1):
        total, part = _ver_rows(law_id, oc, display=100, page=pg)
        rows.extend(part)
        if pg * 100 >= total or not part:
            break
    rows.sort(key=_ver_sort_key, reverse=True)
    return rows


def _version_by_spec(spec, law_id, oc):
    """판 지정 → 판 행. '현행'(기본) · 날짜(그날 시행 판) · 'MST 257993'/'257993' · '제19936호'(공포번호)."""
    s = str(spec or "").strip()
    if not s or s in ("현행", "now", "current", "오늘"):
        return _version_at(law_id, _today(), oc)
    d = _norm_date(s)
    if d:
        return _version_at(law_id, d, oc)
    m = re.fullmatch(r"(?i)(?:MST\s*)?(\d{4,7})", s)
    if m:
        hit = [r for r in _all_ver_rows(law_id, oc) if _num_id(r.get("법령일련번호")) == m.group(1)]
        return hit[0] if hit else None
    m = re.fullmatch(r"(?:공포\s*)?(?:제\s*)?(\d+)\s*호", s)
    if m:
        hit = [r for r in _all_ver_rows(law_id, oc) if _digits(r.get("공포번호")) == int(m.group(1))]
        return hit[0] if hit else None
    return None


def _article_units_for_diff(text):
    """조문 글 → 맞댈 단위 목록 [(비교 열쇠, 보일 줄들)] — 표는 블록 통째로 칸 글자만 비교(너비·줄바꿈 헛 바뀜 방지)."""
    lines = [ln for ln in compact_table(text).split("\n") if ln.strip() and not ln.startswith("=== ")]
    units, i = [], 0
    while i < len(lines):
        if "|" in lines[i]:
            j = i
            while j < len(lines) and "|" in lines[j]:
                j += 1
            block = lines[i:j]
            key = "〔표〕" + re.sub(r"[\s|]", "", "".join(block))
            units.append((key, block))
            i = j
        else:
            units.append((re.sub(r"\s+", " ", lines[i]).strip(), [lines[i]]))
            i += 1
    return units


def _mark_inline(old, new):
    """비슷한 두 줄의 다른 곳에 ⟦ ⟧ 를 친다(글자 단위)."""
    import difflib
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    if sm.ratio() < 0.5:
        return old, new
    o, n = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            o.append(old[i1:i2])
            n.append(new[j1:j2])
        else:
            if i2 > i1:
                o.append("⟦" + old[i1:i2] + "⟧")
            if j2 > j1:
                n.append("⟦" + new[j1:j2] + "⟧")
    return "".join(o), "".join(n)


def tool_compare_versions(a):
    import difflib
    oc = get_oc(a.get("law_oc"))
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨)이 필요합니다."
    art = str(a.get("article") or a.get("jo") or "").strip()
    if not art:
        return "[입력 오류] article(조문 — 예 '제100조의32')이 필요합니다."
    if not a.get("from"):
        return "[입력 오류] from(옛 판 — 날짜·'MST 257993'·'제19936호')이 필요합니다. to 를 빼면 현행과 맞댑니다."
    inf, note = _find_law(a["law_name"], oc)
    if not inf:
        return _law_not_found(a["law_name"], oc)
    r_old = _version_by_spec(a.get("from"), inf["id"], oc)
    r_new = _version_by_spec(a.get("to") or "현행", inf["id"], oc)
    for label, spec, r in (("from", a.get("from"), r_old), ("to", a.get("to") or "현행", r_new)):
        if not r:
            return "[판 없음] %s=%s 에 맞는 판을 찾지 못했습니다(날짜·MST·공포번호 확인)." % (label, spec)
    if _ver_sort_key(r_old) > _ver_sort_key(r_new):
        r_old, r_new = r_new, r_old
    code = jo_code(art)
    label = _jo_label(_digits(code[:4]), _digits(code[4:]))
    head = "신구 대조 : %s %s · 옛 = %s · 새 = %s" % (inf.get("cur_name") or inf["name"], label,
                                                 _ver_label(r_old), _ver_label(r_new))
    out = ([note] if note else []) + [head]
    if _ver_sort_key(r_old) == _ver_sort_key(r_new):
        return "\n".join(out + ["두 판이 같습니다 — from·to 를 다르게 주세요."])
    try:
        t1, p1 = _version_body(r_old, oc)
        t2, p2 = _version_body(r_new, oc)
        b1 = _format_law_body(http_get_json("lawService.do", p1, t1), only_jo=art)
        b2 = _format_law_body(http_get_json("lawService.do", p2, t2), only_jo=art)
    except Exception as e:
        return "\n".join(out + ["[조회 실패] 판 본문을 받지 못했습니다 — %s" % mask(str(e))[:120]])
    miss1, miss2 = b1.startswith("[조문 없음]"), b2.startswith("[조문 없음]")
    if miss1 and miss2:
        return "\n".join(out + ["두 판 모두 %s 이 없습니다." % label])
    if miss1 or miss2:
        return "\n".join(out + ["%s — %s" % ("옛 판에는 없고 새 판에 있음(신설·이동)" if miss1 else
                                            "옛 판에는 있고 새 판에는 없음(삭제·이동)", label), "",
                                (b2 if miss1 else b1)])
    u1, u2 = _article_units_for_diff(b1), _article_units_for_diff(b2)
    sm = difflib.SequenceMatcher(None, [k for k, _ in u1], [k for k, _ in u2], autojunk=False)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    out[-1 if not note else 1] += " · 바뀜 %d 곳" % len(ops)
    if not ops:
        out.append("바뀐 줄 없음(두 판의 이 조문 글이 같음 — 표는 칸 글자 기준)")
        return "\n".join(out)
    for n, (tag, i1, i2, j1, j2) in enumerate(ops, 1):
        out.append("")
        out.append("@@ %d — %s" % (n, {"replace": "바뀜", "delete": "빠짐", "insert": "더해짐"}[tag]))
        olds = [ln for _, ls in u1[i1:i2] for ln in ls]
        news = [ln for _, ls in u2[j1:j2] for ln in ls]
        if tag == "replace" and len(olds) == len(news) and i2 - i1 == j2 - j1 \
                and not any(k.startswith("〔표〕") for k, _ in u1[i1:i2]):
            for o, nw in zip(olds, news):
                mo, mn = _mark_inline(o, nw)
                out.append("− " + mo)
                out.append("+ " + mn)
        else:
            out.extend("− " + ln for ln in olds)
            out.extend("+ " + ln for ln in news)
    out.append("")
    out.append("(− 옛 판 · + 새 판 · ⟦ ⟧ = 다른 글자 · 표는 칸 글자가 다를 때만 바뀜으로 셈)")
    return cap("\n".join(out), MAX_TEXT)


# ---- F4 별표 · 서식 -----------------------------------------------------------
_BOX = "─-╿"
_BORDER_ONLY = re.compile(r"^[%s\s\-=+|]*$" % _BOX)


def _annex_units_of(data):
    law = (data or {}).get("법령") or {}
    b = law.get("별표")
    units = _as_list(b.get("별표단위")) if isinstance(b, dict) else _as_list(b)
    return [u for u in units if isinstance(u, dict)]


def _annex_no(u):
    return _digits(u.get("별표번호")), _digits(u.get("별표가지번호"))


def _annex_label(u):
    kind = (u.get("별표구분") or "별표").strip() or "별표"
    n, g = _annex_no(u)
    if not n and not g:
        return kind                                  # 번호 없는 「[별표]」(상증령 업종표 등)
    num = "%d%s" % (n, ("의%d" % g) if g else "")
    if kind == "서식":
        return "서식 %s · 별지 제%d호%s서식" % (num, n, ("의%d" % g) if g else "")
    return "%s %s" % (kind, num)


def _annex_title(u):
    return clean_text(u.get("별표제목") or u.get("별표제목문자열") or "")


def compact_table(text):
    """표 그림 줄(테두리만 있는 줄)을 빼고 칸 구분을 ' | ' 로 — 긴 별표 분량을 절반 가까이 줄인다."""
    out = []
    for raw in str(text or "").split("\n"):
        if raw.strip() and _BORDER_ONLY.match(raw):
            continue
        boxed = bool(re.search("[%s]" % _BOX, raw))
        ln = re.sub("[%s]+" % _BOX, "|", raw)                 # 테두리 조각(│ ┼ ┤ ─ …)은 모두 칸 경계로
        ln = re.sub(r"\s*\|[\s|]*", " | ", ln)
        ln = re.sub(r"[ \t]{2,}", " ", ln).strip()
        lead = ln.startswith("|")
        ln = re.sub(r"^\|\s*|\s*\|$", "", ln).strip()
        if boxed and ln and "|" not in ln:
            # 「┼───┤급여액 중」 처럼 테두리에 붙은 칸 조각(병합 칸 이어짐) — 표 안 줄로 남겨 표가 끊기지 않게
            ln = ("| " + ln) if lead else (ln + " |")
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip()


def _num_cells(line):
    cells = [c.strip() for c in line.split("|")]
    return sum(1 for c in cells if re.fullmatch(r"[\d,.\-]+", c or "x"))


def _find_pat(key):
    """찾는 말 → 정규식. 숫자로 시작·끝나는 쪽에는 숫자 경계를 둔다 — '3,000' 이 53,000 · 383,000 ·
    3,000,000 에 걸리지 않게(v2.11.0 은 글자 맞춤이라 걸렸다). 앞자리로 찾으려면 끝에 *('3,0*'), 뒷자리는 앞에 *."""
    core = key.strip("*")
    if not core:
        return None
    pat = re.escape(core)
    if core[0] in "0123456789" and not key.startswith("*"):
        pat = r"(?<!\d)(?<!\d[,.])" + pat
    if core[-1] in "0123456789" and not key.endswith("*"):
        pat += r"(?!\d)(?![,.]\d)"
    return re.compile(pat)


def _find_lines(text, find, max_hits=200):
    """find 가 든 줄만 — 그 표의 머리 줄을 앞에 붙인다. 여럿은 ';' 로(쉼표는 '3,000' 같은 천 단위라 나누지 않는다).
    숫자는 숫자 단위로 맞춘다(_find_pat)."""
    pats = [p for p in (_find_pat(k.strip()) for k in str(find).split(";")) if p]
    if not pats:
        return ""
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if any(p.search(ln) for p in pats)]
    if not hits:
        return ("[찾기 결과 없음] '%s' — 이 말이 든 줄이 없습니다. 숫자는 숫자 단위로 맞춥니다"
                "(앞자리로 찾으려면 끝에 * — 예 '3,0*')." % find)
    out, shown = [], None
    for i in hits[:max_hits]:
        if "|" in lines[i]:
            j = i                                        # 이 줄이 든 표의 첫 줄
            while j > 0 and "|" in lines[j - 1]:
                j -= 1
            if j != shown:                               # 표가 바뀌면 그 표의 머리 줄(첫 칸이 숫자가 아닌 줄)을 붙인다
                head = []
                for k in range(j, min(i, j + 6)):
                    if re.fullmatch(r"[\d,.\-]+", lines[k].split("|")[0].strip() or "x"):
                        break
                    head.append(lines[k])
                if out:
                    out.append("")
                out.extend(head + (["…"] if head else []))
                shown = j
        out.append(lines[i])
    more = len(hits) - min(len(hits), max_hits)
    return "\n".join(out + (["…(맞는 줄 %d개 더 — find 를 좁히세요)" % more] if more > 0 else []))


def _paginate(text, page, size):
    pages, cur, n = [], [], 0
    for ln in text.split("\n"):
        if cur and n + len(ln) + 1 > size:
            pages.append("\n".join(cur))
            cur, n = [], 0
        cur.append(ln)
        n += len(ln) + 1
    if cur:
        pages.append("\n".join(cur))
    page = max(1, min(page, len(pages) or 1))
    return (pages[page - 1] if pages else ""), page, len(pages) or 1


def _annex_source(a, oc):
    """law_name(+date) → (판 행 | None, 전체본 data, 머리 안내, 법령 정보) — 실패면 (None, None, 안내문, None)."""
    inf, note = _find_law(a.get("law_name"), oc)
    if not inf:
        return None, None, _law_not_found(a.get("law_name"), oc), None
    date = _norm_date(a.get("date")) if a.get("date") else ""
    if a.get("date") and not date:
        return None, None, "[입력 오류] date 는 YYYY-MM-DD · YYYYMMDD · YYYY.MM.DD 꼴로 주세요.", None
    row = _version_at(inf["id"], date or _today(), oc)
    if not row:
        return None, None, "[판 없음] %s 의 %s 시행 판이 없습니다." % (inf["name"], _fmt_d(date or _today())), None
    text, p = _version_body(row, oc)
    return row, http_get_json("lawService.do", p, text), note, inf


def _annex_kind_ok(u, kind):
    k = (u.get("별표구분") or "별표").strip()
    return kind in ("", "전체", "all") or k == kind


def _annex_files(u):
    out = []
    hwp = str(u.get("별표HWP파일명") or "")
    ext = (os.path.splitext(hwp)[1].lstrip(".").upper() or "HWP") if hwp else ""
    for label, key in (("원본" + ("(%s)" % ext if ext else ""), "별표서식파일링크"), ("PDF", "별표서식PDF파일링크")):
        link = str(u.get(key) or "")
        if link.startswith("/"):
            link = "https://www.law.go.kr" + link
        if link.startswith("http"):
            out.append("  [%s] %s" % (label, mask(link)))
    return out


def tool_list_annexes(a):
    oc = get_oc(a.get("law_oc"))
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨)이 필요합니다."
    row, data, note, inf = _annex_source(a, oc)
    if row is None:
        return note
    kind = str(a.get("kind") or "전체").strip()
    units = [u for u in _annex_units_of(data) if _annex_kind_ok(u, kind)]
    nb = sum(1 for u in units if (u.get("별표구분") or "별표").strip() != "서식")
    head = "별표·서식 목록 — %s · %s · 별표 %d · 서식 %d" % (
        pick(row, "법령명한글", "법령명"), _ver_label(row), nb, len(units) - nb)
    lines = ([note] if note else []) + [head, ""]
    for u in units:
        body = _text_of(u.get("별표내용"))
        rev = re.findall(r"<(?:개정|신설|전문개정)\s*([0-9.\s,]+?)\s*>", body[:300])
        ext = os.path.splitext(str(u.get("별표HWP파일명") or ""))[1].lstrip(".").upper()
        lines.append("[%s] %s%s · %s%s" % (
            _annex_label(u), _annex_title(u),
            (" · <개정 %s>" % rev[-1].strip(" ,.")) if rev else "",
            ("글 %s자" % format(len(body), ",")) if body.strip() else "글 없음(파일만)",
            (" · " + ext) if ext else ""))
    if not units:
        lines.append("(이 판에 %s 이 없습니다)" % (kind if kind not in ("전체", "") else "별표·서식"))
    else:
        u0 = units[0]
        n, g = _annex_no(u0)
        lines.append("")
        lines.append("➡ 한 건 보기: get_annex(law_name=\"%s\", annex_no=\"%d%s\"%s) — 긴 표는 page=2… 또는 find=\"찾을 글\""
                     % (pick(row, "법령명한글", "법령명"), n, ("의%d" % g) if g else "",
                        ", kind=\"서식\"" if (u0.get("별표구분") or "") == "서식" else ""))
    return cap("\n".join(lines), MAX_TEXT)


def tool_get_annex(a):
    oc = get_oc(a.get("law_oc"))
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨)이 필요합니다."
    if not (a.get("annex_no") or a.get("query")):
        return "[입력 오류] annex_no(별표 번호 — 예 '2', '2의2') 또는 query(제목 낱말) 가 필요합니다. 목록은 list_annexes."
    row, data, note, inf = _annex_source(a, oc)
    if row is None:
        return note
    kind = str(a.get("kind") or "별표").strip()
    units = [u for u in _annex_units_of(data) if _annex_kind_ok(u, kind)]
    if a.get("annex_no"):
        m = re.search(r"(\d+)(?:\s*(?:호)?\s*의\s*(\d+))?", str(a["annex_no"]))
        want = (int(m.group(1)), int(m.group(2) or 0)) if m else (0, 0)     # '별표' 만 = 번호 없는 별표
        sel = [u for u in units if _annex_no(u) == want]
    else:
        q = _name_key(a["query"])
        sel = [u for u in units if q in _name_key(_annex_title(u))]
    if not sel:
        return ("[%s 없음] %s · %s 에 맞는 %s 이 없습니다. ➡ list_annexes(law_name=\"%s\") 로 번호를 확인하세요."
                % (kind, pick(row, "법령명한글"), _ver_label(row), kind, pick(row, "법령명한글")))
    if len(sel) > 1:
        return ("[여러 건] '%s' 에 맞는 %s %d건 — annex_no 로 하나를 고르세요:\n%s"
                % (a.get("query") or a.get("annex_no"), kind, len(sel),
                   "\n".join("  [%s] %s" % (_annex_label(u), _annex_title(u)) for u in sel[:20])))
    u = sel[0]
    head = "=== %s [%s] %s · %s ===" % (pick(row, "법령명한글", "법령명"), _annex_label(u), _annex_title(u),
                                         _ver_label(row))
    body = compact_table(_text_of(u.get("별표내용")))
    files = _annex_files(u)
    pre = ([note] if note else []) + [head]
    if not body:
        return "\n".join(pre + ["[글 없음] 법제처 응답에 이 %s 의 글이 없습니다(그림·파일 별표). 원문 파일:" % kind]
                         + files)
    if a.get("find"):
        return cap("\n".join(pre + ["(찾기 '%s')" % a["find"], _find_lines(body, a["find"]), ""] + files), MAX_TEXT)
    try:
        page = int(a.get("page") or 1)
    except (TypeError, ValueError):
        page = 1
    size = max(2000, MAX_TEXT - 800)
    chunk, page, total = _paginate(body, page, size)
    tail = []
    if total > 1:
        n, g = _annex_no(u)
        tail.append("— %d/%d쪽%s" % (page, total, (" · 다음 쪽: get_annex(law_name=\"%s\", annex_no=\"%d%s\", page=%d)"
                                                     % (pick(row, "법령명한글"), n, ("의%d" % g) if g else "", page + 1))
                                                    if page < total else " (끝)"))
        tail.append("   특정 줄만: find=\"3,000\" 처럼 찾을 글을 넘기면 그 줄과 표 머리만 나옵니다.")
    return "\n".join(pre + [chunk, ""] + tail + files)


# =============================================================================
# v2.11 업그레이드 P3 (2026-10) — F6 조문 연혁 · F8 국세청 기본통칙·세법집행기준 · F9 국세청 해석 검색
#   F6 = 법제처 lsJoHstInf(조문별 변경 이력 · lawService + 법령ID + JO). 응답의 '조문링크' 칸에는
#        키(OC)가 그대로 들어 있어 버린다(정의서 공통 요구 3).
#   F8·F9 = 국세법령정보시스템(taxlaw.nts.go.kr) 내부 호출 — 공식 API 아님(실측 2026-10-13).
#        기본통칙: ASISTD001MR01(법 목록) · MR03(연도 판) · MR02(통칙 본문)
#        집행기준: ASISTE001MR03(연도 판 · PDF 파일) · MR02(목차 · PDF 쪽) — 본문은 연도별 PDF 한 권뿐
#        해석 검색: ASEISA001MR01(통합검색 · collection=question) — 법제처 목록에 없는 해석도 나온다
#        판례 · 결정례 검색(v2.13): 같은 호출의 collection=precedent — 법원 판결 · 조세심판 · 이의신청 · 심사 · 과세전적부심사
#        ★예규·해석 기법이라 GitHub 강의 저장소에는 넣지 않는다(8/2 결정) — 이 코어는 NAS 에만 있다.
# =============================================================================
_HS_TAGS = re.compile(r"<!H[SE]>")


def _taxlaw_action(action_id, param, referer_path, ttl=None):
    """국세법령정보시스템 내부 호출(POST /action.do) → data[action_id]. 실패하면 예외(사유 담음)."""
    key = "taxlaw|%s|%s" % (action_id, json.dumps(param, sort_keys=True, ensure_ascii=False))
    hit = _cache_get(key)
    if hit is not None:
        return json.loads(hit)
    body = urllib.parse.urlencode({"actionId": action_id,
                                   "paramData": json.dumps(param, ensure_ascii=False)}, encoding="utf-8").encode("utf-8")
    req = urllib.request.Request(TAXLAW_ACTION, data=body, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA, "Origin": TAXLAW_HOST,
        "Referer": TAXLAW_HOST + referer_path, "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*", "Connection": "close"})
    with _taxlaw_gate:
        gap = TAXLAW_MIN_INTERVAL - (time.monotonic() - _taxlaw_last[0])
        if gap > 0:
            time.sleep(gap)
        _taxlaw_last[0] = time.monotonic()
    with urlopen_tls(req, TAXLAW_TIMEOUT) as resp:
        raw = resp.read(TAXLAW_MAX_BYTES + 1)
    if len(raw) > TAXLAW_MAX_BYTES:
        raise RuntimeError("국세법령정보시스템 응답 과대")
    node = (json.loads(raw.decode("utf-8", "replace")).get("data") or {}).get(action_id)
    if node is None:
        raise LookupError("국세법령정보시스템 응답에 %s 자료가 없음(사이트 개편 가능)" % action_id)
    _cache_put(key, json.dumps(node, ensure_ascii=False), ttl=ttl or CACHE_TTL)
    return node


def _nts_clean(s):
    """국세법령정보시스템 글 — 검색 강조 태그·HTML 엔티티·폭 없는 빈칸(U+200B 등)을 뺀다."""
    s = html.unescape(_HS_TAGS.sub("", str(s or "")))
    return clean_text(_ZW_RE.sub("", s))


_RULE_SEG = r"(\d+)(?:\s*의\s*(\d+))?"
_RULE_RE = re.compile(r"\s*%s\s*-\s*%s\s*(?:…|\.{2,3}|-|·{2,3})\s*%s" % (_RULE_SEG, _RULE_SEG, _RULE_SEG))


def _rule_no(title):
    """통칙·집행기준 번호 → ((법 조, 가지), (영 조, 가지), (일련, 가지)).
    '1-3…1' · '88-0-2' · '1-3-1' → ((1, 0), (3, 0), (1, 0)) · '88-152의3-1' → ((88, 0), (152, 3), (1, 0)).
    v2.12.0 — 그 전에는 「의」 가 든 번호를 못 읽어 목차에서 빠졌다(2026-10-13 실측: 양도소득세 436 항 가운데 172 항 ·
    상속증여세 152 · 조특법 112 · 법인세 86 · 국세기본법 72)."""
    m = _RULE_RE.match(str(title or ""))
    if not m:
        return None
    g = [int(x) if x else 0 for x in m.groups()]
    return (g[0], g[1]), (g[2], g[3]), (g[4], g[5])


def _rule_filter(items, a, title_key="ntstTextNm", text_key="ntstTextCntn"):
    """번호·조문·찾을 말로 고른다 → (고른 것, 갈래 설명)."""
    if a.get("number"):
        want = _rule_no(str(a["number"]))
        if want is None:
            return [], "번호 %s(꼴을 알 수 없음 — 예 '88-152의3-1' · '1-3…1')" % a["number"]
        return [x for x in items if _rule_no(x.get(title_key)) == want], "번호 %s" % a["number"]
    if a.get("article"):
        code = jo_code(a["article"])
        art = (_digits(code[:4]), _digits(code[4:]))
        return [x for x in items if (_rule_no(x.get(title_key)) or ((0, 0),))[0] == art], \
            "법 %s 관련" % _jo_label(*art)
    if a.get("query"):
        q = str(a["query"]).strip()
        return [x for x in items if q in _nts_clean(x.get(title_key)) or q in _nts_clean(x.get(text_key))], \
            "찾을 말 '%s'" % q
    return list(items), "목차"


# ---- F6 조문 연혁 ------------------------------------------------------------
def _hist_kind(reason):
    r = str(reason or "")
    for k in ("전문개정", "신설", "삭제"):
        if k in r:
            return k
    return "개정"


def tool_article_history(a):
    oc = get_oc(a.get("law_oc"))
    if not a.get("law_name") or not (a.get("article") or a.get("jo")):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨)과 article(조문 — 예 '제100조의32')이 필요합니다."
    inf, note = _find_law(a["law_name"], oc)
    if not inf:
        return _law_not_found(a["law_name"], oc)
    code = jo_code(a.get("article") or a.get("jo"))
    label = _jo_label(_digits(code[:4]), _digits(code[4:]))
    p = {"OC": oc, "target": "lsJoHstInf", "type": "JSON", "ID": inf["id"], "JO": code}
    try:
        svc = json.loads(http_get("lawService.do", p)).get("LawService") or {}
    except Exception as e:
        return "[조회 실패] 조문 변경 이력을 받지 못했습니다 — %s" % mask(str(e))[:120]
    rows = [r for r in _as_list(svc.get("law")) if isinstance(r, dict)]
    name = inf.get("cur_name") or inf["name"]
    if not rows:
        return ("\n".join(([note] if note else []) +
                          ["조문 연혁 : %s %s — 법제처 변경 이력에 기록이 없습니다(조번호 확인 · 아주 오래된 조문)." % (name, label),
                           "➡ 그날 판으로 보기: law_as_of(law_name=\"%s\", date=\"YYYY-MM-DD\", article=\"%s\")" % (name, label)]))
    lines = []
    for r in rows:                                  # 응답 차례 = 시행일 오름차순(실측). 조문링크(키 포함)는 버린다
        jo, li = r.get("조문정보") or {}, r.get("법령정보") or {}
        lines.append("· 시행 %s · 공포 %s 제%s호 · %s · %s%s" % (
            _fmt_d(li.get("시행일자") or jo.get("조문변경일")), _fmt_d(li.get("공포일자")),
            int(_num_id(li.get("공포번호")) or 0), li.get("제개정구분명") or "?", _hist_kind(jo.get("변경사유")),
            ("(%s)" % jo.get("변경사유")) if jo.get("변경사유") and jo.get("변경사유") not in ("조문변경",) else ""))
    first = (rows[0].get("법령정보") or {}).get("시행일자")
    last = (rows[-1].get("법령정보") or {}).get("시행일자")
    head = "조문 연혁 : %s %s — %d 차례 바뀜(처음 %s · 마지막 %s)" % (
        name, label, len(rows), _fmt_d(first), _fmt_d(last))
    tail = ["", "➡ 두 판 대조: compare_versions(law_name=\"%s\", article=\"%s\", from=\"%s\")"
            % (name, label, "%s-%s-%s" % (last[:4], last[4:6], last[6:8]) if last and len(_num_id(last)) == 8 else "YYYY-MM-DD"),
            "   그날 판: law_as_of(law_name=\"%s\", date=\"YYYY-MM-DD\", article=\"%s\")" % (name, label)]
    return cap("\n".join(([note] if note else []) + [head] + lines + tail), MAX_TEXT)


# ---- F8 국세 기본통칙 ----------------------------------------------------------
_BSC_LIST_PATH, _BSC_PATH = "/st/USESTD001M.do", "/st/USESTD002M.do"


def _nts_pick_book(raw, books):
    """books = [(id, 이름)] — 법령 이름(약칭 됨)과 맞는 것."""
    name, _ = resolve_law_name(raw)
    k = _name_key(name)
    exact = [b for b in books if _name_key(b[1]) == k]
    return exact or [b for b in books if k and (k in _name_key(b[1]) or _name_key(b[1]) in k)]


def tool_get_basic_rule(a):
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 — 약칭 됨, 예 '소득세법', '상증법')이 필요합니다."
    try:
        books = [(x["ntstBscId"], x["ntstNm"]) for x in
                 _taxlaw_action("ASISTD001MR01", {}, _BSC_LIST_PATH, ttl=86400).get("bscExrDVOList") or []]
        hit = _nts_pick_book(a["law_name"], books)
        if not hit:
            return ("[기본통칙 없음] '%s' 의 국세 기본통칙이 없습니다. 기본통칙이 있는 법: %s"
                    % (a["law_name"], " · ".join(n for _, n in books)))
        bid, bname = hit[0]
        years = [y.get("rgtYr") for y in
                 _taxlaw_action("ASISTD001MR03", {"ntstBscId": bid}, _BSC_PATH, ttl=86400).get("bscExrDVOList") or []]
        yr = str(a.get("year") or (years[0] if years else ""))
        if years and yr not in years:
            return "[판 없음] %s 기본통칙 %s년 판이 없습니다. 있는 판: %s" % (bname, yr, " · ".join(years))
        node = _taxlaw_action("ASISTD001MR02", {"ntstBscId": bid, "rgtYr": yr}, _BSC_PATH, ttl=7 * 86400)
    except Exception as e:
        return "[조회 실패] 국세법령정보시스템 기본통칙을 받지 못했습니다 — %s" % mask(str(e))[:140]
    items = node.get("bscExrDVOList") or []
    rules = [x for x in items if _rule_no(x.get("ntstTextNm"))]
    sel, how = _rule_filter(rules, a)
    head = "국세 기본통칙 — %s · %s년 판(있는 판: %s) · 통칙 %d개 · %s %d건" % (
        bname, yr, " · ".join(years[:8]), len(rules), how, len(sel))
    out = [head]
    if not sel:
        out.append("(맞는 통칙이 없습니다 — number='1-3…1' · article='제1조' · query='찾을 말' 로)")
    elif len(sel) <= 3 and how != "목차":
        for x in sel:
            out += ["", "▸ %s" % _nts_clean(x.get("ntstTextNm")), html_to_text(x.get("ntstTextCntn") or "")]
    else:
        out += [""] + ["· %s" % _nts_clean(x.get("ntstTextNm")) for x in sel[:150]]
        if len(sel) > 150:
            out.append("…(%d건 더 — article·query 로 좁히세요)" % (len(sel) - 150))
        out.append("")
        out.append("➡ 본문: get_basic_rule(law_name=\"%s\", number=\"%s\")" % (
            bname, _nts_clean(sel[0].get("ntstTextNm")).split()[0] if sel else "1-0…1"))
    out += ["", "출처: 국세법령정보시스템 기본통칙(공식 API 아님 — 인용 전 원문 대조) %s%s?ntstBscId=%s"
            % (TAXLAW_HOST, _BSC_PATH, bid)]
    return cap("\n".join(out), MAX_TEXT)


# ---- F8 세법집행기준 — 목차·PDF 쪽(본문은 연도별 PDF) -------------------------------
_EXE_BOOKS = (   # (ntstBscId, ntstPlcnBkId, 책 이름) — 국세법령정보시스템 common_st.js 의 목록(2026-10-13)
    ("100000000000001586", "511100000000000001", "국세기본법 집행기준"),
    ("100000000000001585", "511100000000000002", "국세징수법 집행기준"),
    ("100000000000001563", "511100000000000003", "법인세 집행기준"),
    ("100000000000000603", "511100000000000004", "국제조세 집행기준"),
    ("100000000000001565", "511100000000000005", "종합소득세 집행기준"),
    ("200000000000001565", "511100000000000006", "양도소득세 집행기준"),
    ("100000000000009873", "511100000000000007", "종합부동산세 집행기준"),
    ("100000000000001561", "511100000000000008", "상속증여세 집행기준"),
    ("100000000000001570", "511100000000000009", "개별소비세 집행기준"),
    ("100000000000001568", "511100000000000009", "인지세 집행기준"),
    ("100000000000001566", "511100000000000009", "주세 집행기준"),
    ("100000000000013931", "511100000000000009", "주류면허법 집행기준"),
    ("100000000000000621", "511100000000000010", "증권거래세 집행기준"),
    ("100000000000001571", "510000000000000448", "부가가치세 집행기준"),
    ("100000000000001584", "510000000000000823", "조세특례제한법 집행기준"),
)
_EXE_BY_LAW = {"국세기본법": ("국세기본법",), "국세징수법": ("국세징수법",), "법인세법": ("법인세",),
               "국제조세조정에관한법률": ("국제조세",), "소득세법": ("종합소득세", "양도소득세"),
               "종합부동산세법": ("종합부동산세",), "상속세및증여세법": ("상속증여세",),
               "개별소비세법": ("개별소비세",), "인지세법": ("인지세",), "주세법": ("주세",),
               "주류면허등에관한법률": ("주류면허법",), "증권거래세법": ("증권거래세",),
               "부가가치세법": ("부가가치세",), "조세특례제한법": ("조세특례제한법",)}
_EXE_PATH = "/st/USESTE001M.do"


def _exe_books_for(raw):
    name, _ = resolve_law_name(raw)
    k = _name_key(name)
    heads = _EXE_BY_LAW.get(k) or ()
    got = [b for b in _EXE_BOOKS if any(b[2].startswith(h + " ") for h in heads)]
    return got or [b for b in _EXE_BOOKS if k and (_name_key(b[2]).startswith(k) or k in _name_key(b[2]))]


# ---- F8 집행기준 본문 — 볼트 J- 노트(v2.12.0) -----------------------------------------
# PC5 본부 10-13 회신(대표님 확인): 집행기준 본문은 볼트 J- 노트의 「## 원문」 을 읽는다 — 읽기만 · NAS 가 닿는 PC 만 ·
# 안 닿으면 지금처럼 목차 · PDF 쪽으로 물러난다. 노트 = 국세청 집행기준 PDF 글자층을 쪽 그림과 대조해 옮긴 정본(2024.10 판).
# aliases · 관련논점 · 「## 이음」 은 볼트 안 고리라 내지 않는다. 현행표지 · 「## 주의」 · 「## 현행 확인」 은 원문과 갈라
# 「볼트 표지 · 볼트 주의 · 볼트 현행 확인」 으로 적는다.
VAULT_DIR = os.environ.get("LAW_VAULT_DIR", r"\\SynologyNAS\Alltax\BOOK\10_논점")
VAULT_ON = os.environ.get("LAW_VAULT", "1") != "0"
_EXE_VAULT = {    # 책 → (볼트 묶음 폴더, 파일 머리). 2026-10-13 목차 번호 대조 — 11권 모두 노트 번호가 목차와 맞음.
    "국세기본법 집행기준": ("J-01", "J01-"), "국세징수법 집행기준": ("J-09", "J09-"),
    "법인세 집행기준": ("J-03", "J03-"), "종합소득세 집행기준": ("J-02", "J02-"),
    "상속증여세 집행기준": ("J-04", "J04-"), "부가가치세 집행기준": ("J-05", "J05-"),
    "조세특례제한법 집행기준": ("J-08", "J08-"), "개별소비세 집행기준": ("J-06", "J06-개소-"),
    "인지세 집행기준": ("J-06", "J06-인지-"), "주세 집행기준": ("J-06", "J06-주세-"),
    "주류면허법 집행기준": ("J-06", "J06-주류-"),
}   # 국제조세 · 양도소득세 · 종합부동산세 · 증권거래세는 볼트에 없다(목차 · PDF 쪽만).
_VAULT_TTL = 600                      # 닿음 여부 · 폴더 목록을 기억하는 초
_vault_lock = threading.Lock()
_vault = {"at": -1e9, "ok": False, "index": {}}


def _vault_ready():
    """볼트 폴더가 닿는지. 닿지 않는 NAS 경로는 수십 초 멈출 수 있어 3초만 기다리고, 결과를 10분 기억한다."""
    if not VAULT_ON:
        return False
    with _vault_lock:
        if time.monotonic() - _vault["at"] < _VAULT_TTL:
            return _vault["ok"]
    box = {}
    probe = threading.Thread(target=lambda: box.__setitem__("ok", os.path.isdir(VAULT_DIR)), daemon=True)
    probe.start()
    probe.join(3.0)
    with _vault_lock:
        _vault.update(at=time.monotonic(), ok=bool(box.get("ok")), index={})
        return _vault["ok"]


def _vault_index(folder, head):
    """묶음 폴더 → {번호 열쇠(_rule_no): 노트 경로}. 파일 이름 = 머리 + '번호-제목.md'(J02-12-0-1-… · J06-개소-1-0-1-…)."""
    with _vault_lock:
        got = _vault["index"].get((folder, head))
    if got is not None:
        return got
    idx = {}
    try:
        base = os.path.join(VAULT_DIR, folder)
        for fn in os.listdir(base):
            if fn.startswith(head) and fn.endswith(".md") and "-00-00-" not in fn:
                k = _rule_no(fn[len(head):])
                if k:
                    idx.setdefault(k, os.path.join(base, fn))
    except OSError as e:
        LOG.warning("볼트 목록 실패(%s): %s", folder, e)
    with _vault_lock:
        _vault["index"][(folder, head)] = idx
    return idx


def _vault_note(path):
    """J- 노트 → {이름 · 판 · 출처 · 원문파일 · 현행표지 · 원문 · 주의 · 현행 확인}. 원문이 없거나 못 읽으면 None."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            for ln in text[3:end].splitlines():          # 'key: "값"' 꼴만(목록 · 들여쓴 줄은 쓰지 않음)
                m = re.match(r"([^\s:#-][^:]*):\s*(\S.*)$", ln)
                if m:
                    meta[m.group(1).strip()] = m.group(2).strip().strip('"')
            body = text[end + 4:]
    secs, cur = {}, None
    for ln in body.splitlines():
        h = re.match(r"##\s+(.+?)\s*$", ln)
        if h:
            cur = secs.setdefault(h.group(1), [])
        elif cur is not None:
            cur.append(ln)

    def sec(name, lead_quote=False):
        lines = list(secs.get(name) or [])
        while lines and (not lines[0].strip() or (lead_quote and lines[0].startswith(">"))):
            lines.pop(0)                                    # 원문 머리의 '> … 판 · 번호 · pdf 쪽' 표기는 출처 줄로 대신
        return "\n".join(lines).strip()

    note = {k: meta.get(k, "") for k in ("판", "출처", "원문파일", "현행표지")}
    note.update(이름=os.path.basename(path)[:-3], 원문=sec("원문", True), 주의=sec("주의"), 현행확인=sec("현행 확인"))
    return note if note["원문"] else None


def _vault_block(note):
    def indent(t):
        return ["  " + ln if ln.strip() else "" for ln in t.splitlines()]

    out = ["  ── 원문 — 볼트 %s · %s · 원문파일 %s ──" % (note["이름"], note["출처"] or note["판"], note["원문파일"] or "?")]
    out += indent(note["원문"])
    if note["현행표지"]:
        out.append("  ── 볼트 표지(볼트 안 표시 · 현행 판정 아님): %s" % note["현행표지"])
    for key, label in (("현행확인", "볼트 현행 확인(원문 아님)"), ("주의", "볼트 주의(원문 아님)")):
        if note[key]:
            out.append("  ── %s ──" % label)
            out += indent(note[key])
    return out


def tool_get_execution_standard(a):
    if not a.get("law_name"):
        return "[입력 오류] law_name(법령 이름 · 약칭 · 또는 책 이름 '양도소득세')이 필요합니다."
    books = _exe_books_for(a["law_name"])
    if not books:
        return "[집행기준 없음] '%s' 에 맞는 세법집행기준이 없습니다. 있는 책: %s" % (
            a["law_name"], " · ".join(b[2] for b in _EXE_BOOKS))
    out, total, used = [], 0, 0
    for bid, bk, bname in books:
        try:
            ys = _taxlaw_action("ASISTE001MR03", {"ntstBscId": bid, "ntstPlcnBkId": bk}, _EXE_PATH,
                                ttl=86400).get("exeBaseDVOList") or []
            yrs = [y.get("rgtYr") for y in ys]
            yr = str(a.get("year") or (yrs[0] if yrs else ""))
            ye = next((y for y in ys if str(y.get("rgtYr")) == yr), None)
            if not ye:
                out.append("[판 없음] %s %s년 판이 없습니다. 있는 판: %s" % (bname, yr, " · ".join(yrs)))
                continue
            items = _taxlaw_action("ASISTE001MR02", {"ntstBscId": bid, "rgtYr": yr, "ntstPlcnBkId": bk}, _EXE_PATH,
                                   ttl=7 * 86400).get("exeBaseDVOList") or []
        except Exception as e:
            out.append("[조회 실패] %s — %s" % (bname, mask(str(e))[:120]))
            continue
        rules = [x for x in items if _rule_no(x.get("ntstTextNm"))]
        sel, how = _rule_filter(rules, a)
        total += len(sel)
        pdf = "%s/downloadFile.do?fleId=%s&fleSn=%s" % (TAXLAW_HOST, ye.get("fleId"), ye.get("fleSn")) \
            if ye.get("fleId") and ye.get("fleSn") else ""
        out.append("세법집행기준 — %s · %s년 판(발간 %s · 있는 판: %s) · 항목 %d개 · %s %d건" % (
            bname, yr, _fmt_d(ye.get("plcnDt")), " · ".join(yrs[:8]), len(rules), how, len(sel)))
        # 볼트 원문 — 번호 · 조문 · 찾을 말로 3 항 이하를 골랐을 때만(목차 통째로는 너무 길다)
        vault, notes, vault_msg = _EXE_VAULT.get(bname), {}, ""
        if vault and sel and how != "목차" and len(sel) <= 3:
            if _vault_ready():
                idx = _vault_index(*vault)
                for x in sel:
                    k = _rule_no(x.get("ntstTextNm"))
                    nt = _vault_note(idx[k]) if k in idx else None
                    pan = re.search(r"\d{4}", nt["판"]) if nt else None
                    if nt and pan and pan.group() == yr:
                        notes[k] = nt
                    elif nt:
                        vault_msg = "(볼트 노트는 %s — 이 %s년 판과 달라 싣지 않음)" % (nt["판"], yr)
            else:
                vault_msg = "(볼트 J- 노트에 닿지 않아 목차 · PDF 쪽만 — NAS 연결을 확인하세요)"
        for x in sel[:120]:
            out.append("· [%s] %s · PDF %s쪽" % (_nts_clean(x.get("ntstTextNm")).split()[0],
                                               " ".join(_nts_clean(x.get("ntstTextNm")).split()[1:]),
                                               x.get("srtOrdr") or "?"))
            nt = notes.get(_rule_no(x.get("ntstTextNm")))
            if nt:
                out += _vault_block(nt)
                used += 1
        if vault_msg:
            out.append("  " + vault_msg)
        if len(sel) > 120:
            out.append("…(%d건 더 — article·query 로 좁히세요)" % (len(sel) - 120))
        if vault and sel and (how == "목차" or len(sel) > 3):
            out.append("  ➡ 본문(볼트 원문)은 3 항 이하로 고르면 함께 나온다 — 예 get_execution_standard("
                       "law_name=\"%s\", number=\"%s\")" % (bname.replace(" 집행기준", ""),
                                                            _nts_clean(sel[0].get("ntstTextNm")).split()[0]))
        if pdf:
            out.append("  본문 PDF(%s년 판 한 권): %s" % (yr, pdf))
        out.append("")
    if used:
        out.append("※ 본문은 볼트 J- 노트의 「원문」 이다 — 국세청 집행기준 PDF 글자층을 쪽 그림과 대조해 옮긴 정본(NAS 볼트 · 읽기만). "
                   "볼트 표지 · 볼트 현행 확인 · 볼트 주의는 원문이 아니다. 집행기준은 법 개정을 못 따라오니 근거 조문의 "
                   "현행과 대조하세요. 목차 출처: 국세법령정보시스템(공식 API 아님)")
    else:
        out.append("※ 집행기준 본문은 국세법령정보시스템이 연도별 PDF 로만 준다 — 위 쪽 번호로 PDF 에서 보세요. 볼트에 있는 "
                   "11권은 3 항 이하로 고르면 볼트 원문도 함께 낸다(NAS 가 닿는 PC). 출처: 국세법령정보시스템(공식 API 아님)")
    return cap("\n".join(out), MAX_TEXT)


# ---- F9 국세청 해석 검색 · v2.13 판례 · 결정례 검색(국세법령정보시스템 통합검색) ---------------------
#  쪽 넘김(2026-10-26 실측): sortField 를 사이트 기본값 SCORE/DESC 로 줘야 startCount(글 위치)가 먹는다. 그 전에 쓰던 RANK 는
#  첫 쪽만 오고 startCount>0 이면 0건이었다(해석 · 판례 묶음 모두 — 쿠키 · wnKey 는 상관없었다). 첫 쪽 차례는 둘이 같다(찾을 말
#  여섯 가지 대조). 한 쪽은 10건이 끝이다(viewCount 30 → 10건). 찾을 말에 따라 둘째 쪽부터 0건으로 오는 때가 있다
#  (실측 '해산 결손금 소급공제' 해석 묶음 — 총 39건이라 하고 둘째 쪽 0건) — 사이트 엔진 사정이라 그대로 알린다.
#  날짜순은 내지 않는다 — 화면의 정렬 값(DCM_RGT_DTM/DESC · FRS_RGT_DTM/DESC 등 다섯)을 보내도 차례가 그대로였다(10-26).
_NTS_VIEW_MAX = 10


def _nts_search(q, collection, a):
    """통합검색 한 쪽(정확도순) → (총 건수, 줄 목록, 쪽, 쪽 크기). 실패하면 예외(사유 담음)."""
    try:
        disp = max(1, min(_NTS_VIEW_MAX, int(a.get("display") or 10)))
        page = max(1, int(a.get("page") or 1))
    except (TypeError, ValueError):
        disp, page = 10, 1
    node = _taxlaw_action("ASEISA001MR01", {
        "schVcb": q, "collection": collection, "startCount": (page - 1) * disp, "viewCount": disp,
        "searchType": "", "sortField": "SCORE/DESC"}, "/is/USEISA001M.do", ttl=3600)
    col = ((node.get("searchResultVO") or {}).get("collectionList") or [{}])[0]
    return col.get("totalCount") or 0, col.get("resultList") or [], page, disp


def _nts_empty_page(what, q, total, page):
    return ("[이 쪽 없음] %s '%s' — 총 %s건이라 했지만 %d쪽은 비어 왔습니다.\n"
            "국세법령정보시스템 검색 엔진이 찾을 말에 따라 앞쪽만 주는 때가 있습니다. 찾을 말을 줄이거나 바꿔 보세요."
            % (what, q, total, page))


def tool_search_nts_rulings(a):
    q = str(a.get("query") or "").strip()
    if not q:
        return "[입력 오류] query(찾을 말 · 문서번호 — 예 '재산세제과-35', '1세대 1주택 거주기간')가 필요합니다."
    try:
        total, rows, page, disp = _nts_search(q, "question", a)
    except Exception as e:
        return "[조회 실패] 국세법령정보시스템 검색을 하지 못했습니다 — %s" % mask(str(e))[:140]
    if not rows:
        if page > 1 and total:
            return _nts_empty_page("국세청 · 기재부 해석", q, total, page)
        return ("[검색결과 없음] 국세청 · 기재부 해석 '%s' (총 %s건)\n\n"
                "다시 찾을 때는 문서번호(예 '재산세제과-35')나 더 짧은 말로 찾아보세요.\n"
                "그래도 없으면 예규 · 해석의 문서번호나 내용을 추측해서 채우지 말고, 못 찾았다고 그대로 전하세요."
                % (q, total))
    out = ["국세청·기재부 해석 검색(국세법령정보시스템) '%s' — 총 %s건 · 이 쪽 %d건(%d쪽)" % (q, total, len(rows), page), ""]
    for x in rows:
        did = _num_id(x.get("DOC_ID"))
        out.append("[%s] %s" % (did, _nts_clean(x.get("TTL"))))
        out.append("   문서번호: %s · 생산일자: %s · %s · %s" % (
            _nts_clean(x.get("NTST_DCM_DSCM_CNTN")) or "?", _fmt_d(x.get("DCM_RGT_DTM_S") or str(x.get("NTST_DCM_RGT_DT") or "")[:8]),
            _nts_clean(x.get("LBL1_TTL")) or "?", _nts_clean(x.get("NTST_TLAW_CL_NM")) or "?"))
        gist = _nts_clean(x.get("GIST_CNTN"))
        if gist:
            out.append("   요지: %s" % cap(gist, 160))
        out.append("")
    first = _num_id(rows[0].get("DOC_ID"))
    out.append("➡ 전문 조회:  get_tax_interpretation(id=\"%s\")  (국세법령정보시스템 문서ID 그대로)" % first)
    if page * disp < total:
        out.append("   다음 쪽: search_nts_rulings(query=\"%s\", page=%d)" % (q, page + 1))
    out.append("   법제처 목록에 없는 해석(예: 기재부 재산세제과-35 2021.1.14.)도 여기서 나옵니다. 출처: 국세법령정보시스템(공식 API 아님)")
    out.append("   판결 · 조세심판 · 이의신청 · 심사 결정례는 search_nts_precedents 로 찾습니다.")
    return cap("\n".join(out), MAX_TEXT)


def tool_search_nts_precedents(a):
    """국세법령정보시스템 판례 · 결정례 검색(v2.13 — 노트북 세무자문 좌석 10-25 요청서 1 · 3)."""
    q = str(a.get("query") or "").strip()
    if not q:
        return ("[입력 오류] query(찾을 말 · 사건번호 — 예 '평가심의위원회 비상장주식', '2019서4288', '2022두42020')가 "
                "필요합니다.")
    try:
        total, rows, page, disp = _nts_search(q, "precedent", a)
    except Exception as e:
        return "[조회 실패] 국세법령정보시스템 판례 · 결정례 검색을 하지 못했습니다 — %s" % mask(str(e))[:140]
    if not rows:
        if page > 1 and total:
            return _nts_empty_page("판례 · 결정례", q, total, page)
        return ("[검색결과 없음] 국세법령정보시스템 판례 · 결정례 '%s' (총 %s건)\n\n"
                "다시 찾을 때는 더 짧은 말이나 사건번호(예 '2019서4288' · '2022두42020')로 찾아보세요.\n"
                "그래도 없으면 판결 · 결정의 사건번호나 내용을 추측해서 채우지 말고, 못 찾았다고 그대로 전하세요."
                % (q, total))
    out = ["국세법령정보시스템 판례 · 결정례 검색 '%s' — 총 %s건 · 이 쪽 %d건(%d쪽 · 정확도순)" % (q, total, len(rows), page), ""]
    for x in rows:
        res = _nts_outcome(x.get("NTST_DCM_DCS_CL_CD"), x.get("NTST_DCM_DCS_CL_NM"))
        out.append("[%s] %s · %s · %s%s · %s" % (
            _num_id(x.get("DOC_ID")), _nts_clean(x.get("NTST_DCM_DSCM_CNTN")) or "?",
            _fmt_d(x.get("DCM_RGT_DTM_S") or str(x.get("NTST_DCM_RGT_DT") or "")[:8]),
            _nts_clean(x.get("LBL1_TTL")) or _nts_clean(x.get("NTST_DCM_CL_NM")) or "?",
            (" · 결과 " + res) if res else "", _nts_clean(x.get("NTST_TLAW_CL_NM")) or "?"))
        out.append("   제목: %s" % (_nts_clean(x.get("TTL")) or "?"))
        gist = _nts_clean(x.get("GIST_CNTN"))
        if gist:
            out.append("   요지: %s" % cap(gist, 160))
        out.append("")
    first = _num_id(rows[0].get("DOC_ID"))
    out.append("➡ 본문:  get_tax_interpretation(id=\"%s\")  — 긴 판결 · 결정은 offset 으로 넘기거나 "
               "find=\"판단\" 으로 판단 부분부터" % first)
    if page * disp < total:
        out.append("   다음 쪽: search_nts_precedents(query=\"%s\", page=%d)" % (q, page + 1))
    out.append("   출처: 국세법령정보시스템(공식 API 아님) — 법원 판결 · 조세심판 · 이의신청 · 심사 · 과세전적부심사. "
               "결과는 국세청이 붙인 구분(국승 · 국패 · 기각 · 인용 …)이다.")
    return cap("\n".join(out), MAX_TEXT)


DISPATCH = {
    "search_precedents": tool_search_precedents,
    "get_precedent": tool_get_precedent,
    "search_tax_tribunal": tool_search_tax_tribunal,
    "get_tax_tribunal": tool_get_tax_tribunal,
    "search_interpretations": tool_search_interpretations,
    "get_interpretation": tool_get_interpretation,
    "search_law": tool_search_law,
    "get_law_article": tool_get_law_article,
    "get_law_appendix": tool_get_law_appendix,
    "get_law_addenda": tool_get_law_addenda,
    "list_law_history": tool_list_law_history,
    "search_admin_rule": tool_search_admin_rule,
    "get_admin_rule": tool_get_admin_rule,
    "verify_citation": tool_verify_citation,
    "search_constitutional": tool_search_constitutional,
    "get_constitutional": tool_get_constitutional,
    "search_admin_appeal": tool_search_admin_appeal,
    "get_admin_appeal": tool_get_admin_appeal,
    "search_ordinance": tool_search_ordinance,
    "get_ordinance": tool_get_ordinance,
    "search_english_law": tool_search_english_law,
    "get_english_law": tool_get_english_law,
    "get_law_structure": tool_get_law_structure,
    "search_law_appendix": tool_search_law_appendix,
    "search_tax_interpretation": tool_search_tax_interpretation,
    "get_tax_interpretation": tool_get_tax_interpretation,
    "verify_citations": tool_verify_citations,
    "law_as_of": tool_law_as_of,
    "list_annexes": tool_list_annexes,
    "get_annex": tool_get_annex,
    "compare_versions": tool_compare_versions,
    "article_history": tool_article_history,
    "get_basic_rule": tool_get_basic_rule,
    "get_execution_standard": tool_get_execution_standard,
    "search_nts_rulings": tool_search_nts_rulings,
    "search_nts_precedents": tool_search_nts_precedents,
}


# =============================================================================
# 도구 스키마 (tools/list 응답)
# =============================================================================
def _schema(props, required):
    return {"type": "object", "properties": props, "required": required}


_DATE = {"type": "string", "description": "YYYYMMDD"}
_DISPLAY = {"type": "integer",
            "description": "결과 수(기본 %d, 최대 %d)" % (DEFAULT_DISPLAY, MAX_DISPLAY)}
_PAGE = {"type": "integer", "description": "페이지(기본 1)"}
_SORT = {"type": "string", "enum": ["lasc", "ldes", "dasc", "ddes", "nasc", "ndes"],
         "description": "정렬: dasc/ddes=날짜오름/내림, lasc/ldes=명칭, nasc/ndes=번호"}

TOOLS_SCHEMA = [
    {"name": "search_precedents",
     "description": "법원 판례 검색(국가법령정보센터·법제처 공식 API). 키워드로 대법원/하급심 판례 목록을 조회. 결과의 id 로 get_precedent 호출하여 전문 확인. 여러 키워드는 AND 조건이므로 핵심어 1~2개 권장.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '명의신탁 증여', '저가양수 부당행위')"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=판례명 검색(기본), 2=본문 검색"},
         "from_date": _DATE, "to_date": _DATE,
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_precedent",
     "description": "판례 전문 조회(판시사항·판결요지·참조조문·참조판례·판례내용). id 는 search_precedents 결과의 판례일련번호. 데이터출처명이 '국세법령정보시스템'인 항목은 법제처가 본문을 주지 않는다 — 그때는 같은 사건을 국세법령정보시스템에서 찾아 문서ID 와 get_tax_interpretation 길을 알려 준다(case_no 를 주면 확실).",
     "inputSchema": _schema({
         "id": {"type": "string", "description": "판례일련번호"},
         "case_name": {"type": "string", "description": "판례명(선택) — 공식 변수 LM 으로 넘긴다"},
         "case_no": {"type": "string", "description": "사건번호(선택 — 예 '2022두42020', '대법원-2022-두-42020'). 본문이 없을 때 국세법령정보시스템에서 같은 사건을 찾는 데 쓴다"},
     }, ["id"])},
    {"name": "search_tax_tribunal",
     "description": "조세심판원 심판례(특별행정심판 재결례) 검색. 국세·지방세 불복 사건의 재결례를 키워드로 조회. 결과 id 로 get_tax_tribunal 호출.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '부가가치세 매입세액', '비상장주식 저가양도')"},
         "rslYd": {"type": "string", "description": "의결일자 범위 YYYYMMDD~YYYYMMDD"},
         "dpaYd": {"type": "string", "description": "처분일자 범위 YYYYMMDD~YYYYMMDD"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_tax_tribunal",
     "description": "조세심판원 심판례 전문 조회(재결요지·주문·청구취지·이유·관련법령·세목 등). id 는 search_tax_tribunal 결과의 특별행정심판재결례일련번호.",
     "inputSchema": _schema({
         "id": {"type": "string", "description": "특별행정심판재결례일련번호"},
         "decision_name": {"type": "string", "description": "특별행정심판재결례명(선택) — 공식 변수 LM 으로 넘긴다"},
     }, ["id"])},
    {"name": "search_interpretations",
     "description": "법제처 법령해석례 검색(회신기관 대부분 '법제처'). 세법 적용 관련 법제처 유권해석을 키워드로 조회하고 결과 id 로 get_interpretation 호출. ※국세청·기재부 세법해석(질의회신)은 search_tax_interpretation, 국세청 훈령·예규·고시는 search_admin_rule 을 사용할 것.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=해석례명(기본), 2=본문검색"},
         "inq": {"type": "string", "description": "질의기관 코드(선택)"},
         "rpl": {"type": "string", "description": "회신기관 코드(선택)"},
         "explYd": {"type": "string", "description": "해석일자 범위 YYYYMMDD~YYYYMMDD"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_interpretation",
     "description": "법령해석례 전문 조회(질의요지·회답·이유). id 는 search_interpretations 결과의 일련번호.",
     "inputSchema": _schema({"id": {"type": "string", "description": "법령해석례일련번호"}}, ["id"])},
    {"name": "search_law",
     "description": "현행 법령 검색. 법령명으로 검색하여 법령일련번호(MST)를 얻고, get_law_article 로 특정 조문을 조회. 세법 약칭(조특법·상증령·소득칙 등)도 받아 정식 이름으로 풀고, 결과에 약칭을 함께 보여 준다. 이름이 정확히 같은 법령은 맨 앞에 둔다(법제처 목록 차례로는 '상법'이 34번째).",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "법령명(예: '상속세 및 증여세법', '소득세법', 약칭 '조특법')"},
         "display": _DISPLAY, "page": _PAGE,
     }, [])},
    {"name": "get_law_article",
     "description": "법령 조문 전문 조회. mst(법령일련번호, search_law 결과) 또는 law_name(법령 이름 — 약칭 됨, 현행 판) 가운데 하나, jo 로 특정 조문 지정(예: '제35조', '제10조의2', '§38', 또는 '003500'). jo 생략 시 법령 전체. ★과거 시점 조문은 law_as_of(law_name, date, article) 가 가장 간단하고, list_law_history 결과의 mst 와 그 행의 시행일자를 efYd 로 함께 넘겨도 정확하다.",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "법령일련번호(search_law·list_law_history 결과)"},
         "lawId": {"type": "string", "description": "법령ID(대체 입력). ※법령ID 로는 현행 시행본만 조회된다 — 과거본은 mst+efYd"},
         "law_name": {"type": "string", "description": "법령 이름(대체 입력 · 약칭 됨 — 예 '조특법', '상속세및증여세법 시행령'). 현행 판을 본다"},
         "efYd": {"type": "string", "description": "시행일자 YYYYMMDD — 과거·시행예정본 조회 시 list_law_history 의 그 행 시행일자를 그대로"},
         "jo": {"type": "string", "description": "조문(예: '제35조', '제10조의2', '§38', 또는 6자리 '003500')"},
         "article": {"type": "string", "description": "jo 와 같음(둘 중 하나)"},
     }, [])},
    {"name": "list_law_history",
     "description": "법령의 시행일별 연혁(개정 이력) 목록 조회. 각 버전의 시행일자와 법령일련번호(MST), 판 상태(★현행 · 연혁 · 시행예정)를 반환한다 — 목록 맨 위는 흔히 아직 시행 전인 시행예정 판이니 현행으로 인용하지 말 것. 원하는 시점의 조문은 get_law_article(mst=그 행 MST, efYd=그 행 시행일자) 로 본다 — efYd 를 함께 넘겨야 정확하다. 날짜 하나로 판·조문·그 뒤 개정·부칙을 한 번에 보려면 law_as_of. 과거 시점 법령 확인(경정청구·과거연도 검토) 시 사용.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "법령명(예: '상속세 및 증여세법', 약칭 '상증법')"},
         "from_date": _DATE, "to_date": _DATE,
         "display": _DISPLAY, "page": _PAGE,
     }, [])},
    {"name": "search_admin_rule",
     "description": "행정규칙(훈령·고시·지침·사무처리규정 등 부처 내부규정) 검색. 국세청만 보려면 org='1210000'. 결과 id 로 get_admin_rule 호출(본문 제공). ※주의: 세무에서 말하는 '국세청 예규=질의회신·해석사례'는 이 도구가 아니라 search_tax_interpretation 을 쓸 것(이 도구의 '예규'는 행정규칙 종류를 의미). 법제처 법령해석례는 search_interpretations.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '법인세 사무처리', '전자세금계산서')"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=행정규칙명(기본), 2=본문검색"},
         "org": {"type": "string", "description": "소관부처 코드. 국세청=1210000 (다른 부처는 결과의 소관부처명 참고)"},
         "knd": {"type": "string", "description": "종류 코드(불확실 — 생략 권장)"},
         "nw": {"type": "integer", "enum": [1, 2], "description": "1=현행(기본) 2=연혁"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_admin_rule",
     "description": "행정규칙 전문 조회(조문내용·별표·발령일자·소관부처 등). id 는 search_admin_rule 결과의 행정규칙일련번호. ※조문이 수백 개인 규정이 많아 전체 조회는 출력 한도에서 잘린다 — 특정 조를 볼 때는 jo 로 좁힐 것.",
     "inputSchema": _schema({
         "id": {"type": "string", "description": "행정규칙일련번호"},
         "ruleName": {"type": "string", "description": "행정규칙명(선택, 검증용)"},
         "jo": {"type": "string", "description": "조문 지정(예: '제12조', '제12조의3'). 생략 시 전체"},
     }, ["id"])},
    {"name": "verify_citation",
     "description": "어시스턴트가 생성한 인용(판례 사건번호·법령 조문·조세심판원 청구번호·법령해석례)이 법제처 공식 API에 '실제로 존재'하는지 검증한다. 정확히 일치하면 표준 메타데이터와 후속 get_* 호출용 일련번호를 반환하고, 없으면 'VERIFIED: false'와 함께 '인용 금지'를 명시한다. 판례·법령·심판례를 인용하기 전에 반드시 이 도구로 검증할 것.",
     "inputSchema": _schema({
         "citation": {"type": "string", "description": "검증할 인용 원문(예: '2017두38249', '상속세 및 증여세법 제35조', '조심2018서1234')"},
         "kind": {"type": "string",
                  "enum": ["precedent", "law_article", "tax_tribunal", "interpretation", "constitutional", "auto"],
                  "description": "종류 힌트(기본 auto=자동판별). constitutional=헌재결정례"},
         "case_no": {"type": "string", "description": "판례 사건번호(직접 지정)"},
         "law_name": {"type": "string", "description": "법령명(직접 지정)"},
         "article": {"type": "string", "description": "조문(예: 제35조)"},
         "claim_no": {"type": "string", "description": "조세심판 청구번호(직접 지정)"},
     }, [])},
    {"name": "search_constitutional",
     "description": "헌법재판소 결정례 검색. 세법 위헌·헌법불합치 결정(종부세·상속증여세 합산과세·가산세 등)을 키워드로 조회. 결과 id 로 get_constitutional 호출.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '종합부동산세', '재산세 위헌')"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=결정례명(기본), 2=본문검색"},
         "edYd": {"type": "string", "description": "종국일자 범위 YYYYMMDD~YYYYMMDD"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_constitutional",
     "description": "헌재 결정례 전문 조회(판시사항·결정요지·심판대상조문·참조조문). id 는 search_constitutional 결과의 헌재결정례일련번호.",
     "inputSchema": _schema({"id": {"type": "string", "description": "헌재결정례일련번호"}}, ["id"])},
    {"name": "search_admin_appeal",
     "description": "행정심판 재결례 검색(국민권익위 중앙행정심판위 등). 지방세·행정처분 불복 재결례를 키워드로 조회. 결과 id 로 get_admin_appeal 호출.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '취득세', '재산세 부과')"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=재결례명(기본), 2=본문검색"},
         "rslYd": {"type": "string", "description": "의결일자 범위 YYYYMMDD~YYYYMMDD"},
         "dpaYd": {"type": "string", "description": "처분일자 범위 YYYYMMDD~YYYYMMDD"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_admin_appeal",
     "description": "행정심판 재결례 전문 조회(주문·청구취지·이유·재결요지·처분청·재결청). id 는 search_admin_appeal 결과의 행정심판재결례일련번호.",
     "inputSchema": _schema({"id": {"type": "string", "description": "행정심판재결례일련번호"}}, ["id"])},
    {"name": "search_ordinance",
     "description": "자치법규(조례·규칙) 검색. 지방세 감면조례·세율조례 등 지자체 법규를 키워드로 조회. 지자체는 org(시·도)/sborg(시·군·구) 코드로 필터. 결과 id(MST) 로 get_ordinance 호출.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '지방세 감면', '세율')"},
         "org": {"type": "string", "description": "시·도 코드(선택)"},
         "sborg": {"type": "string", "description": "시·군·구 코드(선택)"},
         "knd": {"type": "string", "description": "종류: 30001=조례, 30002=규칙"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_ordinance",
     "description": "자치법규 전문 조회. mst(자치법규일련번호, search_ordinance 결과) 필수, jo 를 주면 그 조문 하나만(선택).",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "자치법규일련번호(search_ordinance 결과)"},
         "id": {"type": "string", "description": "자치법규일련번호(mst 대체 입력)"},
         "jo": {"type": "string", "description": "조문(예: '제20조', '제6조의2') — 전문을 받아 그 조만 골라낸다(법제처 자치법규 조회에는 조문 지정 변수가 없음)"},
     }, [])},
    {"name": "search_english_law",
     "description": "영문법령 검색. 한국 세법(소득세법·법인세법 등)의 공식 영문본을 조회(외국인투자·조세조약 자문용). 결과 id(MST) 로 get_english_law 호출.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "법령명(한글 또는 영문, 예: 'Income Tax', '소득세법')"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_english_law",
     "description": "영문법령 전문 조회(공식 영문 조문). mst 는 search_english_law 결과의 법령일련번호.",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "법령일련번호(search_english_law 결과)"},
         "id": {"type": "string", "description": "법령일련번호(mst 대체 입력)"},
     }, [])},
    {"name": "get_law_structure",
     "description": "법령 체계도 조회 — 해당 법령의 시행령·시행규칙 및 관련 법령을 법령명+MST 로 반환. 반환된 MST 로 get_law_article 을 호출해 시행령/규칙 조문을 조회. (법-시행령-시행규칙 3단 연계 분석에 사용.)",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "법령일련번호(search_law 결과)"},
         "id": {"type": "string", "description": "법령일련번호(mst 대체 입력)"},
     }, [])},
    {"name": "search_law_appendix",
     "description": "별표·서식을 '제목/키워드'로 검색(target=licbyl) — 파일/PDF 링크 제공. ※주의: 검색 대상은 별표의 '제목'이라 '법령명'으로는 0건이 나온다(예: '수도권정비계획법'✗ → '과밀억제권역'✓). 특정 법령의 모든 별표를 보려면 get_law_appendix(mst) 를 쓸 것.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "별표 제목/내용 키워드(예: '과밀억제권역','세액공제'). 법령명 아님."},
         "knd": {"type": "string", "description": "종류 필터(선택, 코드 체계 불확실 — 생략 시 전체)"},
         "display": _DISPLAY, "page": _PAGE,
     }, [])},
    {"name": "get_law_appendix",
     "description": "법령의 별표 '본문'을 텍스트로 조회. 조문이 '…별표 N과 같다'로 끝나 내용이 안 보일 때, mst(법령일련번호)와 byl(별표번호)로 그 별표의 실제 표·목록을 가져온다(예: 수도권정비계획법 시행령 과밀억제권역 범위 = 별표 1). byl 생략 시 그 법령의 모든 별표. 원본 PDF/HWP 링크도 함께 제공.",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "법령일련번호(search_law 결과). 시행령/시행규칙의 mst 일 수 있음"},
         "lawId": {"type": "string", "description": "법령ID(대체 입력)"},
         "byl": {"type": "string", "description": "별표번호(예: '1', '제1호'). 생략 시 전체 별표"},
     }, [])},
    {"name": "get_law_addenda",
     "description": "법령 부칙(附則) 조회 — 개정규정의 '시행일 단서'·'적용례'·'경과조치' 원문. 부칙은 현행본에 역대 공포번호별로 누적 수록되므로 연혁본 MST 가 필요 없다: mst=현행본 MST + no=공포번호(list_law_history 로 확인)가 정석. 특정 조문의 시행시기를 찾을 땐 query='제95조의2' 처럼 본문 검색(최신 3건 반환). 둘 다 생략 시 최신 부칙.",
     "inputSchema": _schema({
         "mst": {"type": "string", "description": "법령일련번호 — '현행본' MST 권장(search_law 결과)"},
         "lawId": {"type": "string", "description": "법령ID(대체 입력)"},
         "no": {"type": "string", "description": "공포번호(예: '21223') — 특정 개정의 부칙 지정"},
         "query": {"type": "string", "description": "부칙 본문 키워드(예: '제95조의2', '월세') — 포함 부칙 최신 3건"},
     }, [])},
    {"name": "search_tax_interpretation",
     "description": "★국세청 '예규'·질의회신·서면질의·해석사례·사전답변(및 기재부·관세청 세법해석)을 찾을 때 가장 먼저 쓰는 도구. 법제처 법령해석례(expc)·행정규칙(admrul)과 별개의 과세관청 유권해석 — 세무자문에서 가장 직접적인 근거. 전문까지 보려면 결과의 '법령해석상세링크' 안에 있는 ntstDcmId(18자리)를 get_tax_interpretation(id=…, 동일 source) 에 넘길 것(응답 하단 힌트가 그 형태로 나온다). 관세청은 법제처 일련번호를 그대로 쓴다.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "검색 키워드(예: '1세대 1주택', '양도소득세 비과세')"},
         "source": {"type": "string", "enum": ["nts", "moef", "customs"],
                    "description": "기관: nts=국세청(기본), moef=기획재정부, customs=관세청"},
         "search": {"type": "integer", "enum": [1, 2], "description": "1=해석명(기본), 2=본문검색"},
         "explYd": {"type": "string", "description": "해석일자 범위 YYYYMMDD~YYYYMMDD"},
         "display": _DISPLAY, "page": _PAGE, "sort": _SORT,
     }, [])},
    {"name": "get_tax_interpretation",
     "description": "세법해석 전문(요지·회신·본문) 조회. id 는 두 가지를 받는다 — ①국세법령정보시스템 문서ID(ntstDcmId · 18자리 숫자): 국세청·기획재정부 해석(search_tax_interpretation 의 '법령해석상세링크' · search_nts_rulings 결과)과 판례·결정례(search_nts_precedents 결과 — 법원 판결 · 조세심판 · 이의신청 · 심사 · 과세전적부심사, 결과 구분 국승·기각 등을 머리에 적음). 법제처 API 는 이들의 본문을 주지 않으므로 국세법령정보시스템에서 가져온다(공식 API 아님 — 출처 표기 포함). ②관세청(customs): 법제처 일련번호. 긴 본문은 잘라 버리지 않고 끝에 다음 쪽 offset 을 알린다 — offset 으로 이어 보거나 find='판단'(또는 '주문'·'이유')으로 그 머리 줄부터 본다.",
     "inputSchema": _schema({
         "id": {"type": "string",
                "description": "nts·moef·판례·결정례: ntstDcmId(18자리) / customs: 법령해석일련번호"},
         "source": {"type": "string", "enum": ["nts", "moef", "customs"],
                    "description": "기관: nts=국세청(기본), moef=기획재정부, customs=관세청"},
         "offset": {"type": "integer", "description": "본문 시작 글자 위치(기본 0) — 앞 쪽 끝의 안내 숫자를 그대로"},
         "find": {"type": "string", "description": "이 말이 든 머리 줄부터(예 '판단', '주문', '이유', '사실관계')"},
     }, ["id"])},
    {"name": "verify_citations",
     "description": "글 속 법령 인용을 모두 뽑아 실제로 있는지·조문 제목이 맞는지 한 번에 검증한다(원고·노트 교정, 상담 답변 검토). '법령명 제N조(의M) [제N항] [제N호]'·'조특법 §104의5①3'·「상속세 및 증여세법」 제18조의2 꼴, 약칭(조특법·상증령…), 「같은 법」·「동법 시행령」·「법」·「영」, 열거(제1조ㆍ제3조)·범위(제10조부터 제13조까지)를 푼다. 상태: ✓ 있음(조문 제목) · ✗ 없음(그 판 조문 범위) · ⌛ 삭제(시행예정 판에 있으면 따로 알림) · ⊘ 법령 폐지 · ⚠ 확인 필요. date 를 주면 그날 시행 판으로 본다.",
     "inputSchema": _schema({
         "text": {"type": "string", "description": "인용이 든 글(text·citations 가운데 하나는 필수)"},
         "citations": {"type": "array", "items": {"type": "string"},
                       "description": "'법령명|제N조(의M)' 꼴 목록(볼트 근거조문 칸 그대로)"},
         "date": {"type": "string", "description": "기준일(YYYY-MM-DD·YYYYMMDD·YYYY.MM.DD). 없으면 현행"},
         "max": {"type": "integer", "description": "볼 인용 수 한도(기본 30, 최대 200)"},
     }, [])},
    {"name": "law_as_of",
     "description": "행위시법 한 번에 — 날짜 하나로 그날 시행 판(시행일·공포번호·MST) + 조문 본문 + 그 뒤 개정 수·현행 판·시행예정 + 그 조문을 말하는 부칙(적용례·경과조치) 발췌를 함께 본다. 약칭 됨. 제명이 바뀐 법령도 법령ID 로 옛 이름 시절 판까지 잇는다. 같은 시행일 판이 여럿이면 가장 늦게 공포된 판. (list_law_history → get_law_article(efYd) → get_law_addenda 세 번을 한 번에)",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨 — 예 '조특법', '상속세 및 증여세법')"},
         "date": {"type": "string", "description": "기준일(YYYY-MM-DD·YYYYMMDD·YYYY.MM.DD)"},
         "article": {"type": "string", "description": "조문(선택 — 예 '제18조의2', '§100의32')"},
     }, ["law_name", "date"])},
    {"name": "list_annexes",
     "description": "법령의 별표·서식 목록(번호·제목·개정 표시·글 분량·파일 형식). date 를 주면 그날 시행 판의 별표. 약칭 됨. 한 건은 get_annex 로.",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨 — 예 '소득령', '상속세 및 증여세법 시행령')"},
         "date": {"type": "string", "description": "기준일(선택). 없으면 현행"},
         "kind": {"type": "string", "enum": ["전체", "별표", "서식"], "description": "갈래(기본 전체)"},
     }, ["law_name"])},
    {"name": "get_annex",
     "description": "별표·서식 한 건의 글·표(세율표·업종표·간이세액표 등). annex_no(번호) 또는 query(제목 낱말)로 고른다. 표 그림 줄을 빼고 칸을 ' | ' 로 줄여 보여 주며, 긴 표는 page 로 넘기거나 find 로 필요한 줄만(예 월급여 '3,000') 뽑는다. date 를 주면 그날 시행 판. 글이 없는 그림·파일 별표는 원문 파일 링크를 알린다.",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨)"},
         "annex_no": {"type": "string", "description": "별표(서식) 번호 — 예 '2', '2의2'"},
         "query": {"type": "string", "description": "제목 낱말(번호 대신 — 예 '가업상속', '간이세액')"},
         "kind": {"type": "string", "enum": ["별표", "서식", "전체"], "description": "갈래(기본 별표)"},
         "date": {"type": "string", "description": "기준일(선택). 없으면 현행"},
         "page": {"type": "integer", "description": "긴 별표의 쪽(기본 1)"},
         "find": {"type": "string", "description": "이 글이 든 줄만(예 '3,000' — 여럿이면 ';' 로: '3,000;3,500'). 숫자는 숫자 단위로 맞춘다('3,000' 은 53,000·3,000,000 에 걸리지 않음) — 앞자리로 찾으려면 끝에 *('3,0*')"},
     }, ["law_name"])},
    {"name": "compare_versions",
     "description": "신구 조문 대조 — 두 판의 같은 조문을 맞대어 바뀐 줄을 보여 준다(− 옛 · + 새 · 다른 글자 ⟦ ⟧). 판은 날짜(그날 시행 판)·'현행'·'MST 257993'·'제19936호'(공포번호)로 준다. to 를 빼면 현행과 맞댐. 표는 칸 글자 기준으로 맞대어 표 그림(칸 너비) 때문에 생기는 헛 바뀜이 없다. 약칭 됨.",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨)"},
         "article": {"type": "string", "description": "조문(예 '제100조의32', '§104의5')"},
         "from": {"type": "string", "description": "옛 판 — 날짜(YYYY-MM-DD 등) · 'MST 257993' · '제19936호'"},
         "to": {"type": "string", "description": "새 판(선택 — 없으면 현행)"},
     }, ["law_name", "article", "from"])},
    {"name": "article_history",
     "description": "조문 연혁 — 한 조문이 언제 신설·개정·삭제됐는지 판마다 한 줄(시행일·공포일·공포번호·제개정 구분·바뀜 갈래). 법제처 조문별 변경 이력. 약칭 됨. 두 판 글 대조는 compare_versions.",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨)"},
         "article": {"type": "string", "description": "조문(예 '제100조의32')"},
     }, ["law_name", "article"])},
    {"name": "get_basic_rule",
     "description": "국세 기본통칙(소득세법·법인세법·상증법·부가세법 등 15개 법) — 국세법령정보시스템에서 통칙 본문을 가져온다(법제처 행정규칙에는 없음). number('1-3…1' 꼴, '1-3-1' 도 됨)·article('제1조' → 그 조 관련 통칙들)·query(찾을 말) 로 고르고, 없으면 목차. year 로 옛 판(2019 등). 공식 API 아님 — 인용 전 원문 대조.",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨 — 예 '소득세법', '상증법')"},
         "number": {"type": "string", "description": "통칙 번호(예 '1-3…1', '1-3-1')"},
         "article": {"type": "string", "description": "법 조문(예 '제1조') — 그 조 관련 통칙"},
         "query": {"type": "string", "description": "찾을 말(제목·본문)"},
         "year": {"type": "string", "description": "판 연도(예 '2019') — 없으면 최신"},
     }, ["law_name"])},
    {"name": "get_execution_standard",
     "description": "세법집행기준(국세청) — 목차(번호 '88-0-2' · '88-152의3-1' · 제목 · PDF 쪽)와 본문. number·article·query 로 3 항 이하를 고르면 NAS 볼트 J- 노트의 「원문」(국세청 PDF 를 쪽 그림과 대조해 옮긴 정본 · 2024.10 판)을 함께 낸다 — 11권(국세기본법 · 국세징수법 · 법인세 · 종합소득세 · 상속증여세 · 부가가치세 · 조특법 · 개별소비세 · 인지세 · 주세 · 주류면허법), NAS 가 닿는 PC. 볼트에 없는 책(양도소득세 · 국제조세 · 종합부동산세 · 증권거래세)이나 NAS 가 안 닿으면 목차 · PDF 쪽 · PDF 링크. 볼트 표지 · 주의는 원문과 갈라 적는다. law_name 은 법령 이름(소득세법 → 종합소득세 · 양도소득세 두 권)이나 책 이름. 목차는 국세법령정보시스템(공식 API 아님).",
     "inputSchema": _schema({
         "law_name": {"type": "string", "description": "법령 이름(약칭 됨) 또는 책 이름('양도소득세', '상속증여세')"},
         "number": {"type": "string", "description": "집행기준 번호(예 '88-0-2', '88-152의3-1', '47의2-0-1')"},
         "article": {"type": "string", "description": "법 조문(예 '제88조', '제18조의2') — 그 조 관련 집행기준"},
         "query": {"type": "string", "description": "찾을 말(제목)"},
         "year": {"type": "string", "description": "판 연도(예 '2022') — 없으면 최신"},
     }, ["law_name"])},
    {"name": "search_nts_rulings",
     "description": "국세청·기재부 해석(질의회신·서면·사전답변 등)을 국세법령정보시스템 통합검색으로 찾는다 — 법제처 목록(search_tax_interpretation)에 빠진 해석도 나온다(예: 기재부 재산세제과-35 2021.1.14.). 문서번호·생산일자·갈래·세목·요지를 보이고, 결과 [문서ID] 를 get_tax_interpretation(id) 에 넘기면 전문. 판결·결정례는 search_nts_precedents. 공식 API 아님.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "찾을 말 또는 문서번호(예 '재산세제과-35', '1세대 1주택 거주기간')"},
         "display": {"type": "integer", "description": "한 쪽 결과 수(기본 10, 최대 10 — 사이트 한도)"},
         "page": _PAGE,
     }, ["query"])},
    {"name": "search_nts_precedents",
     "description": "국세법령정보시스템의 판례·결정례를 낱말이나 사건번호로 찾는다 — 법원 판결(대법원·고등법원·행정법원·지방법원) · 조세심판원 결정(조심-…) · 지방국세청 이의신청(이의-…) · 국세청 심사(심사-…) · 과세전적부심사(적부-…). 법제처 판례 목록(search_precedents)에 없거나 본문이 없는 조세 판결도 나온다. 줄마다 [문서ID] · 문서번호 · 선고·결정일 · 갈래 · 결과 구분(국승·국패·일부국패·기각·인용·일부인용·경정·재조사 …) · 세목 · 제목 · 요지. [문서ID] 를 get_tax_interpretation(id) 에 넘기면 본문(긴 판결은 offset·find 로 끝까지). 공식 API 아님.",
     "inputSchema": _schema({
         "query": {"type": "string", "description": "찾을 말 또는 사건번호(예 '평가심의위원회 비상장주식', '2019서4288', '2022두42020')"},
         "display": {"type": "integer", "description": "한 쪽 결과 수(기본 10, 최대 10 — 사이트 한도). 정확도순"},
         "page": _PAGE,
     }, ["query"])},
]


# =============================================================================
# MCP stdio (JSON-RPC 2.0, 개행 구분)
# =============================================================================
def send(msg):
    """stdout 으로 JSON-RPC 응답 1줄 전송. 워커 스레드와 메인이 동시 기록해도
    프레이밍이 깨지지 않도록 락으로 직렬화. 종료 경합(stdout 닫힘)은 조용히 폐기."""
    data = json.dumps(msg, ensure_ascii=False) + "\n"
    with _stdout_lock:
        try:
            sys.stdout.write(data)
            sys.stdout.flush()
        except (BrokenPipeError, ValueError, OSError):
            pass   # 클라이언트가 먼저 stdout 을 닫은 경우 — 응답 보낼 곳 없음


def handle(req):
    mid = req.get("id")
    method = req.get("method")
    params = req.get("params") or {}

    if method == "initialize":
        send({"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": params.get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }})
    elif method in ("notifications/initialized", "initialized"):
        return
    elif method == "ping":
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
    elif method == "tools/list":
        tools = TOOLS_SCHEMA if ALLOWED_TOOLS is None else [
            t for t in TOOLS_SCHEMA if t.get("name") in ALLOWED_TOOLS]
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": tools}})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if SERVICE_NOTICE:   # 교육용 만료 등 — 모든 호출에 안내문만 반환(빨간 에러 아님)
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": SERVICE_NOTICE}]}})
            return
        fn = DISPATCH.get(name)
        if not fn:
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "[오류] 알 수 없는 도구: %s" % name}],
                "isError": True}})
            return
        if ALLOWED_TOOLS is not None and name not in ALLOWED_TOOLS:
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "[안내] 이 배포판에서는 제공하지 않는 도구입니다: %s" % name}],
                "isError": True}})
            return
        try:
            text = fn(args)
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": text}]}})
        except Exception as e:
            LOG.exception("도구 %s 실패: %s", name, e)
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "[오류] %s: %s" % (name, e)}],
                "isError": True}})
    elif mid is not None:
        send({"jsonrpc": "2.0", "id": mid,
              "error": {"code": -32601, "message": "Method not found: %s" % method}})


def _safe_handle(req):
    """워커 스레드에서 tools/call 처리. 어떤 예외도 루프/프로세스를 죽이지 않게
    백스톱으로 잡아 traceback 을 로깅하고 JSON-RPC 오류로 응답."""
    try:
        handle(req)
    except Exception as e:
        LOG.exception("worker 처리 오류: %s", e)
        mid = req.get("id")
        if mid is not None:
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "[오류] %s" % e}], "isError": True}})


def run_stdio():
    LOG.info("server start (%s v%s)", SERVER_NAME, SERVER_VERSION)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        # 네트워크를 타는 tools/call 만 워커로 보내고(읽기 루프 비차단),
        # initialize/ping/tools-list 등 즉답 메서드는 인라인 처리해 헬스체크가 막히지 않게 한다.
        if req.get("method") == "tools/call":
            _POOL.submit(_safe_handle, req)
        else:
            try:
                handle(req)
            except Exception as e:
                LOG.exception("inline 처리 오류: %s", e)
    # EOF: 클라이언트가 stdin 을 닫음 — 대기 중 작업을 취소해 종료 지연(atexit join) 최소화
    try:
        _POOL.shutdown(wait=False, cancel_futures=True)
    except TypeError:                  # Python 3.8 호환(cancel_futures 미지원)
        _POOL.shutdown(wait=False)
    LOG.info("server stop (stdin EOF)")


# =============================================================================
# CLI (자체 점검)
# =============================================================================
def run_selftest(oc):
    if oc:
        os.environ["LAW_OC"] = oc
    _oc = os.environ.get("LAW_OC") or ""
    print("== 자체 점검: 법제처 OC =", ("설정됨(%d자)" % len(_oc)) if _oc else "(미설정)")
    try:
        get_oc()
    except Exception as e:
        print("FAIL:", e)
        return 1
    ok = True
    for label, fn, args in [
        ("판례 검색('양도소득세')", tool_search_precedents, {"query": "양도소득세", "display": 2}),
        ("조세심판원 심판례 검색('부가가치세')", tool_search_tax_tribunal, {"query": "부가가치세", "display": 2}),
        ("행정규칙 검색(국세청 'org=1210000')", tool_search_admin_rule,
         {"query": "법인세", "org": "1210000", "display": 2}),
        ("인용검증(실존 법령조문 → true)", tool_verify_citation, {"citation": "상속세 및 증여세법 제35조"}),
        ("인용검증(허위 사건번호 → false)", tool_verify_citation, {"citation": "2099두99999"}),
        ("헌재결정례 검색('종합부동산세')", tool_search_constitutional, {"query": "종합부동산세", "display": 2}),
        ("자치법규 검색('지방세 감면')", tool_search_ordinance, {"query": "지방세 감면", "display": 2}),
        ("법령 연혁('상속세 및 증여세법' 2020년)", tool_list_law_history,
         {"query": "상속세 및 증여세법", "from_date": "20200101", "to_date": "20201231", "display": 2}),
        ("판례 전문 미제공 안내(국세청 출처 ID)", tool_get_precedent, {"id": "347462"}),
        ("인용검증(헌재 사건번호 2022헌바189 → true)", tool_verify_citation, {"citation": "2022헌바189"}),
        ("별표·서식 검색('소득세법')", tool_search_law_appendix, {"query": "소득세법", "display": 2}),
        ("국세청 세법해석 검색('1세대 1주택')", tool_search_tax_interpretation,
         {"query": "1세대 1주택", "source": "nts", "display": 2}),
    ]:
        print("\n--- %s ---" % label)
        try:
            print(cap(fn(args), 800))
        except Exception as e:
            ok = False
            print("FAIL:", e)
    print("\n== 결과:", "OK" if ok else "일부 실패", "==")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if "--list-tools" in args:
        for t in TOOLS_SCHEMA:
            print(t["name"], "-", t["description"][:70])
        return 0
    if "--selftest" in args:
        oc = None
        if "--oc" in args:
            i = args.index("--oc")
            if i + 1 < len(args):
                oc = args[i + 1]
        return run_selftest(oc)
    run_stdio()
    return 0


if __name__ == "__main__":
    sys.exit(main())
