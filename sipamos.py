
import sys
import pjsua
import threading
import wave
from time import sleep


def log_cb(level, str, len):
    print str,

class MyAccountCallback(pjsua.AccountCallback):
    sem = None

    def __init__(self, account=None):
        pjsua.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

def cb_func(pid) :
    print '%s playback is done' % pid
    current_call.hangup()


# Callback to receive events from Call
class MyCallCallback(pjsua.CallCallback):

    def __init__(self, call=None):
        pjsua.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global current_call
        global in_call
        print "Call with", self.call.info().remote_uri,
        print "is", self.call.info().state_text,
        print "last code =", self.call.info().last_code, 
        print "(" + self.call.info().last_reason + ")"
        
        if self.call.info().state == pjsua.CallState.DISCONNECTED:
            current_call = None
            print 'Current call is', current_call

            in_call = False
        elif self.call.info().state == pjsua.CallState.CONFIRMED:
            #Call is Answred
            print "Call Answred"
            wfile = wave.open("message.wav")
            time = (1.0 * wfile.getnframes ()) / wfile.getframerate ()
            print str(time) + "ms"
            wfile.close()
            call_slot = self.call.info().conf_slot
            self.wav_player_id=pjsua.Lib.instance().create_player('message.wav',loop=False)
            self.wav_slot=pjsua.Lib.instance().player_get_slot(self.wav_player_id)
            pjsua.Lib.instance().conf_connect(self.wav_slot, call_slot)
            sleep(time)
            pjsua.Lib.instance().player_destroy(self.wav_player_id)
            self.call.hangup()
            in_call = False

    # Notification when call's media state has changed.
    def on_media_state(self):
        if self.call.info().media_state == pjsua.MediaState.ACTIVE:
            print "Media is now active"
        else:
            print "Media is inactive"

# Function to make call
def make_call(uri):
    try:
        print "Making call to", uri
        return acc.make_call(uri, cb=MyCallCallback())
    except pjsua.Error, e:
        print "Exception: " + str(e)
        return None


lib = pjsua.Lib()

try:
    lib.init(log_cfg = pjsua.LogConfig(level=4, callback=log_cb))
    lib.create_transport(pjsua.TransportType.UDP, pjsua.TransportConfig(5080))
    lib.set_null_snd_dev()
    lib.start()
    lib.handle_events()

    acc_cfg = pjsua.AccountConfig()
    acc_cfg.id = "sip:USERNAME@YOURSIPSERVER.COM"
    acc_cfg.reg_uri = "sip:YOURSIPSERVER.COM"
    acc_cfg.proxy = [ "sip:PROXY.YOURSIPSERVER.COM;lr" ]
    acc_cfg.auth_cred = [ pjsua.AuthCred("*", "YOURUSERNAME@YOURSIPSERVER.COM", "YOURPASSWORD") ]


    acc_cb = MyAccountCallback()
    acc = lib.create_account(acc_cfg, cb=acc_cb)
    
    acc_cb.wait()

    print "\n"
    print "Registration complete, status=", acc.info().reg_status, \
          "(" + acc.info().reg_reason + ")"
    

    #YOURDESTINATION is landline or mobile number you want to call
    dst_uri="sip:YOURDESTINATION@YOURSIPSERVER.COM"

    in_call = True
    lck = lib.auto_lock()
    current_call = make_call(dst_uri)
    print 'Current call is', current_call
    del lck

    #wait for the call to end before shuting down
    while in_call:
        pass
    #sys.stdin.readline()
    lib.destroy()
    lib = None

except pjsua.Error, e:
    print "Exception: " + str(e)
    lib.destroy()

