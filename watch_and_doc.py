"""
b51-coder pane의 transcript.jsonl을 모니터링하여,
새로운 학습 질문/답변이 감지되면 자동으로 study/docs/에 문서를 생성하고,
'질문마다 1개씩' git commit을 자동으로 수행하는 데몬.
LLM API를 호출하지 않는 순수 로컬 파이썬 프로세스이므로 토큰 소모가 0개입니다.
"""

from __future__ import annotations
import json
import os
import re
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(SCRIPT_DIR, "docs")
CURSOR_FILE = os.path.join(DOCS_DIR, ".watcher_cursor.json")


def get_agent_conversation_id(agent_name="b51-coder"):
    herdr_bin = os.environ.get("HERDR_BIN_PATH", "herdr")
    try:
        res = subprocess.run(
            [herdr_bin, "agent", "get", agent_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        data = json.loads(res.stdout)
        session = data.get("result", {}).get("agent", {}).get("agent_session", {})
        return session.get("value")
    except Exception:
        return "bca4b5bc-db10-4e89-93ea-2ba3c4a5c938"


def load_cursor():
    if os.path.exists(CURSOR_FILE):
        try:
            with open(CURSOR_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_step_index": 19, "next_doc_number": 12}


def save_cursor(cursor):
    with open(CURSOR_FILE, "w", encoding="utf-8") as f:
        json.dump(cursor, f, indent=2, ensure_ascii=False)


def clean_user_request(text):
    if not text:
        return ""
    m = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()


def is_learning_question(text):
    text_lower = text.lower()
    ignore_patterns = [
        r"^(오케이|네|응|커밋|다음|진행|ㅇㅇ|ㅇㅋ|ㄱㄱ)",
        r"^git\s+",
        r"^py\s+",
        r"커밋하고\s*다음",
        r"다음\s*구현으로",
    ]
    for pat in ignore_patterns:
        if re.search(pat, text_lower):
            return False

    question_hints = ["왜", "무슨", "어떻게", "뭐지", "어떤", "이유", "차이", "?", "궁금", "설명", "의미"]
    return any(q in text_lower for q in question_hints) or len(text) > 40


def make_slug(question_text):
    words = re.findall(r"[a-zA-Z0-9가-힣]+", question_text)
    if not words:
        return "qna"
    slug = "-".join(words[:4]).lower()
    return slug[:35]


def git_commit_doc(filename, doc_id_str, title_text):
    """study 브랜치에 질문 문서 단위로 커밋 및 push를 수행한다."""
    try:
        subprocess.run(
            ["git", "-C", SCRIPT_DIR, "add", os.path.join("docs", filename)],
            capture_output=True,
            check=True,
        )
        commit_msg = f"docs: {doc_id_str} {title_text[:40]}"
        subprocess.run(
            ["git", "-C", SCRIPT_DIR, "commit", "-m", commit_msg],
            capture_output=True,
            check=True,
        )
        print(f"[Watcher] Git 커밋 완료: {commit_msg}", flush=True)

        # origin/study로 자동 push
        subprocess.run(
            ["git", "-C", SCRIPT_DIR, "push", "origin", "study"],
            capture_output=True,
            check=True,
        )
        print(f"[Watcher] Git Push 완료: origin/study", flush=True)
    except Exception as e:
        print(f"[Watcher Git Error] {e}", flush=True)


def process_new_steps():
    conv_id = get_agent_conversation_id("b51-coder")
    if not conv_id:
        return

    user_profile = os.environ.get("USERPROFILE", r"C:\Users\alsgu")
    transcript_path = os.path.join(
        user_profile,
        ".gemini",
        "antigravity-cli",
        "brain",
        conv_id,
        ".system_generated",
        "logs",
        "transcript.jsonl",
    )

    if not os.path.exists(transcript_path):
        return

    cursor = load_cursor()
    last_idx = cursor.get("last_step_index", 19)
    next_num = cursor.get("next_doc_number", 12)

    steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                steps.append(obj)
            except Exception:
                continue

    current_user_q = None
    max_seen_idx = last_idx

    for step in steps:
        idx = step.get("step_index", -1)
        if idx <= last_idx:
            continue

        if idx > max_seen_idx:
            max_seen_idx = idx

        stype = step.get("type")
        content = step.get("content", "")

        if stype == "USER_INPUT":
            req_text = clean_user_request(content)
            if is_learning_question(req_text):
                current_user_q = req_text
            else:
                current_user_q = None

        elif stype == "PLANNER_RESPONSE" and current_user_q:
            resp_text = content.strip()
            if resp_text and len(resp_text) > 50:
                doc_id_str = f"{next_num:04d}"
                slug = make_slug(current_user_q)
                filename = f"{doc_id_str}-{slug}.md"
                filepath = os.path.join(DOCS_DIR, filename)

                doc_content = f"# {doc_id_str} · {current_user_q[:50]}\n\n"
                doc_content += f"## Q. {current_user_q}\n\n---\n\n"
                doc_content += f"{resp_text}\n"

                with open(filepath, "w", encoding="utf-8") as out_f:
                    out_f.write(doc_content)

                print(f"[Watcher] 새 문서 생성: {filename}")
                git_commit_doc(filename, doc_id_str, current_user_q)

                next_num += 1
                current_user_q = None

    if max_seen_idx > last_idx:
        cursor["last_step_index"] = max_seen_idx
        cursor["next_doc_number"] = next_num
        save_cursor(cursor)


def main():
    print("[Watcher] b51-coder 질답 자동 문서화 + 질문별 자동 커밋 시작 (15초 주기, 0토큰)...", flush=True)
    while True:
        try:
            process_new_steps()
        except Exception as e:
            print(f"[Watcher Error] {e}", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    main()
