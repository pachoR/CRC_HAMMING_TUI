from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Label, LoadingIndicator, Button, Switch
from textual.containers import ScrollableContainer, Container, Horizontal, Vertical, Center
import socket
import platform
import os
import re
from Hamming_CRC import Hamming_CRC
