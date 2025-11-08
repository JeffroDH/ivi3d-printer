# IVI-El-Perdido
API control scripts for the IVI printer, whose betas got shipped before COVID killed the Kickstarter campaign. 

Requirements: 
1. A functional IVI beta printer
2. The IVI slicer software

The beta version of the slicer has a console for issuing g-code commands directly to the printer, but it does not actually point at a functional endpoint on the printer's API. By using Wireshark to sniff the traffic to the printer from the slicer application, I've figured out what is included here. 

This control script is SUPER basic, and really exists just to store this knowledge for future expansion and development. My goal is to get the printer to a state where I can control it with Orca Slicer and/or other popular slicers.  I need to work on the CNC and laser functionality as well, and see if other programs can create compatible gcode for those tool heads.  If you want to help with the project (there might be a dozen people with a version of this printer) I will happily accept it. 

I have not figured out how to execute gcode commands directly from the API, but you can upload gcode to the printer. I derived the TOKEN from the printer configuration section of the slicer software, toward the bottom of the file. There is a much longer key near the top of the JSON, and that is not the correct one. You'll likely need to copy that key into this script in order for it to work with your particular printer.

The web server being used by the printer seems to be Kore. 
