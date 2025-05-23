import sys, requests, subprocess, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
AI = "devstral"

def parse_log():
    history_lines = []
    last_lines = []
    mode = None
    if os.path.exists("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as f:
            for line in f:
                L = line.strip()
                if L.lower() == "history:":
                    mode = "history"
                    continue
                elif L.lower() == "last:":
                    mode = "last"
                    continue
                if mode == "history":
                    if L.startswith("- User:") or L.startswith("- AI:"):
                        history_lines.append(L)
                elif mode == "last":
                    if L.startswith("- User:") or L.startswith("- AI:"):
                        last_lines.append(L)
    return history_lines, last_lines

def read_files_txt():
    if not os.path.exists("files.txt"):
        return ""
    with open("files.txt", "r", encoding="utf-8") as f:
        return f.read()

def Run(Msg):
    Hst, Lst = parse_log()

    Personality = ""
    if os.path.exists("personality.txt"):
        with open("personality.txt", "r", encoding="utf-8") as P:
            Personality = P.read().strip()

    UserInfo = ""
    if os.path.exists("userInfo.txt"):
        with open("userInfo.txt", "r", encoding="utf-8") as U:
            UserInfo = U.read().strip()

    FilesTxtContent = read_files_txt()

    Prompt = ""
    if Personality:
        Prompt += f"Personality:\n{Personality}\n\n"
    if UserInfo:
        Prompt += f"UserInfo:\n{UserInfo}\n\n"
    if FilesTxtContent:
        Prompt += f"Files.txt content:\n{FilesTxtContent}\n\n"
    if Hst:
        Prompt += "History:\n" + "\n".join(Hst) + "\n\n"
    if Lst:
        Prompt += "Last:\n" + "\n".join(Lst) + "\n\n"
    Prompt += f"User: {Msg}\nAI:"

    m = re.match(r'read (\S+)', Msg.lower())
    if m:
        F = m.group(1)
        if os.path.exists(F):
            with open(F, 'r', encoding='utf-8') as R:
                C = R.read()
            Prompt = f"File content:\n{C}\n\nPlease analyze."
        else:
            print(f"File not found: {F}")
            return

    with open("debug.txt", "w", encoding="utf-8") as D:
        D.write(f"Prompt -> {Prompt}\n")

    R = requests.post("http://127.0.0.1:11434/api/generate",
                      json={"model": AI, "prompt": Prompt},
                      stream=True)

    Resp = ""
    for L in R.iter_lines():
        if not L:
            continue
        J = json.loads(L.decode())
        if "response" in J:
            Resp += J["response"]

    Resp = Resp.strip()
    print("Response ->", Resp)

    with open("debug.txt", "a", encoding="utf-8") as D:
        D.write(f"Response -> {Resp}\n\n")

    history_text = ""
    if Hst:
        history_text = "\n".join(Hst) + "\n"
    if Lst:
        history_text += "\n".join(Lst) + "\n"

    last_text = f"- User: {Msg}\n- AI: {Resp}\n"

    with open("log.txt", "w", encoding="utf-8") as F:
        F.write("history:\n")
        if history_text.strip():
            F.write(history_text.strip() + "\n\n")
        else:
            F.write("\n")
        F.write("last:\n")
        F.write(last_text)

    for L in Resp.splitlines():
        if L.startswith("CMD:"):
            subprocess.run(L[4:].strip(), shell=True)
        elif L.startswith("READ:"):
            F = L[5:].strip()
            if os.path.exists(F):
                with open(F, "r", encoding='utf-8') as R:
                    print(R.read())
        elif L.startswith("WRITE:"):
            F, D = L[6:].split("::", 1)
            with open(F.strip(), "w", encoding='utf-8') as W:
                W.write(D.strip())

if __name__ == "__main__":
    Msg = " ".join(sys.argv[1:])
    if not Msg.strip():
        print("No input")
        sys.exit(1)
    Run(Msg)
