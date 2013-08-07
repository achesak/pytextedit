# -*- coding: utf-8 -*-

"""

pytextedit server
For pytextedit version 0.4
Written by Adam Chesak.

This is the server for the collaborative editing in pytextedit.
Use the configuration variables to change the port, host, and 
the file being edited.

Start the server with "python pytextedit_server.py".

"""





############### Configuration ###############
#
# Specifies the port used. Note that if this is
# changed the port in the client will need to
# be changed as well.
conf_port = 14113
#
# Specifies the host name. Set to the empty
# string to use localhost.
conf_host = ""
#
# Specifies the file to edit. Make sure this
# file exists before using.
conf_file = "pytextedit_server_out.txt"
#
# Specifies whether writing to the file is allowed.
conf_write = True
#
# Specifies whether reading from the file is allowed.
conf_read = True
#
# Specifies whether the server should output
# messages to the terminal.
conf_out = True
#
# Specifies whether the server should use a 
# whitelist, a blacklist, or if it should allow
# everyone. Set to 1 for no restrictions, 2 for a
# whitelist, and 3 for a blacklist.
conf_restrict = 1
#
# Specifies the whitelist, if used. This should
# be a list of IP addresses, each in their own string.
conf_whitelist = []
#
# Specifies the blacklist, if used. This should
# be a list of IP addresses, each in their own string.
conf_blacklist = []
#
#############################################






# Import socketserver for creating the server.
# Try the Python3 module, and if that fails 
# use the Python2 module name.
try:
    import socketserver
except ImportError:
    import SocketServer as socketserver
# Import time for getting the time.
import time

# Create the server class.
class PytexteditServer(socketserver.BaseRequestHandler):
    def handle(self):
        """Handle the client."""
        # Check the whitelist, if specified.
        if conf_restrict == 2:
            # If the IP address is not in the whitelist, refuse the request.
            if self.client_address[0] not in conf_whitelist:
                out("pytextedit_server (\"%s\" on %d): connection from %s refused (not whitelisted)" % (conf_host, conf_port, self.client_address[0]))
                self.request.send("w".encode())
                self.request.close()
                return
        # Check the blacklist, if specified.
        if conf_restrict == 3:
            # If the IP address is in the blacklist, refuse the request.
            if self.client_address[0] in conf_blacklist:
                out("pytextedit_server (\"%s\" on %d): connection from %s refused (blacklisted)" % (conf_host, conf_port, self.client_address[0]))
                self.request.send("b".encode())
                self.request.close()
                return
        # Get the mode.
        mode = self.request.recv(1)
        # "t": Test connection.
        if mode == "t":
            # Send confirmation.
            self.request.send("success".encode())
            out("pytextedit_server (\"%s\" on %d): new connection from %s" % (conf_host, conf_port, self.client_address[0]))
        # "r": Read from the file.
        elif mode == "r" and conf_read:
            out("pytextedit_server (\"%s\" on %d): read request recieved from %s" % (conf_host, conf_port, self.client_address[0]))
            try:
                # Read the data.
                data_file = open(conf_file, "r")
                data = data_file.read()
                data_file.close()
                out("pytextedit_server (\"%s\" on %d): read successful for %s" % (conf_host, conf_port, self.client_address[0]))
            except IOError:
                out("pytextedit_server (\"%s\" on %d): read failed for %s" % (conf_host, conf_port, self.client_address[0]))
                data = ""
            # Send the data.
            self.request.send("d".encode() + data.encode())
            out("pytextedit_server (\"%s\" on %d): read request data sent to %s" % (conf_host, conf_port, self.client_address[0]))
        # "w": Write to the file.
        elif mode == "w" and conf_write:
            out("pytextedit_server (\"%s\" on %d): write request recieved from %s" % (conf_host, conf_port, self.client_address[0]))
            # Get the data to write.
            data = ""
            while True:
                data2 = self.request.recv(1024)
                if not data2:
                    break
                else:
                    data += data2
            try:
                # Write the data.
                data_file = open(conf_file, "w")
                data_file.write(data)
                data_file.close()
                out("pytextedit_server (\"%s\" on %d): write successful from %s" % (conf_host, conf_port, self.client_address[0]))
                self.request.send("d".encode())
            except IOError:
                out("pytextedit_server (\"%s\" on %d): write failed from %s" % (conf_host, conf_port, self.client_address[0]))
                self.request.send("f".encode())
                pass
        # Close the connection.
        self.request.close()

# Define the function for output. This is just to remove the need
# for tons of "if" blocks.
def out(text):
    """Prints text to the terminal."""
    # Only do this if output is enabled.
    if conf_out:
        # Get the time.
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print("[%s] %s" % (now, text))

# Print some basic info about the server before it starts.
out("pytextedit_server: using \"%s\" on port %d" % (conf_host, conf_port))
out("pytextedit_server: editing file \"%s\"" % (conf_file))
out("pytextedit_server (\"%s\" on %d): starting..." % (conf_host, conf_port))

# Start the server.
pte_server = socketserver.ThreadingTCPServer((conf_host, conf_port), PytexteditServer)
pte_server.serve_forever()