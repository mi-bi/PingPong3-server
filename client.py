
import asyncio
import websockets
import json
import concurrent
import sys

class request:

    counter = 0
    body = {}

    def __init__(self, command, session_id=None):
        request.counter = request.counter + 1
        self.body['request'] = command
        self.body['transaction_id'] = request.counter
        if session_id is not None:
            self.body['session_id'] = session_id
    
    def __str__(self):
        return json.dumps(self.body)
    
async def sendrecv(ws, req):
    await ws.send(str(req))
    msg = await ws.recv()
    msg = msg
    ret = json.loads(msg)
    return ret

async def pingpong(host,port,delay):
    uri = "ws://"+host+":"+port+"/"
    req = request(command="create_session")
    retry = 3
    is_connected = False
    while not is_connected:
        try:
            print("Lacze")
            ws = await asyncio.wait_for(websockets.connect(uri), timeout=5)
            ans = await asyncio.wait_for(sendrecv(ws, req), timeout=3)
            is_connected = True
        except ConnectionRefusedError:
            print("Odrzucone")
        except websockets.exceptions.ConnectionClosedError:
            print("Przerwane")
        except concurrent.futures._base.TimeoutError:
            print("Timeout")
            pass

        if not is_connected:
            #ws.colse()
            retry = retry - 1
            if retry >= 0:
                await asyncio.sleep(3)
            else:
                return
    try:
        sid = ans['session_id']
        while True: 
            req = request(command="ping", session_id=sid)
            message = await asyncio.wait_for(sendrecv(ws, req), timeout=3)
            print(message)
            await asyncio.sleep(delay)
    except websockets.exceptions.ConnectionClosedError:
        print("Polaczenie zostalo przerwane")
    except websockets.exceptions.ConnectionClosedOK:
        print("Polaczenie zostalo zamkniete")
    except ConnectionRefusedError:
        print("Poloczenie zostalo odrzucone")
    except json.decoder.JSONDecodeError:
        print("Zly format wiadmosci")
    except KeyError:
        print("Niepelna wiadomosc")
    except concurrent.futures._base.TimeoutError:
        print("Timeout")

if len(sys.argv) != 3:
    print("WebSocket pingpong client")
    print("")
    print("Uzycie "+sys.argv[0]+" host port")
    print("")
else:
    try:
        asyncio.get_event_loop().run_until_complete(pingpong(sys.argv[1],sys.argv[2],1))
    except KeyboardInterrupt:
        print("Koniec")

