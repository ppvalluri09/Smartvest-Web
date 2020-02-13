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
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
@app.route('/home', methods=["POST", "GET"])
def hello():
    if request.method=="POST":
        company_name = request.form['company']
        return redirect(url_for('content', name=company_name))
    else:
        return render_template('home.htm')

@app.route('/<name>', methods=['GET', 'POST'])
def content(name):
    df = pd.read_csv('./smartvest/company_list/companylist.csv')
    df = df.loc[df['Symbol'] == f'{name}'.upper()]
    print([ele for ele in df.iloc[:]])
    data = {
        'symbol': df['Symbol'].values[0],
        'name': df['Name'].values[0],
        'market_cap': df['MarketCap'].values[0],
        'ipo': df['IPOyear'].values[0],
        'sector': df['Sector'].values[0]
    }
    print(data)
    return render_template('content.htm', title=f'{name}', data=data)

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
    if filename == 'open_close':
        data = data[['Open', 'Close']].iloc[-150:, :]
        l1 = axis.plot(data['Open'], c='r', label='Open')
        l2 = axis.plot(data['Close'], c='g', label = 'Close')
    elif filename=='high_low':
        data = data[['High', 'Low']].iloc[-150:, :]
        l1 = axis.plot(data['High'], c='c', label='High')
        l2 = axis.plot(data['Low'], c='m', label='Low')
    elif filename == 'volume':
        data = data[['Volume']].iloc[-365:, :]
        axis.plot(data.values, c='b', label='Volume', alpha=0.7)
    axis.set_xlabel('Years')
    axis.set_ylabel('Price in $')
    axis.set_title(" ".join([x.upper() for x in filename.split('_')]))
    fig.legend()
    return fig

if __name__ == '__main__':
    app.run(debug=True)