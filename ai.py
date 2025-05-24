import sys, requests, subprocess, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
AI = "devstral"

def parse_log():
    H = []
    L = []
    m = None
    if os.path.exists("log.txt"):
        with open("log.txt", "r", encoding="utf-8") as f:
            for ln in f:
                l = ln.rstrip('\n')
                low = l.lower()
                if low == "history:":
                    m = "history"
                    continue
                elif low == "last:":
                    m = "last"
                    continue
                if m == "history":
                    H.append(l)
                elif m == "last":
                    L.append(l)

    def group_blocks(lines):
        b = []
        blk = []
        for ln in lines:
            if ln.startswith("- User:") or ln.startswith("- AI:"):
                if blk:
                    b.append(blk)
                blk = [ln]
            else:
                if blk:
                    blk.append(ln)
                elif b:
                    b[-1].append(ln)
        if blk:
            b.append(blk)
        return b

    return H, group_blocks(L)

def read_files():
    if not os.path.exists("files.txt"):
        return ""
    with open("files.txt", "r", encoding="utf-8") as f:
        return f.read()

def Run(Msg):
    Hst, LstBlk = parse_log()

    P = ""
    if os.path.exists("personality.txt"):
        with open("personality.txt", "r", encoding="utf-8") as p:
            P = p.read().strip()

    U = ""
    if os.path.exists("userInfo.txt"):
        with open("userInfo.txt", "r", encoding="utf-8") as u:
            U = u.read().strip()

    Ftxt = read_files()

    Pr = ""
    if P:
        Pr += f"Personality:\n{P}\n\n"
    if U:
        Pr += f"UserInfo:\n{U}\n\n"
    if Ftxt:
        Pr += f"Files.txt content:\n{Ftxt}\n\n"
    if Hst:
        Pr += "History:\n" + "\n".join(Hst) + "\n\n"
    if LstBlk:
        flat = []
        for blk in LstBlk:
            flat.extend(blk)
        Pr += "Last:\n" + "\n".join(flat) + "\n\n"
    Pr += f"User: {Msg}\nAI:"

    m = re.match(r'read (\S+)', Msg.lower())
    if m:
        f = m.group(1)
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as r:
                c = r.read()
            Pr = f"File content:\n{c}\n\nPlease analyze."
        else:
            print(f"File not found: {f}")
            return

    with open("debug.txt", "w", encoding="utf-8") as d:
        d.write(f"Prompt -> {Pr}\n")

    r = requests.post("http://127.0.0.1:11434/api/generate",
                      json={"model": AI, "prompt": Pr},
                      stream=True)

    resp = ""
    for l in r.iter_lines():
        if not l:
            continue
        j = json.loads(l.decode())
        if "response" in j:
            resp += j["response"]

    resp = resp.strip()
    print("Response ->", resp)

    with open("debug.txt", "a", encoding="utf-8") as d:
        d.write(f"Response -> {resp}\n\n")

    if LstBlk:
        for blk in LstBlk:
            Hst.extend([line.rstrip('\n') for line in blk])

    with open("log.txt", "w", encoding="utf-8") as f:
        f.write("history:\n")
        if Hst:
            f.write("\n".join(Hst).rstrip() + "\n\n")
        else:
            f.write("\n")

        f.write("last:\n")
        f.write(f"- User: {Msg}\n")
        lines = resp.splitlines()
        if lines:
            f.write(f"- AI: {lines[0]}\n")
            for ln in lines[1:]:
                f.write(ln + "\n")
        else:
            f.write("- AI:\n")

    for l in resp.splitlines():
        if l.startswith("CMD:"):
            subprocess.run(l[4:].strip(), shell=True)
        elif l.startswith("READ:"):
            f = l[5:].strip()
            if os.path.exists(f):
                with open(f, "r", encoding='utf-8') as r:
                    print(r.read())
        elif l.startswith("WRITE:"):
            f, d = l[6:].split("::", 1)
            with open(f.strip(), "w", encoding='utf-8') as w:
                w.write(d.strip())

if __name__ == "__main__":
    M = " ".join(sys.argv[1:])
    if not M.strip():
        print("No input")
        sys.exit(1)
    Run(M)
