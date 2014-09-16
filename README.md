sipamos
=======

Simple python script that makes a call, plays a wave and disconnects using pjsip pythion lib (http://www.pjsip.org/).

Requires the installation of the pjsip lib and pjsua python module. For more info on how to do that go to : http://trac.pjsip.org/repos/wiki/Python_SIP/Build_Install

Just edit sipamos.py to change your sip account settings and the destination number and run the script.

It will call the destination defined on dst_uri, play the file message.wav when the call is answered by the destination and hangup in the end.

The configurations presented are the ones i use for my ISP sip account (vodafone.pt)