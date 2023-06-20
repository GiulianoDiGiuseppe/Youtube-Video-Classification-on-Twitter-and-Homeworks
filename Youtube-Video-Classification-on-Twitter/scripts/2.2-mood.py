import tweetnlp 
import pandas as pd 
import sys

#mood choice
mood = sys.argv[1]
tipo_mood = mood

#for the sentiment model we want to store both the neutral and negative mood
if mood=="sentiment":
    if sys.argv[2] == "neutral":
        tipo_mood = "neutral"
    else:
        tipo_mood = "negative"

#model loading
model = tweetnlp.load_model(mood) 

#csv loading
df = pd.read_csv("merged_yt_collection_preprocessedtxt.csv")

#get the mood score for the selected choice and append it in a file
def get_mood(model, text, tipo_mood):
    output_file = f"{tipo_mood}.txt"
    output = model.predict(text, return_probability = True)
    if output_file is not None:
        with open(output_file, "a") as file:
            file.write(str(output["probability"][tipo_mood]) + "\n")

text_list = df["preprocessed_text"].to_list()
for text in text_list:
     get_mood(model, text , tipo_mood)