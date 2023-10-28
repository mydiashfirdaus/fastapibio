from fastapi import FastAPI

app = FastAPI()

# Variabel untuk menyimpan flag
flag = 0
run_flag = 0
flag1 = 0

#flag untuk get direction fokus rendah
@app.get("/set_flag/{direction}")
async def set_flag(direction: int):
    global flag
    flag = direction
    return {"flag": flag}

#flag untuk get direction fokus tinggi
@app.get("/set_flag1/{direction1}")
async def set_flag1(direction1: int):
    global flag1
    flag1 = direction1
    return {"flag": flag1}

#flag untuk start
@app.get("/selesai/{flag_main}")
async def selesai(flag_main: int):
    global run_flag
    run_flag = flag_main
    return {"flag": run_flag}

@app.get("/get_flag_rendah")
async def get_flag_rendah():
    return {"flag": flag}

@app.get("/get_flag_tinggi")
async def get_flag_tinggi():
    return {"flag": flag1}

@app.get("/get_flag_slider")
async def get_flag_slider():
    return {"flag": run_flag}