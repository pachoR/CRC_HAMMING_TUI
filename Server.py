from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, LoadingIndicator, Button, Switch
from textual.containers import ScrollableContainer, Container, Horizontal, Vertical, Center
import socket
import platform
import os
import re
from Hamming_CRC import Hamming_CRC

ip_addr = None
encoder = Hamming_CRC()
server = None
client = None
addr = None
shared_key = '1010'
done = False


def get_ip():
    os_system = platform.system()
    
    if os_system == 'Windows':
        hostname = socket.gethostname()
        IPaddrs = socket.gethostbyname(hostname)
        return IPaddrs
    else:
        """
        The past implementation, quite more easy than the following, it's no
        available using UNIX-like OS, so we need to get the full command output
        and, with the help of RegEx, extract the IP 
        """
        command_stream = os.popen('ifconfig -a')
        command_output = command_stream.read()
        ip_regex_pattern = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
        matches = ip_regex_pattern.findall(command_output)
        
        ip_addresses = [ip for ip in matches if ip != '127.0.0.1']
        if ip_addresses:
            return ip_addresses[0]
        else:
            return 'No-found IP'
        

class ChatServer(Screen):

    def __init__(self, *args, **kwargs):
        #this_self = self
        super().__init__(*args, **kwargs)
        global done
        # self.text_area = TextArea()
        # self.text_label = Label("", id="text_label")
        # self.text_label2 = Label("", id="text_label2")
        self.text_corregido = Label("", id="text_corregido")
        self.text_indice = Label("", id="text_indice")
        self.text_mensaje = Label("", id="text_mensaje")
        self.text_error = Label("",id="text_error")
        self.switch = Switch(animate=False, id="switch")
        valor = 5

        #msg_recieved = client.recv(1204).decode('utf-8')  
        while not done:
            msg_recieved = client.recv(1204).decode('utf-8')  
            raw_message = encoder.get_rawData(msg_recieved[0:len(msg_recieved)-len(shared_key)+1])
            crc_recieved = msg_recieved[len(msg_recieved)-len(shared_key)+1:]
            
            error = encoder.decode_CRC(raw_message+crc_recieved, shared_key)

            if not error == None:
                msg_recieved, error_corrected, err_idx = encoder.hamming_decode(msg_recieved[0:len(msg_recieved)-len(shared_key)+1])
                self.text_corregido.update(str(error_corrected))
                self.text_indice.update(str(err_idx))
                self.text_mensaje.update(str(msg_recieved))
            else:
                self.text_error.update(encoder.bin_to_string(raw_message))

            

            response = 'Recibido'
            response = encoder.string_to_bin(response)
            crc_response = encoder.CRC_code(response, shared_key)
            response = encoder.hamming_codification(response)
            response = encoder.generate_err(response)
            response = response + crc_response
            client.send(response.encode('utf-8'))


            done = True
        
        

    def compose(self) -> None:
        yield ScrollableContainer(
            Center(
             Label("CONECTADO CORRECTAMENTE CON EL CLIENTE, BIENVENIDO AL SERVER!!!", id="msg_bienvenida"),
             Label("ESPERE EL MENSAJE DEL CLIENTE:)", id="msg_text"),
             id="center-texto"
             ),
             Center(
                 Label("AQUI VA A RECIBIR EL MENSAJE DEL CLIENTE:      ", id="recibir"),
                 id="center-text"
             ),
             Center(
                Label("ERROR CORREGIDO:"),
                self.text_corregido,
                Label(""),
                Label("INDICE EN DONDE FUE CORREGIDO EL ERROR:"),
                self.text_indice,
                Label(""),
                Label("MENSAJE DEL CLIENTE:"),
                self.text_mensaje,
                Label(""),
                self.text_error,
                 id="center-cliente"
             ),
             Center(
             Button.error(id="borrar", label="ESPERAR NUEVO MENSAJE"),
             Button.error(id="volver", label="DESCONECTARSE"),
             id="center-volver"
             ),
             id="contenedor_todo"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
         global done
         if event._sender.id == "volver":
          done = False
          server.close()
          self.app.pop_screen()
         if event._sender.id == "borrar":
          self.text_corregido.update("")
          self.text_indice.update("")
          self.text_mensaje.update("")
          self.text_error.update("")
          done = False
          self.app.pop_screen()
          self.app.push_screen(ChatServer())

             
class BSOD(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static("CONECTATE!!! ", id="title")
        yield LoadingIndicator()
        yield Static("IP: "+get_ip(), id="ip")
        yield Static("PORT: 9999", id="puerto")
        yield Static("Presione 'ESC' para Salir", id="any-key")
        yield Button.error("VER CONEXION")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
           global server, encoder, client, addr, done
           encoder = Hamming_CRC()
           server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           server.bind((get_ip(), 9999))
           server.listen()
           client, addr = server.accept()
           self.app.push_screen(ChatServer())
          

           


class BSODApp(App):
    CSS_PATH = "./styles/server.tcss"
    SCREENS = {"bsod": BSOD()}
    BINDINGS = [("s", "push_screen('bsod')", "BSOD")]
    
    def compose(self)->ComposeResult:
     yield Label('BIENVENIDO',id='bienvenido')
     yield Label('presione S para iniciar el servidor', id='inicio')


if __name__ == "__main__":
    app = BSODApp()
    app.run()