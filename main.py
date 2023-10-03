import asyncio
import re
import whisper
import speech_recognition as sr
import pyttsx3
from EdgeGPT import Chatbot, ConversationStyle

# Create a recognizer object and a wake word variable
recognizer = sr.Recognizer()
BING_WAKE_WORD = "hello"

def get_wake_word(phrase):
    # Checks if voice input has the wake word by converting the all upper case string to lower case and equates strings
    if BING_WAKE_WORD in phrase.lower():
        return BING_WAKE_WORD
    else:
        return None

def synthesize_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

async def main():
    while True:
        # Records with microphones
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print(f"Waiting for wake words 'ok Art'")
            while True:
                audio = recognizer.listen(source)
                try:
                    with open("audio.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    # Using the preloaded tiny_model in whisper
                    model = whisper.load_model("tiny")
                    result = model.transcribe("audio.wav")
                    phrase = result["text"]
                    print(f"You said: {phrase}")

                    wake_word = get_wake_word(phrase)
                    if wake_word is not None:
                        break
                    else:
                        print("Not a wake word. Try again.")
                except Exception as e:
                    # Prints an error if something goes wrong with the transcription
                    print("Error transcribing audio: {0}".format(e))
                    continue

            print("Speak a prompt...")
            synthesize_speech("What can I help you with?")
            audio_prompt = recognizer.listen(source)
                
            try:
                with open("audio_prompt.wav", "wb") as f:
                    f.write(audio_prompt.get_wav_data())
                # Using the preloaded tiny_model in whisper
                model = whisper.load_model("tiny")
                result = model.transcribe("audio_prompt.wav")
                user_input = result["text"]
                print(f"You said: {user_input}")
            except Exception as e:
                # Prints an error if something goes wrong with the transcription
                print("Error transcribing audio prompt: {0}".format(e))
                continue

            bot = Chatbot(cookie_path='cookies.json')
            response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.creative)

            # Filters out the bot's response from the JSON dictionary
            for message in response["item"]["messages"]:
                if message["author"] == "bot":
                    bot_response = message["text"]
                    # Removes the random characters from the string feedback using the regex library
                    bot_response = re.sub('\[\^\d+\^\]', '', bot_response)
                    # Prints the bot's response
                    print("Art's response:", bot_response)

                    # Speak out the response using text-to-speech
                    synthesize_speech(bot_response)

            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())