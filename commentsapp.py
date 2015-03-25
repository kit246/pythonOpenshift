from flask import Flask, render_template, url_for, request, flash, session
import random
import time
import os

app = Flask(__name__)

@app.route('/')
def display_home():
	return render_template("home.html",
							the_title="Welcome to Kamil's word game",
							playurl=url_for("play"),
							hsurl=url_for("showHighScore") )

@app.route('/play')
def play():
	with open(os.path.dirname(os.path.realpath(__file__))+"/files/source.txt") as source:
		lines = source.read().splitlines()
	r = random.randint(0, len(lines))
	session['timeStart'] = time.time()
	return render_template("enter.html",
							the_title="Play a word game",
							source= lines[r],
							the_save_url=url_for("saveformdata"),
							home_link=url_for("display_home") )

@app.route('/saveform', methods=["POST"])
def saveformdata():
	words = request.form.getlist('input[]')
	source = request.form['source']
	b=True
	properWords = []
	newWords = []
	with open(os.path.dirname(os.path.realpath(__file__))+"/files/words.txt") as wordFile:
		properWords = wordFile.read().splitlines()
	charsS = list(source)
	for word in list(words):
		word = word.strip().lower()
		if not word:
			b = False
			flash("You didn't enter a word!")
		elif not word in properWords:
			b = False
			flash("Not a proper word: "+word)
		elif word in newWords:
			b = False
			flash('You already entered "'+word+'"')
		elif not set(charsS).issuperset(set(list(word))):
			b = False
			flash(word+" is not present in "+source)
		else:
			flash('"'+word + '" is a proper word')
		newWords.append(word)
	if 'timeStart' in session:
		if b:
			session['timeTaken'] = round(time.time() - session['timeStart'],3);
			return render_template("tellmeName.html", the_title="You won! Tell me your name please.", t=str(session['timeTaken']), home_link=url_for("display_home"), save_url=url_for("saveHighScore") )
		return render_template("thanks.html", the_title="Thanks!", mess= 'You lost. Learn some english and try again!', home_link=url_for("display_home"), tryAgain=url_for("play") )
	else:
		return render_template("thanks.html", the_title="Thanks!", mess= 'Error occured. Try again!', home_link=url_for("display_home"), tryAgain=url_for("play") )


@app.route('/saveHighScore', methods=["POST"])
def saveHighScore():
	name = request.form['name'] or "anonymous"
	hsDict = []
	pos = 1
	with open(os.path.dirname(os.path.realpath(__file__))+"/files/highScores.txt") as hsFile:
		hsDict = hsFile.readlines()
	hsDict = [hsDict for hsDict in hsDict if hsDict != "\n"]	# list comprehension; no empty lines
	nhsDict = []
	for line in hsDict:
		line = line.split()
		nhsDict.append([ round(float(line[0]), 2), line[1] ])
	hsDict = nhsDict
	if 'timeTaken' in session:
		tempTime= round( float( session['timeTaken']))
		for line in hsDict:
			if tempTime<=line[0]:
				break
			pos += 1
		hsDict.append([tempTime, name])
		hsDict = sorted(hsDict, key=lambda item: item[0])	#sort 2d list on first element=time
		stringSave = ""
		for line in hsDict:
			stringSave = stringSave + str(line[0]) + "\t"+ line[1] + "\n"
		hsFile = open(os.path.dirname(os.path.realpath(__file__))+"/highScores.txt", "w")
		print(stringSave, file=hsFile, end='')
		session.clear()
	i=1
	table = []
	for line in hsDict:
		if i>10:
			break
		table.append([str(i),line[1], str(line[0])+" sec"])
		i+=1
	if pos:
		return render_template("highScores.html", the_title="Top Ten", home_link=url_for("display_home"), position=pos ,lis=table )
	return render_template("highScores.html", the_title="Top Ten", home_link=url_for("display_home"),lis=table )

@app.route('/showHighScore')
def showHighScore():
	table = []
	i=1
	with open(os.path.dirname(os.path.realpath(__file__))+"/files/highScores.txt") as hsFile:
		for line in hsFile:
			if i > 10:
				break
			line = line.split("\t",2)
			table.append([str(i),line[1],line[0]+" sec"])
			i+=1
	return render_template("highScores.html", the_title="Top Ten", home_link=url_for("display_home") ,lis=table)

app.config['SECRET_KEY'] = 'thisismysecretkeywhichyouwillneverguesshahahahahahahaha'
if __name__ == '__main__':
	app.run(debug=True, port=80)