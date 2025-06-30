from app import app
from flask import render_template, request, redirect, url_for, session
import base64
import random
import os
from werkzeug.utils import secure_filename
from datetime import datetime 
 
UPLOAD_FOLDER = 'app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def simulate_ia_prediction():
    return random.choice(["Pleine", "Vide"])

@app.route('/')
def home():
    return render_template('accueil.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        session.clear()

        file = request.files.get('file')
        choice = request.form.get('choice')
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        if not file or file.filename == '' or not choice:
            return redirect(url_for('upload'))
        
        now = datetime.now()
        if date_str and time_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                time_obj = datetime.strptime(time_str, "%H:%M").time()
                if date_obj > now.date() or (date_obj == now.date() and time_obj > now.time()):
                    return redirect(url_for('upload'))
            except ValueError:
                return redirect(url_for('upload'))

        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(file.filename)


        # Sauvegarde physique du fichier image dans le dossier /static/uploads/
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Stockage dans la session : seulement le chemin relatif
        session['image_path'] = f'uploads/{filename}'
        session['location'] = request.form.get('location')
        session['date'] = date_str
        session['time'] = time_str
        session['notes'] = request.form.get('notes')
        session['choice'] = choice

        if choice == 'IA':
            session['prediction'] = simulate_ia_prediction()
        else:
            session['prediction'] = choice

        return redirect(url_for('annotate'))

    return render_template('upload.html')


@app.route('/annotate')
def annotate():
    if 'image_path' not in session:
        return redirect(url_for('upload'))

    image_info = {
        "location": session.get('location'),
        "date": session.get('date'),
        "time": session.get('time'),
        "notes": session.get('notes'),
        "choice": session.get('choice'),
        "prediction": session.get('prediction'),
        "image_url": url_for('static', filename=session['image_path'])
    }

    return render_template('annotate.html', image_info=image_info)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/greenit')
def greenit():
    return render_template('greenit.html')


@app.route('/help')
def help():
    return render_template('aide.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')
