# -*- coding: utf-8 -*-

"""
Events from a scene in North by North West


Some ideas about notation:

Events are dictionaries; the parser will sort them, so don't worry if you do not get the ordering right.
We are using short tags to annotate them.

t - beginning in ms
d - duration
e - end

sub - subtitle
x - execute (call a function from the api verbatim)
"""

__author__ = 'joscha'
__date__ = '4/6/16'


script = [
{"t": 4229767, "e": 4231394, "sub": "Hi." },
{"t": 4233563, "e": 4236274, "sub": "-Hot day. -Seen worse."},
{"t": 4238693, "e": 4240820, "sub": "Are you supposed to be meeting someone here?" },
{"t": 4240987, "e": 4244657, "sub": "-Waiting for the bus. Due any minute. -Oh." },
{"t": 4245324, "e": 4248744, "sub": "Some of them crop-duster pilots get rich, if they live long enough." },
{"t": 4249829, "e": 4251372, "sub": "Yeah." },
{"t": 4251914, "e": 4255168, "sub": "And, uh, then your name isn't Kaplan?" },
{"t": 4255835, "e": 4258129, "sub": "Can't say it is, because it ain't." },
{"t": 4258838, "e": 4261424, "sub": "Here she comes. Right on time." },
{"t": 4264719, "e": 4266721, "sub": "-That's funny. -What?" },
{"t": 4266888, "e": 4269640, "sub": "That plane's dusting crops where there ain't no crops." },
{"t": 4503290, "e": 4506669, "sub": "Get out of here! The other tank may blow!" },
{"t": 4517096, "e": 4518597, "sub": "What happened?" },
{"t": 4542288, "e": 4544081, "sub": "Hey!" },
{"t": 4544707, "e": 4546459, "sub": "Come back! Hey!" },
{"t": 4546625, "e": 4551047, "sub": "Come back! Come back! Hey!" }
]