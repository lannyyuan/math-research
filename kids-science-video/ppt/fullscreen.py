"""Give every video named "clip" a click-to-play, full-screen timing node (PowerPoint's
"Start: When Clicked On" + "Play Full Screen"). pptxgenjs writes no <p:timing> at all."""
import re, sys, zipfile, shutil, os

src = sys.argv[1]
tmp = src + ".tmp"
TIMING = (
    '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
    '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
    '<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="{id}"/></p:tgtEl></p:cond></p:stCondLst>'
    '<p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync><p:childTnLst>'
    '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
    '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
    '<p:par><p:cTn id="5" presetID="2" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">'
    '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
    '<p:cmd type="call" cmd="togglePause"><p:cBhvr><p:cTn id="6" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{id}"/></p:tgtEl></p:cBhvr></p:cmd>'
    '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
    '</p:childTnLst></p:cTn><p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
    '<p:video fullScrn="1"><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
    '<p:tgtEl><p:spTgt spid="{id}"/></p:tgtEl></p:cMediaNode></p:video>'
    '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
)
n = 0
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if re.fullmatch(r"ppt/slides/slide\d+\.xml", item.filename):
            xml = data.decode("utf8")
            m = re.search(r'<p:cNvPr id="(\d+)" name="clip"', xml)
            if m and "<p:timing>" not in xml:
                # <p:timing> follows <p:clrMapOvr> (and any <p:transition>) inside <p:sld>
                xml = xml.replace("</p:sld>", TIMING.format(id=m.group(1)) + "</p:sld>", 1)
                assert xml.index("<p:timing>") > xml.index("</p:clrMapOvr>")
                data = xml.encode("utf8"); n += 1
        # media is already compressed; store it to keep the rewrite fast
        ct = zipfile.ZIP_STORED if item.filename.endswith((".mp4", ".png", ".jpg", ".jpeg")) else zipfile.ZIP_DEFLATED
        zout.writestr(item, data, compress_type=ct)
shutil.move(tmp, src)
print(f"full-screen timing added to {n} slides")
