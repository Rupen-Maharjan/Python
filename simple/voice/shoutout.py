import win32com.client

def speak(names):
    speaker=win32com.client.Dispatch('SAPI.SpVoice')
    for name in names:
        speaker.Speak(f'Shoutout to {name}')


names= input('Please enter names of people using space as a seperator\n: ')

lnames= names.split(' ')

speak(lnames)