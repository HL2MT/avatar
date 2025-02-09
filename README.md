# Avatar
This pipeline is designed for ASR+NLP+TTS task.
In this user can talk to AI chatbot in hindi.
This pipeline is tested on python 3.12

# How to use

pip install requirements.txt

# Then
replace with your groq api key in .env file

# Then
streamit run speech_to_speech_with_history.py

# Note
This is just a POC with open source models whisper for Speech to text and llama for text to text,these models support hindi and good to go but as these are not designed for specific hindi conversation ,sometime they doesn't work 100% accurately.So better use SFT with Preference
Alignment according to avatar design.Models like gemma 2 or llama with max 7b perameters is best for these conversational task with enough perameters these models are fast on time for first token as well.And use inference on groq cloud for real time conversation.

For speech to text gtts is used it is good go but have some limitations like ratelimit as being in a library it can't use controled for rate limitations,as it is little slow fo instant conversation so better use eleven lab models which are great in hindi and fastest as well.

Also history for every  conversation is summarised to keep conversation engaged with memory.


# Future pipeline for conversational avatar
Whisper(SFT on hindi)+llama or gemma 2(SFT on hindi)+ elevenlab model

or 
model merging for single model (speech-to-speech)(inference on groq cloud with LPU)

# Spoiler 
Both of my speakers and mike are not working properly(poor guy),so I used microphone from my earphones and speakers from external connected speakers,so I was the reason ,sometimes it lags for few microsecs while speaking due to changing mike and speakers setting everytime.
