from flask import Flask, jsonify, request
import pandas as pd
from demographic_filtering import output
from content_filtering import get_recommendations

articles_data = pd.read_csv('articles.csv')
all_articles = articles_data[['url' , 'title' , 'text' , 'lang' , 'total_events']]
liked_articles = []
not_liked_articles = []

app = Flask(__name__)

def assign_val():
    m_data = {
        "url": all_articles.iloc[0,0],
        "title": all_articles.iloc[0,1],
        "text": all_articles.iloc[0,2] or "N/A",
        "lang": all_articles.iloc[0,3],
        "total_events": all_articles.iloc[0,4]/2
    }
    return m_data

@app.route("/get-article")
def get_article():

    article_info = assign_val()
    return jsonify({
        "data": article_info,
        "status": "success"
    })

@app.route("/liked-article")
def liked_article():
    global all_articles
    article_info = assign_val()
    liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

@app.route("/unliked-article")
def unliked_article():
    global all_articles
    article_info = assign_val()
    not_liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

# API to return most popular articles.
@app.route("/popular-articles")
def popular_articles():
    popular_article_data = []
    for index, row in output.iterrows():
      popular_article = {
         "url" : row["url"],
         "title" : row["title"],
         "text" : row["text"],
         "lang" : row["lang"],
         "total_events" : row["total_event"],
      }
      popular_article_data.append(popular_article)
    return jsonify({
       "data" : popular_article_data, "status" : "success"
    })

# API to return top 10 similar articles using content based filtering method.
@app.route("/recommended-articles")
def recommended_articles():
   global liked_articles
   column_name = ["url", "title", "text", "lang", "total_events"]
   recommend = pd.DataFrame(columns = column_name)
   for liked_article in liked_articles:
      output = get_recommendations(liked_article["title"])
      recommend = recommend.append(output)
   recommend.drop_duplicates(subset=["title"], inplace = True)
   recommend_data = []
   for index, row in recommend.iterrows():
      recommend_article = {
         "url" : row["url"],
         "title" : row["title"],
         "text" : row["text"],
         "lang" : row["lang"],
         "total_events" : row["total_event"],
      }
      recommend_data.append(recommend_article)
   return jsonify({
      "data" : recommend_data, "status" : "success",
   })

if __name__ == "__main__":
    app.run()