import subprocess, os, sys

"""
    CommandMap class

    This class is used in conjunction with config.json to configure the bot's behavior.
"""

class CommandMap(object):
    def __init__(self, config):
        self.config = config

    def format(self, text):
        return '\n```'+ text +'```\n'

    def sayHello(self, args):
        return 'Hello, ' + args

    def getHelp(self, args):
        if not any(c.isalpha() for c in args):
            return '*help*: ' + self.config['commands']['help']['help']
        elif args.replace(' ', '') in self.config['commands']:
            return '*'+ args +':* '+ self.config['commands'][args.replace(' ', '')]['help']
        return 'No help information found for ' + args

    def dig(self, args):
        if any(c.isalpha() for c in args):
            args = args.split(' ')

            for i,arg in enumerate(args):
                if arg.find('|') > 0:
                    args[i] = arg[arg.find('|')+1:arg.find('>')]

            args.insert(0, 'dig')
            records = str(subprocess.check_output(args))

            return self.format(records)
        else:
            return '*dig:* No domain specified.'

    def ping(self, args):
        if any(c.isalpha() for c in args):
            args = args.split(' ')

            args.insert(0, 'ping')
            args.insert(1, '-c')
            args.insert(2, '3')

            for i,arg in enumerate(args):
                if arg.find('|') > 0:
                    args[i] = arg[arg.find('|')+1:arg.find('>')]

            results = str(subprocess.check_output(args))

            return self.format(results)
        else:
            return '*ping:* No domain specified.'

    def getHostname(self, args):
        return self.format(str(subprocess.check_output(["hostname"])))

    def diskStatus(self, args):
        return self.format(str(subprocess.check_output(["df","-h"])))

    def ifconfig(self, args):
        return self.format(str(subprocess.check_output(["ifconfig"])))

    def syslog(self, args):
        return self.format(str(subprocess.check_output(["tail","/var/log/syslog","-n","100"])))

    def authlog(self, args):
        return self.format(str(subprocess.check_output(["tail","/var/log/auth.log","-n","100"])))

    def lsof(self, args):
        return self.format(str(subprocess.check_output(["lsof","-i"])))

    def getUptime(self, args):
        return self.format(str(subprocess.check_output(["uptime"])))

    def sysinfo(self, args):
        return self.format(str(subprocess.check_output(["landscape-sysinfo"])))

    def reboot(self, args):
        msg = str(subprocess.check_output(["shutdown","-r","+2"]))
        return 'Reboot scheduled in 2 minutes. ' + self.format(msg)

    def undoReboot(self, args):
        msg = str(subprocess.check_output(["shutdown","-c"]))
        return 'Reboot cancelled! ' + self.format(msg)

    def listCommands(self, args):
        commands = list()
        for key in self.config['commands']:
            commands.append(key)
        return 'Available commands are: ' + ', '.join(commands)

    def killClient(self, args):
        exit(0)
