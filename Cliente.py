#TUI imports
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, Input, Button, TextArea
from textual.containers import ScrollableContainer, Horizontal, Center
#Miscellaneous
import platform
import os
import re
#Networking/Communication imports
import socket
import sys
from Hamming_CRC import Hamming_CRC


