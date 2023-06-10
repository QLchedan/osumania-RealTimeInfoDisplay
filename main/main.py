import json
import requests
import uvicorn
from rosu_pp_py import Beatmap, Calculator
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from configparser import ConfigParser
import subprocess
import os


devnull = open(os.devnull, 'w')
subprocess.Popen('.\\MemServer.exe', stdout=devnull)
conf = ConfigParser()
conf.read('config.ini')
port = int(conf['Settings']['Port'])
songs_path = conf['Settings']['SongsPath']
if songs_path[-1] != '\\': songs_path += '\\'

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
curr_map_id = str()
curr_diff = None


@app.get('/', response_class = HTMLResponse)
async def show():
   h = str()
   with open('index.html', 'r', encoding='utf8') as f:
       h = f.read()
   return h

@app.get('/getjson')
async def getjson():
    global curr_diff, curr_map_id
    curr_hit_err = 0
    avg_hit_err = 0
    r = requests.get('http://localhost:9810/getjson').content
    j = json.loads(r)
    hp = j['Beatmap']['Hp']
    od = j['Beatmap']['Od']
    map_id = j['Beatmap']['Id']
    hit320 = j['Player']['HitGeki']
    hit300 = j['Player']['Hit300']
    hit200 = j['Player']['HitKatu']
    hit100 = j['Player']['Hit100']
    hit50 = j['Player']['Hit50']
    hit0 = j['Player']['HitMiss']
    hit_err = j['Player']['HitErrors']
    folder_name = j['Beatmap']['FolderName']
    osu_file_name = j['Beatmap']['OsuFileName']
    mods = j['Player']['Mods']['Value']
    map = Beatmap(path = songs_path + folder_name + '\\' + osu_file_name)
    calc = Calculator(mods = mods, mode = 3, n_geki = hit320, n_katu = hit200, n300 = hit300, n100 = hit100, n50 = hit50, n_misses = hit0)
    if map_id == curr_map_id:
        calc.set_difficulty(curr_diff)
    else:
        curr_diff = calc.difficulty(map)
        curr_map_id = map_id
    pp = calc.performance(map).pp
    pp = str(round(pp, 2)) + 'pp'
    try:
        curr_hit_err = hit_err[-1]
        t = 0
        if len(hit_err) <= 100:
            for i in hit_err:
                t += i
            avg_hit_err = round(t / len(hit_err), 2)
        else:
            for i in hit_err[-100:]:
                t += i
            avg_hit_err = round(t / 100, 2)
    except:
        pass
    return json.dumps([hp, od, hit320, hit300, hit200, hit100, hit50, hit0, pp, curr_hit_err, avg_hit_err])
    

if __name__ == '__main__':
    print('osu!mania实时显示插件')
    print('by 千里扯淡 2023.6')
    print('GitHub: https://github.com/QLchedan/osumania-RealTimeInfoDisplay')
    osu = '  ___  ____  _   _ _ \n / _ \\/ ___|| | | | |\n| | | \\___ \\| | | | |\n| |_| |___) | |_| |_|\n \\___/|____/ \\___/(_)\n                     \n'
    print(osu)
    print('祝您屙屎愉快！')
    print('Address: \'http://localhost:' + str(port) + '\'')
    print('Ctrl+C 退出')
    uvicorn.run(app, host="localhost", port=port, log_level="error")
    
