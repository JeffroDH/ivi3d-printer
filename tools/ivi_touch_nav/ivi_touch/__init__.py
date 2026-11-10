"""ivi_touch - screen-aware virtual-touch navigation for the IVI3D touchscreen app.

Runs on the Mac (next to ivi_bridge.py); talks to the A33 over SSH.  On the A33 only the static
`ivitap2` helper (in /tmp) and BusyBox dd/gzip are used.  See README.md.
"""
__version__ = "0.2.0"
