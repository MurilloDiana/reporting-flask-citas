from flask import Flask, jsonify, render_template
from flask_pymongo import PyMongo
import pandas as pd

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://osder:78575353@cluster0.jdqqlsg.mongodb.net/vet_cristo?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/api/report_cita')
def report():
    try:
        visits = list(mongo.db.visits.find())        
        df_visits = pd.DataFrame(visits)
        df_visits['date'] = pd.to_datetime(df_visits['date'])
        df_reservas = df_visits[df_visits['reserved'] == True]

        citas_atendidas = df_reservas[df_reservas['status'] == 'Atendido'].groupby(df_reservas['date'].dt.date).size()
        citas_canceladas = df_reservas[df_reservas['status'] == 'Cancelado'].groupby(df_reservas['date'].dt.date).size()

        df_citas = pd.DataFrame({
            'Citas Atendidas': citas_atendidas,
            'Citas Canceladas': citas_canceladas
        }).fillna(0)
        df_citas.index = pd.to_datetime(df_citas.index)

        data = {
            'fechas': df_citas.index.strftime('%Y-%m-%d').tolist(),
            'citas_atendidas': df_citas['Citas Atendidas'].tolist(),
            'citas_canceladas': df_citas['Citas Canceladas'].tolist()
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
