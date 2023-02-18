import os
import json
from pydub import AudioSegment
import whisper
import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import streamlit as st


def transcribe (audio):
    model = whisper.load_model("medium") # You can choose between ["tiny", "base", "small", "medium", "large"]
    transcription = model.transcribe(get_Audio_Path(audio))
    return transcription


def convert_ogg_to_mp3(ogg_file_path, mp3_file_path): # Used for WhatsApp Audios
    given_audio = AudioSegment.from_file(ogg_file_path, format="ogg")   
    given_audio.export(mp3_file_path, format="mp3") # saves .ogg file as .mp3 file

def get_Audio_Path(audio): 
    if audio.type == "ogg": #.ogg files are for example Whatsapp Audio Files
        name = str(audio.name).split(".")[0] # Gets the name of the uploaded file 
        convert_ogg_to_mp3(audio.name, name + ".mp3") # Converts .ogg to .mp3
        return name + ".mp3" # Returns the .mp3 path
    return audio.name # Returns the path 
        
def postJsonInSlack(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__)) + "\\"
    slackid = ....... # The ID of your Slack Bot (Deleted from here: You have to put your own!)
    client = WebClient(slackid)
    
    # The Channel where you want to post 
    channel_id = "#botcreate"   # Here you can automize more


    # Read contents of text file
    with open(current_dir + filename, "r") as f:
        file_contents = str(json.load(f))

    # Post contents of text file in Slack channel
    try:
        response = client.chat_postMessage( channel=channel_id, text= " *Eure Zusammenfassung vom XX.XX.XXXX um XX Uhr* \n"+ file_contents )
        print("File posted successfully in Slack channel")
    except SlackApiError as e:
        print("Error posting file: {}".format(e))    
    
def getAnswer(transcript, filename):
    # Get Environment Variable
    openai.api_key = ............

    # Create a Prompt what GPT-3 should do 
    prompt ="Folgendes Transkript stammt aus einem Meeting. Bitte fasse die Audio einmal zusammen und gebe danach die Todos Stichpunktartig aus, die sich in dem Meeting ergeben haben: \n \" " + transcript + " \" " #GERMAN VERSION
    #prompt = "The following transcript is from a meeting. Please summarise the audio once and then bullet point the todos that came up in the meeting: \n \" " + transcript + " \" " #ENGLISCH VERSION
    
    
    # Define the Setting for GPT-3
    model_engine = "text-davinci-003"   
    temperature = 0.9   
    max_tokens = 2048

    # Get an response from GPT-3
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    # Get the first Response and clean the Data
    resp = response.choices[0].text.strip()
    
    # Save the Summary as a json file.
    with open(filename + ".json", "w") as file:
        json.dump(resp, file)

    # Return the response
    return resp



st.title("MeetSum - Summarize your Meetings")

# Upload audio file
st.subheader("Upload Audio")
audio = st.file_uploader("", type=["wav", "mp3", "m4a", "ogg"])
# Upload Summary file
st.subheader("Upload Summary")
trans = st.file_uploader("", type=["json"])

# Playing Uploaded Audio
st.sidebar.header("Play Original Audio")
st.sidebar.audio(audio)

# Transcribing, Summarizing and Posting Audio in Slack
if st.sidebar.button("Summarize Meeting"):
    if audio is not None:
        st.sidebar.success("Transcribing Audio")
        transcription = transcribe(audio)
        st.sidebar.success("Transcription Succeed")
        st.sidebar.markdown(transcription["text"])
        summary = getAnswer(transcription["text"], str(audio.name).split(".")[0])  
        st.markdown(summary) 
        postJsonInSlack(str(audio.name).split(".")[0] + ".json") 
        st.success("Summary Posted in Slack channel")
    else:
        st.sidebar.error("Please Upload Audio file first")
        
    
# Just Posting uploaded Summary in Slack (So you dont have to pay again for GPT-3) 
if st.sidebar.button("Upload Summary & Post"):
    if trans is not None:
        st.success("Uploading Script")
        postJsonInSlack(trans.name)
    else:
        st.sidebar.error("No Transcript Uploaded yet")




