from tkinter import *
from tkinter import ttk
from contextlib import suppress
import asyncio, struct, serial, socket, sys

class DetectCOMPorts:
    def __init__(self):
        self.ports = ['COM%s' % (i + 1) for i in range(16)]
        self.result = []

    def detect(self):
        for port in self.ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.result.append(port)
            except (OSError, serial.SerialException) as exc:
                print(f'{exc}')
                pass
        return self.result

class DGramStream:
    def __init__(self):
        self.loop       = asyncio.get_event_loop()

    async def stream(self, com_port, sockport, game_name):
        self.com_port   = com_port
        self.sockport   = int(sockport)
        self.game_name  = game_name
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = ('0.0.0.0', self.sockport)
        sock.bind(address)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1)
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: Recv(self.com_port, self.game_name),
            sock = sock)

class Recv(asyncio.Protocol):
    def __init__(self, com_port, game_name):
        self.transport = None
        self.sendr = Sendr(com_port)
        self.game_name  = game_name

    def connection_made(self, transport):
        self.transport = transport
        gui.setTransport(transport)

    def datagram_received(self, data, addr):
        if self.game_name == "dr_wrc":
            data = struct.unpack('64f', data[0:256])
            data = {'speed': int(data[7]*3.6), 'gear': int(data[33]),
                    'rpm': int(data[37] * 10), 'max_rpm': int(data[63] * 10)
                    }

        if self.game_name == "rbr_ngp6":
            rpm = struct.unpack_from("@f", data , offset=136)[0]
            speed = struct.unpack_from("@f", data , offset=60)[0]
            gear = struct.unpack_from("@l", data , offset=44)[0]
            data = {'rpm': abs(int(round(rpm))), 'max_rpm': 7200,
                    'speed': abs(int(speed)), 'gear': int(round(gear))-1}

        if self.game_name == "pcars1-2":
            with suppress(ValueError):
                rpm     = int(struct.unpack_from("@H", data , offset=124)[0])
                max_rpm = int(struct.unpack_from("@H", data , offset=126)[0])
                speed   = int(struct.unpack_from("@f", data , offset=120)[0])
                gear    = hex(struct.unpack_from("@B", data , offset=128)[0])[3:]
                if gear == 'f':
                    gear = int(10)
                else:
                    gear = int(gear)
                data = {'rpm': rpm, 'max_rpm': max_rpm,
                        'speed': int(speed*3.6), 'gear': gear}

        if self.game_name == "ea_wrc":
            data = struct.unpack('@fffb', data)
            data = {'speed': int(data[2]*3.6), 'gear': data[3],
                   'rpm': int(data[0]), 'max_rpm': int(data[1])
                    }
                        
        self.sendr.send(data)

    def error_received(self, exc):
        print(f'Error received: {exc}')
        gui.setWarning('⚠')

    def connection_lost(self, exc):
        print(f'Connection lost: {exc}')
        gui.setWarning('⚠')
        pass


class Sendr:
    def __init__(self, com_port):
        try:
            self.serial1 = serial.Serial(com_port, 9600,
                writeTimeout=.3, timeout=.3, dsrdtr=True, xonxoff=True)
        except serial.serialutil.SerialException as exc:
            print(f'{exc} at {com_port}')
        print(f'{self.serial1}\r\n')
        gui.setSerial(self.serial1)
        gui.setWarning('✅')

    def send(self, data):
        try:
            #with suppress(TypeError):
            package1 = struct.pack('>cHHcbch',
                        b'R', data['rpm'], data['max_rpm'],
                        b'G', data['gear'], b'S', data['speed']
                        )
            self.serial1.write(package1)
            self.serial1.reset_output_buffer()
        except serial.serialutil.SerialTimeoutException as exc:
            print(f'we got {len(package1)} bytes input, but something wrong: {exc}')
            gui.setWarning('⚠')
            pass
        except serial.serialutil.SerialException as exc:
            print(f'oops! {exc}')
            gui.setWarning('⚠')

class mainWindow:
    def __init__(self, tk_handler):
        self.tk_handler = tk_handler
        self.tk_handler.protocol("WM_DELETE_WINDOW", self.quit)
        tk_handler.geometry("240x100+800+400")
        tk_handler.title('rally arduino gauge')
        frame = Frame(tk_handler)
        frame.pack()
        self.frame = frame
        self.box_name(frame)
        self.box_comport(frame)
        self.entry_sockport(frame)
        self.startbutton(frame)
        self.d = {}
        self.isRunning = True

    def box_name(self, frame):
        self.vlist              = ["dr_wrc", "ea_wrc", "rbr_ngp6", "pcars1-2"]
        self.box_name           = ttk.Combobox(frame, values=self.vlist,
                                               state="readonly", width=15)
        self.box_name.extra     = 'game_name'
        self.box_name.set("game")
        self.box_name.grid(row=0, column=0, padx=5, pady=5)
        self.box_name.bind('<<ComboboxSelected>>', self.check)
        
    def setWarning(self, text='ok'):
        self.warn_sign = ttk.Label(self.frame, text=text).grid(row=3, column=1)
            
    def box_comport(self, frame):
        self.clist              = DetectCOMPorts().detect()
        self.box_comport        = ttk.Combobox(frame, values=self.clist, state="readonly", width=8)
        self.box_comport.extra  = 'com_port'
        self.box_comport.set("com port")
        self.box_comport.grid(row=0, column=1, padx=5, pady=5)
        self.box_comport.bind('<<ComboboxSelected>>', self.check)
        
    def entry_sockport(self, frame):
        self.entry_var = IntVar()
        self.entry_sockport = ttk.Entry(frame, width=8, textvariable=self.entry_var)
        self.entry_sockport.grid(row=2, column=0, padx=5, pady=5)
        self.entry_sockport.bind('<KeyRelease>', self.check)
        self.entry_sockport.extra='sockport'

    def startbutton(self, frame):
        self.buttonvals = ['run!', 'running: press to stop']
        self.buttonval = 0
        self.startbutton = ttk.Button(frame, text=self.buttonvals[self.buttonval], state="disabled", command=self.run)
        self.startbutton.grid(row=3, column=0, padx=5, pady=5)

    def setTransport(self, transport):
        self.transport = transport

    def setSerial(self, serial):
        self.serial = serial
        
    def check(self, event):
        t = [(event.widget.extra, event.widget.get())]
        self.set_defaults(event.widget.extra, event.widget.get())
        self.d.update(t)
        if self.entry_sockport.get() != None:
            t = [(self.entry_sockport.extra, self.entry_sockport.get())]
            self.d.update(t)
        if len(self.d) == 3:
            if (
                self.d['game_name'] in self.vlist and
                self.d['com_port'] in self.clist and self.d['sockport'].isnumeric()
                ):
                self.startbutton.config(state='enabled')
            else:
                self.startbutton.config(state='disabled')

    def set_defaults(self, name, value):
        if value == "dr_wrc":
            self.entry_sockport.delete(0, END)
            self.entry_sockport.insert(0, "20777")
        if value == "ea_wrc":
            self.entry_sockport.delete(0, END)
            self.entry_sockport.insert(0, "20777")
        if value == "rbr_ngp6":
            self.entry_sockport.delete(0, END)
            self.entry_sockport.insert(0, "6776")
        if value == "pcars1-2":
            self.entry_sockport.delete(0, END)
            self.entry_sockport.insert(0, "5606")

    def run(self):
        self.buttonval  = not self.buttonval
        com_port        = self.d['com_port']
        sockport        = self.d['sockport']
        game_name       = self.d['game_name']
        self.isRunning  = not self.isRunning
        self.dgram      = DGramStream()
        self.startbutton.config(text=self.buttonvals[self.buttonval])
        if not self.isRunning:
            fut = asyncio.run_coroutine_threadsafe(self.dgram.stream(
                com_port, sockport, game_name), asyncio.get_event_loop())
            for x in [self.box_name, self.box_comport, self.entry_sockport]:
                x.config(state='disabled')
        else:
            print(self.transport)
            self.setWarning('➿')
            self.transport.close()
            self.serial.close()
            for x in [self.box_name, self.box_comport, self.entry_sockport]:
                x.config(state='enabled')

    def quit(self):
        try:
            self.transport.close()
            self.serial.close()
        except:
            pass
        self.tk_handler.quit()
        asyncio.get_event_loop().stop()
        self.tk_handler.destroy()


if __name__ ==  '__main__':
    root    = Tk()
    gui     = mainWindow(root)

    def run_tk():
        root.update()
        asyncio.get_event_loop().call_soon(run_tk)

    try:
        run_tk()
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
