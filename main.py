import csv
import pandas as pd 
from flask import Flask, request, render_template , redirect, session

app = Flask(__name__)
app.secret_key = "OSjuDu8DSv2BDeu2SWHDbjw"

@app.route("/")
def start():
    return render_template("studentteacher.html")

@app.route("/home", methods =['GET','POST'])
def home(): 
    if request.method == "GET":
        session['topic'] = 'ALL'
        posts = get_relevant_posts(session["topic"])
        return render_template("home.html",post_list = posts)
    else: 
        posts = get_relevant_posts("ALL")
        try:
            posts = get_relevant_posts(request.form['subject'])
           
        except: 
            pass
        try:
            if request.form['vote'] == "upvote":
                score = 1
            else: 
                score = -1 
            pid = int(request.form['resource_id'])
            upvote(score,pid)
            posts = get_relevant_posts(session["topic"])
            
        except: 
            pass
        try:
            title = request.form['title']
            subject = request.form['subject']
            upvotes = 0
            if "user" in session:
                postername = session["user"]
            else: 
                postername = "Anon"
            link = request.form['link']
            text = request.form['comment']
            pid = 0
            with open('posts.csv', mode='r', newline='') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in csvfile:
                    pid += 1
            # append the data to the CSV file
            with open('posts.csv', mode='a', newline='') as csv_file:
                fieldnames = ['pid','postername', 'title', 'Subject', 'link','text','Upvotes']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'pid':pid,'postername':postername, 'title': title, 'Subject': subject, 'link': link, 'Upvotes': upvotes,'text': text})
            session["topic"] = request.form["subject"]
            posts = get_relevant_posts(session["topic"])
            
        except: 
            pass
        return render_template("/home.html", post_list = posts)


@app.route('/create_post', methods=['GET','POST'])
def create_post():
    if request.method == "POST":
        # retrieve data from the AJAX call
        title = request.form['title']
        subject = request.form['subject']
        upvotes = 0
        if "user" in session:
            postername = session["user"]
        else: 
            postername = "Anon"
        link = request.form['link']
        text = request.form['comment']
        pid = 0
        with open('posts.csv', mode='r', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvfile:
                pid += 1
        # append the data to the CSV file
        with open('posts.csv', mode='a', newline='') as csv_file:
            fieldnames = ['pid','postername', 'title', 'Subject', 'link','text','Upvotes']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'pid':pid,'postername':postername, 'title': title, 'Subject': subject, 'link': link, 'Upvotes': upvotes,'text': text})

        posts = get_relevant_posts("ALL")
        return render_template("home.html",post_list = posts)
    else: 
        posts = get_relevant_posts("ALL")
        return render_template("home.html",post_list = posts)

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else: 
        session['user'] = request.form['email']
        return redirect("/home")

@app.route('/create_account', methods=['POST','GET'])
def create_account():
    if request.method == "POST":
            # retrieve data from the AJAX call
        status = request.form['status']
        courses = request.form['Course']
        session['course'] = request.form['Course']
        uName = request.form['text']
        session["user"] = uName
        posts = ''
        upvotes = 0

        # append the data to the CSV file
        with open('accounts.csv', mode='a', newline='') as csv_file:
            fieldnames = ['uName','Status', 'Courses', 'Posts', 'Upvotes']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'uName':uName, 'Status': status, 'Courses': courses, 'Posts': posts, 'Upvotes': upvotes})
        return redirect("/home")
    else: 
        return render_template("signup.html")


@app.route('/upvote', methods=['POST'])
def upvote(score,target_pid):
    df = pd.read_csv("posts.csv")
    df.at[target_pid-2, 'votes'] = df.at[target_pid-2, 'votes'] + score
    df.to_csv("posts.csv", index = False)

def checkstatus(name): 
    df = pd.read_csv("accounts.csv")
    filtered_df = df[df['name'] == name]
    if filtered_df.empty:
        return "Guest"
    else: 
        return filtered_df.iloc[0]['status']


def get_relevant_posts(subject):
    correct_posts = []
    with open('posts.csv', 'r') as data:
        for row in csv.DictReader(data):
            if row['Subject'] == subject or subject == "ALL":
                row["pid"] = int(row["pid"])
                row["votes"] = int(row["votes"])
                row["score"] = row["votes"]+row["pid"]*2 
                row["status"] = checkstatus(row["postername"])
                correct_posts.append(row)
    
    
    for current in range(len(correct_posts)):
        max_rel = current
        for i in range(current, len(correct_posts)):
            if correct_posts[i]["score"] > correct_posts[max_rel]["score"]:
                max_rel = i
        temp = correct_posts[current]
        correct_posts[current] = correct_posts[max_rel]
        correct_posts[max_rel] = temp

    sorted_posts = correct_posts
    return sorted_posts
        

if __name__ == '__main__':
    app.run(debug=True,host = '0.0.0.0')

