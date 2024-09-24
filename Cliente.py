from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Input, Button, TextArea
from textual.containers import ScrollableContainer, Horizontal, Center
import platform
import os
import re

import socket
import sys
from Hamming_CRC import Hamming_CRC

encoder = Hamming_CRC()
client = None
ip_addr = None
shared_key = '1010'

def get_ip():
    os_system = platform.system()

    if os_system == 'Windows':
        hostname = socket.gethostname()
        IPaddrs = socket.gethostbyname(hostname)
        return IPaddrs
    else:
        command_stream = os.popen('ifconfig -a')
        command_output = command_stream.read()
        ip_regex_pattern = re.compile(r'inet (\d+\.\d+\.\d+\.\d+)')
        matches = ip_regex_pattern.findall(command_output)

        ip_addresses = [ip for ip in matches if ip != '127.0.0.1']
        if ip_addresses:
            return ip_addresses[0]
        else:
            return 'No-found IP'



# done = False


class EnviarInfo(Screen):
     
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mensaje_input = Input(id="mensaje", placeholder="MENSAJE", type="text")
        # self.textArea = TextArea.code_editor("", id="area")
        # self.text_label = Label("", id="text_label")
        self.text_corregido = Label("TRUE",id="label_error_corregido")
        self.text_indice = Label("Posicion 31",id="label_indice_corregido")
        self.text_servidor = Label("Recibido",id="label_servidor")
        self.text_error = Label("",id="label_error")
     
     def compose(self) -> ComposeResult:
        yield ScrollableContainer(
             Center(
             Label("CONECTADO CORRECTAMENTE, BIENVENIDO AL SERVER!!!", id="msg_bienvenida"),
             Label("ESCRIBA EL MENSAJE A ENVIAR:)", id="msg_text"),
             id="center-texto"
             ),
             Horizontal(
                 self.mensaje_input,
                 Button.success(id="enviar", label="ENVIAR"),
             ),
             Center(
                 Label("ERROR CORREGIDO:"),
                 self.text_corregido,
                 Label(""),
                 Label("INDICE EN DONDE FUE CORREGIDO EL ERROR:"),
                 self.text_indice,
                 Label(""),
                 Label("RESPUESTA DEL SERVIDOR:"),
                 self.text_servidor,
                 self.text_error,
                 id="center-text"
             ),
             Center(
             Button.error(id="volver", label="DESCONECTARSE"),
             id="center-volver"
             ),
             
             id="contenedor_todo"
         )
        
     def on_button_pressed(self, event: Button.Pressed) -> None:
         if event._sender.id == "volver":
          client.close()
          self.app.pop_screen()
         if event._sender.id == "enviar":
            msg_to_send = self.mensaje_input.value
            msg_to_send = encoder.string_to_bin(msg_to_send)
            crc_code = encoder.CRC_code(msg_to_send, shared_key)
            msg_to_send = encoder.hamming_codification(msg_to_send)
            msg_to_send = encoder.generate_err((msg_to_send))
            msg_to_send = msg_to_send + crc_code     
            client.send(msg_to_send.encode('utf-8'))
            msg_recieved = client.recv(1024).decode('utf-8')
            # self.text_label.update(msg_recieved)
            raw_message = encoder.get_rawData(msg_recieved[0:len(msg_recieved)-len(shared_key)+1])
            crc_recieved = msg_recieved[len(msg_recieved)-len(shared_key)+1:]
            #error = encoder.decode_CRC(raw_message, shared_key)
            error = encoder.decode_CRC(raw_message+crc_recieved, shared_key)
            if not error == None:
                msg_recieved, error_corrected, err_idx = encoder.hamming_decode(msg_recieved[0:len(msg_recieved)-len(shared_key)+1])
                self.text_corregido.update(str(error_corrected))
                self.text_indice.update(str(err_idx))
                self.text_servidor.update(str(msg_recieved))
            else:
                self.text_error.update(encoder.bin_to_string(raw_message))
                self.text_corregido.update("")
                self.text_indice.update("")
                self.text_servidor.update("")
                pass
            
     

class BSOD(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    def compose(self) -> ComposeResult:
             yield ScrollableContainer(EnviarInfo(), id="enviar")
    

class Formulario(Static):
      
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ip_input = Input(id="ip", placeholder="IP", type="text", value=get_ip())
        self.port_input = Input(id="port", placeholder="PORT", type="number", max_length=5, value="9999")
     
      def compose(self) -> ComposeResult:
           yield ScrollableContainer(
            Label("BIENVENIDO, CONECTESE A UN SERVIDOR"),
            self.ip_input,
            self.port_input,
            Button.error(id="send-btn", label="Conectarse al Servidor"),
            Label(id="output"),
      )
    
      def on_button_pressed(self, event: Button.Pressed) -> None:
         global encoder, client
         if event._sender.id == "send-btn":
            try:
              encoder = Hamming_CRC()
              client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              client.connect((self.ip_input.value,int(self.port_input.value)))
              self.app.push_screen(EnviarInfo())
            except Exception as e:
              print(f"Error: {e}")
              
          #  shared_key = '1010'
           


class App(App):
    CSS_PATH = "./styles/cliente.tcss"
    SCREENS = {"bsod": BSOD()}
    BINDINGS = [("s", "push_screen('bsod')", "BSOD")]
    def compose(self) -> ComposeResult:
             yield ScrollableContainer(Formulario(), id="initial-container")
        


if __name__ == "__main__":
    app = App()
    app.run()