import json
from random import randint

#Phonetic pronunciations of mispronounced words
telugu_phonetic_ssml = "<phoneme alphabet='ipa' ph='/ˈtɛluɡuː/'>telugu</phoneme>"
virijallu_phonetic_ssml = "<phoneme alphabet='ipa' ph='/ˈviridʒɐlluː/'>virijallu</phoneme>"
bhakti_phonetic_ssml = "<phoneme alphabet='ipa' ph='/bhɐkθi/'>bhakthi</phoneme>"

#HTTPS stream urls of telugu radio streams
station_urls = {
                f"london {telugu_phonetic_ssml} radio": "https://c8.radioboss.fm/stream/33", 
                "air tirupati": "https://air.pc.cdn.bitgravity.com/air/live/pbaudio032/chunklist.m3u8", 
                "all india radio visakhapatnam": "https://air.pc.cdn.bitgravity.com/air/live/pbaudio080/chunklist.m3u8",
                "all india radio kurnool": "https://air.pc.cdn.bitgravity.com/air/live/pbaudio052/chunklist.m3u8", 
                "a.p. 9 f.m. radio": "https://stream.ap9fm.in/radio/8000/radio.mp3",
                "radio city bhakti": "https://prclive4.listenon.in/Bhakti",
                "virijallu": "https://13683.live.streamtheworld.com/SAM02AAC10_SC"
            }

station_names = {
                 "#1":f"london {telugu_phonetic_ssml} radio",
                 "#2":"air tirupati",
                 "#3":"all india radio visakhapatnam",
                 "#4":"all india radio kurnool",
                 "#5":"a.p. 9 f.m. radio",
                 "#6":"radio city bhakti",
                 "#7":"virijallu"
            }

def build_response(speech):
    return {
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "SSML",
                        "ssml": speech,
                        "playBehavior": "REPLACE_ENQUEUED"      
                    },   
                },
               "shouldEndSession": True
            }

def indian_pronounciation(speech):
    return "<speak><voice name='Aditi'><lang xml:lang='en-IN'>"+speech+"</lang></voice></speak>"

def play_stream(station_name, stream_url):
    speech_snippet = "Starting <prosody rate='110%'>"+station_name+"</prosody>"
    if("radio" not in station_name):
        speech_snippet = speech_snippet + " radio"
    speech_response = indian_pronounciation(speech_snippet)
    return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                  "type": "SSML",
                  "ssml": speech_response,
                  "playBehavior": "REPLACE_ENQUEUED"      
                },  
                "directives": [
                    {
                        "type": "AudioPlayer.Play",
                        "playBehavior": "REPLACE_ALL",
                        "audioItem": {
                            "stream": {
                                "token": "12345",
                                "url": stream_url,
                                "offsetInMilliseconds": 0,
                            }
                        }
                    }
                ],
                "shouldEndSession": True
            }
        }
        
def handle_intent(request):
    intent_name = request["intent"]["name"]
    if(intent_name in [
                        "AMAZON.StopIntent",
                        "AMAZON.PauseIntent",
                        "AMAZON.CancelIntent",
                        "AMAZON.PreviousIntent",
                        "AMAZON.ShuffleOffIntent",
                        "AMAZON.LoopOffIntent"
                    ]):
        return {
                "version": "1.0",
                "sessionAttributes": {},
                "response": {
                    "directives": [
                        {
                            "type": "AudioPlayer.Stop"
                        }
                    ],
                    "shouldEndSession": True
                }
            }
    elif(intent_name in [
                            "AMAZON.ResumeIntent",
                            "AMAZON.StartOverIntent",
                            "AMAZON.RepeatIntent",
                            "AMAZON.ShuffleOnIntent",
                            "AMAZON.LoopOnIntent",
                            "AMAZON.NextIntent"
                        ]):
        station_index = "#" + str(randint(1, 6))
        station_name = station_names[station_index]
        station_url = station_urls[station_name]
        return play_stream(station_name, station_url)
    elif(intent_name == "PlayRadio"):
        intent = request["intent"]
        station_index = intent["slots"]["stationNumber"]["value"].lower()
        station_name = station_names[station_index]
        station_url = station_urls[station_name]
        return play_stream(station_name, station_url)
    elif(intent_name == "PlayRandomRadio"):
        station_index = "#" + str(randint(1, 6))
        station_name = station_names[station_index]
        station_url = station_urls[station_name]
        return play_stream(station_name, station_url)
    elif(intent_name == "DescribeRadio"):
        intent = request["intent"]
        station_index = intent["slots"]["stationNumber"]["value"].lower()
        explanation = "Station " + station_index + " is " + station_names[station_index]
        return build_response(indian_pronounciation(explanation))

def handle_session_end_request():
    return {
        "version": "1.0",
        "response": {
            "shouldEndSession": True
        }
    }

def lambda_handler(event, context):
    if(event["request"]["type"] == "LaunchRequest"):
        return build_response("<speak>Please ask for a station number when starting the radio.</speak>")
    elif(event["request"]["type"] == "IntentRequest"):
        return handle_intent(event["request"])
    elif(event["request"]["type"] == "SessionEndedRequest"):
        return build_response("<speak>Please ask for a station number when starting the radio.</speak>")
