# export FLASK_APP=app.py and flask run
# export FLASK_DEBUG=1    to restart server after every change
# or use the code    app.run(debug=True)
from flask import Flask, render_template, url_for, redirect, request, Response
from smartvest.preprocessing.preprocessing import *
from smartvest.analytics.analysis import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import sqlite3
import pickle
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def hello():
    if request.method=="POST":
        company_name = request.form['company']
        return redirect(url_for('content', name=company_name))
    else:
        conn = connect_db('./db/smartvest.db')
        cur = list(conn.execute('SELECT * from pop order by count desc;'))[1:]
        return render_template('home.htm', comp_list=cur)

@app.route('/<name>', methods=['GET', 'POST'])
def content(name):
    df = pd.read_csv('./smartvest/company_list/companylist.csv')
    df = df.loc[df['Symbol'] == str(name).upper()][['Symbol', 'Name', 'MarketCap', 'IPOyear', 'Sector']]
    comp_data = df.values.tolist()
    conn = connect_db('./db/smartvest.db')
    cur = conn.execute('SELECT * from pop where symbol = "{}"'.format(str(name).upper()))
    print(cur)
    if sum([len(x) for x in cur]) == 0:
        conn.execute('INSERT INTO pop values("{}", {});'.format(str(name).upper(), 1))
    else:
        conn.execute('UPDATE pop SET count = count + 1 where symbol = "{}";'.format(str(name).upper()))
    conn.commit()
    conn.close()
    return render_template('content.htm', title=f'{name}', data=comp_data)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.htm'), 404

@app.route('/<name>/<filename>.png')
def plot_png(name, filename):
    fig = create_figure(name, filename)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(name, filename):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    data = load_data(name.upper())
    date = (int(data['Date'].values.tolist()[-150][:4]), int(data['Date'].values.tolist()[-1][:4]))
    if filename == 'open_close':
        data = data[['Open', 'Close']].iloc[-150:, :]
        axis.plot(data['Open'], c='r', label='Open')
        axis.plot(data['Close'], c='g', label = 'Close')
    elif filename=='high_low':
        data = data[['High', 'Low']].iloc[-150:, :]
        axis.plot(data['High'], c='c', label='High')
        axis.plot(data['Low'], c='m', label='Low')
    elif filename == 'volume':
        data = data[['Volume']].iloc[-365:, :]
        axis.plot(data.values, c='b', label='Volume', alpha=0.7)
    elif filename == 'forecast':
        data = clean_data(data, ['Date', 'Ex-Dividend', 'Split Ratio', 'Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume'])
        params = (data[['Close']].mean(), data[['Close']].std())
        data = feature_scale(data)
        x_t = data[['Open', 'High', 'Low', 'Volume']].iloc[:-30, :]
        x_v = data[['Open', 'High', 'Low', 'Volume']].iloc[-30:, :]
        y_t = data[['Close']].iloc[30:, :]
        
        if os.path.isfile('./models/' + f'{name}'.upper() + '.sav'):
            file = open('./models/' + f'{name}'.upper() + '.sav', 'rb')
            model = pickle.load(file)
            file.close()
        else:
            model = train_MLP(x_t.values, y_t.values)
            with open('./models/' + f'{name}'.upper() + '.sav', 'wb') as file:
                pickle.dump(model, file)
        y_pred = list(model.predict(x_v))
        
        # rewind = lambda x: x*params[1] + params[0]
        # y_t = y_t.apply(rewind)
        # for ele in y_pred:
        #     y_pred[y_pred.index(ele)] = rewind(ele)
        
        axis.plot([i for i in range(y_t.iloc[-30:, :].shape[0])], y_t.iloc[-30:, :].values, c='y', label='Known prices')
        axis.plot([y_t.iloc[-30:, :].shape[0] + i for i in range(len(y_pred))], y_pred, c='m', label='Predicted Values')
     
    axis.set_xlabel('{} - {}'.format(date[0], date[1]))
    axis.set_ylabel('Price in $')
    axis.set_title(" ".join([x.upper() for x in filename.split('_')]))
    axis.set_xticks([])
    fig.legend()
    return fig

def connect_db(db):
    return sqlite3.connect(db)

if __name__ == '__main__':
    app.run(debug=True)