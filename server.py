
import asyncio
import websockets
import json
import sys

# session counter
counter = 0

async def pingpong(websocket, path):
    global counter
    print(websocket)
    sid = None
    try:
        async for message in websocket:
            print("Dostalem:"+message)
            data = json.loads(message)
            if 'request' in data:
                rq = data['request']
                ans = {'transaction_id':data['transaction_id']}
                if rq == 'create_session':
                    if sid is not None:
                        print("sesja zostala juz utworzona!!")
                        return
                    #  await asyncio.sleep(40)
                    sid = counter
                    counter = counter + 1
                    ans['session_id'] = sid
                    print(f"Tworze nowa sesje: sessoin_id:{sid}")
                    await websocket.send(json.dumps(ans))
                elif rq == 'ping':
                    if sid is None:
                        print("sesja nie zostala utworzona!!!")
                        return
                    if data['session_id'] != sid:
                        print("Zly numer sesji!!!!")
                        return
                    ans['session_id'] = sid
                    ans['message'] = 'pong'
       #             if data['transaction_id']%5 == 0:
       #                 ans['message'] = "pogo"
       #             if data['transaction_id']%10 == 0:
       #                 continue
                    await websocket.send(json.dumps(ans))

    except websockets.exceptions.ConnectionClosedError:
        print("Polaczenie zostało przerwane")
        return
    except websockets.exceptions.ConnectionClosedOK:
        print("Polaczenie zostalo zamkniete")
        return
    except json.decoder.JSONDecodeError:
        print("Zly format wiadmosci")
        return
    except KeyError:
        print("Niepelna wiadomosci")
        return


if len(sys.argv) != 3:
    print("WebSocket PingPong Server")
    print("")
    print("Uzycie: "+sys.argv[0]+" IP PORT")
    print("")
else:
    start_server = websockets.serve(pingpong, sys.argv[1], int(sys.argv[2]))
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

