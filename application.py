from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
import logging
import os
from pymongo import MongoClient

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=["GET"])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review', methods=["POST", "GET"])
@cross_origin()
def result():
    if request.method == "POST":
        try:
            query = request.form['content'].replace(" ", "")

            # Directory for saving images
            save_dir = 'images'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
            main_url = f"https://www.google.com/search?q={query}&sca_esv=ca2c68be96a7cdb5&udm=2&sxsrf=ADLYWIJJNCfiG1r1kSUoYvhGnbgA2AHk7w%3A1730772335057&ei=b30pZ4aXA5Ce4-EPyY-eqQM&ved=0ahUKEwjGit-xjcSJAxUQzzgGHcmHJzUQ4dUDCBA&oq=car&gs_lp=EgNpbWciA2NhcjINEAAYgAQYsQMYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTINEAAYgAQYsQMYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBTIKEAAYgAQYQxiKBUjISFDcBFiHPXAEeACQAQKYAbMCoAH6CKoBBzAuMi4yLjG4AQzIAQD4AQGYAgagArUEqAIKwgIGEAAYBxgewgIIEAAYBxgKGB7CAg4QABiABBixAxiDARiKBcICBxAjGCcY6gLCAgQQIxgnwgILEAAYgAQYsQMYgwGYAwmIBgGSBwc0LjAuMS4xoAe9Gg&sclient=img"
            response = requests.get(main_url, headers=headers)
            soup = bs(response.content, 'html.parser')

            image_tags = soup.find_all('img')
            if image_tags:
                del image_tags[0]  # Removing the first image tag if it's not needed

            # Store images and save data for MongoDB
            image_list = []
            for i, img_tag in enumerate(image_tags):
                image_url = img_tag.get('src')
                if image_url:
                    image_data = requests.get(image_url).content
                    myDict = {"Index": i, "Image": image_url}
                    image_list.append(myDict)

                    # Save image locally
                    with open(os.path.join(save_dir, f"{query}_{i}.jpg"), "wb") as f:
                        f.write(image_data)

            # MongoDB Connection and Insertion
            client = MongoClient("mongodb+srv://saman_323:saman323@cluster0.9i3r4fz.mongodb.net/")
            db = client['Image_Scrapper_take1']
            img_coll = db['Image_Scrapper_take1_coll']
            img_coll.insert_many(image_list)

            logging.info("Images loaded and saved to MongoDB successfully.")
            return "Images loaded successfully."
        
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return "An error occurred while loading images."
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
