from subprocess import Popen, PIPE
import re

class SnortAlert:
    def __init__(self, gid, sid, rev, msg):
        #Trust only the sid...
        self.sid = sid
        self.gid = gid
        self.rev = rev
        self.msg = msg

    def __str__(self):
        return "[**] [%s:%s:%s] %s [**]" % (self.gid, self.sid, self.rev, self.msg)

class TestSnort:
    
    def __init__(self, snort_conf, pcap, loaded_sids):
        self.logfile = "/var/log/snort/r2a.log"
        self.alerts = []
        self.alert_sids = []
        self.snort_conf = snort_conf
        self.pcap = pcap
        self.loaded_sids = loaded_sids
        self.cmd    = "snort -c %s -K none -q -A console -r %s" % (self.snort_conf, self.pcap)

    def run(self):
        p = Popen(self.cmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        stdout = stdout.splitlines()
        sig_reg = re.compile(r'\[\*\*\]\s+\[(?P<gid>\d+):(?P<sid>\d+):(?P<rev>\d+)\]\s*(?P<msg>.*)\s*\[\*\*\]')
    
        for alert in stdout:
            m = sig_reg.search(alert)
            if m:
                try:
                    s = SnortAlert(m.group("gid"),m.group("sid"),m.group("rev"),m.group("msg"))
                    self.alerts.append(s)
                    self.alert_sids.append(s.sid)
                except:
                    print "Error parsing alert: %s" % alert

        if len(self.alerts) == len(self.loaded_sids):
            print "Successfully alerted on all loaded rules"
        elif len(self.alerts) < len(self.loaded_sids):
			f = open("output/fail.log",'w')
			f2 = open("output/success.log",'w')
            missed = len(self.loaded_sids) - len(self.alerts)
            print "Failed to alert on %d rules" % missed
            for sid in self.loaded_sids:
                if not sid in self.alert_sids:
					f.write(sid + "\n")
				if sid in self.alert_sids:
					f2.write(sid + "\n")
					
			f.close()
			f2.close()
            
    def readSnortAlerts(self):
        #12/21-16:14:50.971883  [**] [1:20000000:1] Snort alert [**] [Priority: 0] {TCP} 192.168.0.1:9001 -> 1.1.1.1:80
        #                            [gid:sid:rev]
        p = re.compile(r'\[\*\*\]\s+\[(?P<gid>\d+):(?P<sid>\d+):(?P<rev>\d+)\]\s*(?P<msg>.*)\s*\[\*\*\]')
        f = open(self.logfile, "r")
        for line in f.read().splitlines():
            m = p.search(line)
            if m:
                try:
                    self.alerts.append(SnortAlert(m.group("gid"),m.group("sid"),m.group("rev"),m.group("msg")))
                except:
                    print "Error parsing alert from " + str(line)

        if len(self.alerts) > 0:
            self.clearLog()

    def printAlerts(self):
        for alert in self.alerts:
            print alert