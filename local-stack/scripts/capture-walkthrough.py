# Drives ATLAS through the demo path (home -> data sources -> cohort definition + generation -> vocabulary
# search -> concept set -> duplicate-name error -> configuration -> raw API JSON), taking full-screen
# screenshots and an ffmpeg screen recording into $OUT (default ./evidence).
# Needs an X display (e.g. `Xvfb :99 -screen 0 1600x1000x24 &; export DISPLAY=:99`), ffmpeg, ImageMagick
# `import`, and `pip install playwright && playwright install chromium`. Creates (and on the next run deletes)
# a concept set named "GSK Demo - Sinusitis"; generates cohort #1 on EUNOMIA.
import asyncio, subprocess, json, urllib.request, os
from playwright.async_api import async_playwright
B="http://localhost:8090/atlas/"
OUT=os.environ.get("OUT", os.path.abspath("evidence")); os.makedirs(OUT,exist_ok=True)
DUP="GSK Demo - Sinusitis"
DISPLAY=os.environ.get("DISPLAY",":99")
def api(method,path,body=None):
    req=urllib.request.Request("http://localhost:8090/WebAPI/"+path,method=method,data=json.dumps(body).encode() if body else None,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: return r.read()
for c in json.loads(api("GET","conceptset/")):
    if c["name"]!="Demo chronic sinusitis": api("DELETE",f"conceptset/{c['id']}")
def shot(name):
    subprocess.run(["import","-display",DISPLAY,"-window","root",f"{OUT}/{name}.png"],check=True); print("shot",name,flush=True)
async def pause(pg,ms=2500): await pg.wait_for_timeout(ms)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=False,args=["--window-position=0,0","--window-size=1600,1000","--no-first-run","--disable-infobars","--test-type"])
        ctx=await b.new_context(no_viewport=True)
        pg=await ctx.new_page()
        dialog_seen=asyncio.Event()
        async def on_dialog(d):
            print("DIALOG:",d.message,flush=True)
            if "already exists" not in d.message:
                await d.accept(); return
            await asyncio.sleep(2.5); shot("08_duplicate_conceptset_error"); await asyncio.sleep(2.5)
            await d.accept(); dialog_seen.set()
        pg.on("dialog",lambda d: asyncio.ensure_future(on_dialog(d)))
        rec=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","x11grab","-video_size","1600x1000","-framerate","15","-i",DISPLAY,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",f"{OUT}/atlas_walkthrough.mp4"],stdin=subprocess.PIPE)
        try:
          await run(pg,dialog_seen)
        finally:
          rec.communicate(b"q"); await b.close()
async def run(pg,dialog_seen):
        # 1 home
        await pg.goto(B+"#/home"); await pg.locator("text=Welcome to ATLAS >> visible=true").first.wait_for(timeout=60000); await pause(pg,3000); shot("01_atlas_home")
        # 2 data sources
        await pg.click("text=Data Sources"); await pause(pg,3000)
        await pg.locator("select").nth(2).select_option(label="Dashboard"); 
        await pg.wait_for_timeout(9000); shot("02_data_sources_dashboard")
        await pg.mouse.move(800,600); await pg.mouse.wheel(0,700); await pause(pg,2500); shot("02b_data_sources_dashboard_scrolled")
        # 3 cohort definitions list
        await pg.click("a:has-text('Cohort Definitions')"); await pg.locator("text=Demo new users of diclofenac >> visible=true").first.wait_for(timeout=60000); await pause(pg,2500); shot("03_cohort_definitions_list")
        # 4 editor
        await pg.click("text=Demo new users of diclofenac"); await pg.locator("text=Cohort Entry Events >> visible=true").first.wait_for(timeout=60000); await pause(pg,3500); shot("04_cohort_definition_editor")
        # 5 generation
        await pg.click("a:has-text('Generation')"); await pg.wait_for_selector("button:has-text('Generate')"); await pause(pg,1500)
        await pg.click("button:has-text('Generate')")
        for i in range(60):
            await pg.wait_for_timeout(3000)
            if await pg.locator("td:has-text('COMPLETE')").count(): break
        await pause(pg,2000); shot("05_cohort_generation_complete")
        # 6 vocab search
        await pg.click("a:has-text('Search')"); await pause(pg,1500)
        inp=pg.locator("input[type=text]:visible").first; await inp.fill("sinusitis"); await inp.press("Enter")
        await pg.locator("text=Chronic sinusitis >> visible=true").first.wait_for(timeout=60000); await pause(pg,3000); shot("06_vocabulary_search")
        # 7 build concept set
        for nm in ["Sinusitis","Chronic sinusitis"]:
            await pg.locator(f"tr:has(a:text-is('{nm}'))").locator("td").first.click(); await pause(pg,800)
        await pg.click("button:has-text('Add To New Concept Set')"); await pause(pg,2000)
        await pg.click("a:has-text('Concept Sets')"); await pg.locator("td:has-text('sinusitis') >> visible=true").first.wait_for(timeout=60000); await pause(pg,2500)
        name=pg.locator("input[data-bind*='currentConceptSet().name']")
        await name.fill(DUP); await pause(pg,1500)
        await pg.click("button[title='Save']"); await pg.wait_for_timeout(5000); shot("07_conceptset_created")
        # 8 duplicate
        await pg.click("button[title='Close']"); await pause(pg,2000)
        await pg.click("a:has-text('Search')"); await pause(pg,1500)
        inp=pg.locator("input[type=text]:visible").first; await inp.fill("sinusitis"); await inp.press("Enter")
        await pg.locator("text=Acute bacterial sinusitis >> visible=true").first.wait_for(timeout=60000); await pause(pg,1500)
        await pg.locator("tr:has(a:text-is('Acute bacterial sinusitis'))").locator("td").first.click(); await pause(pg,800)
        await pg.click("button:has-text('Add To New Concept Set')"); await pause(pg,2000)
        await pg.click("a:has-text('Concept Sets')"); await pg.locator("td:has-text('sinusitis') >> visible=true").first.wait_for(timeout=60000); await pause(pg,2500)
        name=pg.locator("input[data-bind*='currentConceptSet().name']")
        await name.fill(DUP); await pause(pg,1500)
        await pg.click("button[title='Save']")
        await asyncio.wait_for(dialog_seen.wait(),30); await pause(pg,2000)
        # 9 configuration
        await pg.evaluate("window.onbeforeunload=null")
        pg.on("dialog",lambda d: asyncio.ensure_future(d.accept()))
        await pg.click("a:has-text('Configuration')"); await pg.locator("text=Vocabulary Version >> visible=true").first.wait_for(timeout=60000); await pause(pg,3000); shot("09_configuration_vocab_version")
        # 10/11 API json
        await pg.goto("http://localhost:8090/WebAPI/info"); await pause(pg,3500); shot("10_api_webapi_info")
        await pg.goto("http://localhost:8090/WebAPI/source/sources"); await pause(pg,3500); shot("11_api_source_sources")
asyncio.run(main())
