"""Video timing for presenting with a clicker/arrow keys (v4.5+).

Every video named "clip" (part pages) or "compareVideo" gets PowerPoint's
"Start: On Click (in click sequence)" + "Play Full Screen":
  - the first Next/arrow/clicker press on the slide plays the video full screen,
  - when it ends the slide is shown again and the next press goes to the next slide,
  - clicking the video itself still plays/pauses it.
pptxgenjs writes no <p:timing>, so it is added here after writeFile."""
import re, sys, zipfile, shutil, subprocess, tempfile, os, json

src = sys.argv[1]
tmp = src + ".tmp"

def timing(spid, dur_ms):
    return (
        '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        # main click sequence: Next plays the video from the start
        '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">'
        '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f'<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{dur_ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
        '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn>'
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
        # clicking the video itself toggles play/pause
        '<p:seq concurrent="1" nextAc="seek"><p:cTn id="7" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
        f'<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cond></p:stCondLst>'
        '<p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync><p:childTnLst>'
        '<p:par><p:cTn id="8" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="9" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        '<p:par><p:cTn id="10" presetID="2" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">'
        '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f'<p:cmd type="call" cmd="togglePause"><p:cBhvr><p:cTn id="11" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
        '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn><p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
        # full-screen playback
        '<p:video fullScrn="1"><p:cMediaNode vol="80000"><p:cTn id="12" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
        f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
        '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
    )

def duration_ms(data):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(data); path = f.name
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
        return int(round(float(out) * 1000))
    finally:
        os.unlink(path)

report = []
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        m_name = re.fullmatch(r"ppt/slides/(slide\d+)\.xml", item.filename)
        if m_name:
            xml = data.decode("utf8")
            m = re.search(r'<p:cNvPr id="(\d+)" name="(clip|compareVideo)"', xml)
            if m and "<p:timing>" not in xml:
                # the video's media part, via the p14:media embed id on that picture
                pic = xml[m.start():xml.index("</p:pic>", m.start())]
                rid = re.search(r'p14:media[^>]*r:embed="(rId\d+)"', pic).group(1)
                rels = zin.read(f"ppt/slides/_rels/{m_name.group(1)}.xml.rels").decode()
                target = re.search(rf'Id="{rid}"[^>]*Target="\.\./([^"]+)"', rels).group(1)
                dur = duration_ms(zin.read("ppt/" + target))
                xml = xml.replace("</p:sld>", timing(m.group(1), dur) + "</p:sld>", 1)
                assert xml.index("<p:timing>") > xml.index("</p:clrMapOvr>")
                data = xml.encode("utf8")
                report.append((m_name.group(1), m.group(2), dur))
        ct = zipfile.ZIP_STORED if item.filename.endswith((".mp4", ".png", ".jpg", ".jpeg")) else zipfile.ZIP_DEFLATED
        zout.writestr(item, data, compress_type=ct)
shutil.move(tmp, src)
for r in sorted(report, key=lambda r: int(r[0][5:])): print(*r)
print(f"click-to-play full-screen timing on {len(report)} slides")
