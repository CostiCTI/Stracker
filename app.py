from flask import Flask, render_template, flash, request, redirect, url_for, session, abort, g
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, IntegerField
from operator import itemgetter

import pygal
import re
import time
import datetime
import pprint as pp

from pygal.style import DarkSolarizedStyle
import user_projects as esc
import arimaf as ar

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'secret'


class RForm(Form):
    codelines = IntegerField('Code Lines', [validators.required()])
    commlines = IntegerField('Comments', [validators.required()])
    operlines = IntegerField('Operands', [validators.required()])
    addbut = SubmitField('Add')
    delbutton = SubmitField('Delete last')
    importbutton = SubmitField('Import')
    

@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')

def create_pygraph3(title, g1, g2, xlabels, l1, l2):
    graph = pygal.Line(height=420, legend_at_bottom=True, legend_at_bottom_columns=2)
    graph.title = title
    graph.x_labels = xlabels
    graph.add(g1,  l1)
    graph.add(g2,  l2)
    graph.add('Forecast Start Point', 10)
    graph_data = graph.render_data_uri()

    return graph_data


def create_pygraph2(title, g1, g2, xlabels, l1, l2):
    graph = pygal.Line(height=420, legend_at_bottom=True, legend_at_bottom_columns=2)
    graph.title = title
    graph.x_labels = xlabels
    graph.add(g1,  l1)
    graph.add(g2,  l2)
    graph_data = graph.render_data_uri()

    return graph_data


def create_pygraph(title, g1, g2, g3, xlabels, l1, l2, l3):
    graph = pygal.Line(height=420, legend_at_bottom=True, legend_at_bottom_columns=3)
    graph.title = title
    graph.x_labels = xlabels
    graph.add(g1,  l1)
    graph.add(g2,  l2)
    graph.add(g3,  l3)
    graph_data = graph.render_data_uri()

    return graph_data
    


@app.route('/measures', methods=['POST', 'GET', 'PUT', 'DELETE'])
def measures():

    if g.user == None:
        return redirect(url_for('index'))

    form = RForm()

    project_name = request.args.get('proname')
    current_user = g.user
    ddlist = esc.get_project_data(project_name, current_user)
    dlist = sorted(ddlist, key=itemgetter('insert_date'))

    linecode  = []
    linecomm  = []
    linecommp = []
    operands  = []
    operandsp = []
    dates  = []    
    zeros = []
    last_input = dlist[len(dlist) - 1]['insert_date']

    for d in dlist:
        linecode.append(d['lcode'])
        linecomm.append(d['lcom'])
        linecommp.append(d['lcom_pred'])
        operands.append(d['operands'])
        operandsp.append(d['operands_pred'])
        #dates.append(d['insert_date'])
        zeros.append(0)
        dates.append(time.strftime("%a %d %b %Y %H:%M:%S GMT", time.gmtime(d['insert_date'] / 1000.0)))

    scorecomm = []
    sc = esc.get_score(linecode[len(linecode)-1], linecomm[len(linecomm)-1], operands[len(operands)-1], "comments")
    for i in range(sc):
        scorecomm.append('*')

    pscorecomm = []
    if len(linecode) >= 2:
        sc = esc.get_score(linecode[len(linecode)-2], linecomm[len(linecomm)-2], operands[len(operands)-2], "comments")
    for i in range(sc):
        pscorecomm.append('*')

    scoreopnd = []
    sc = esc.get_score(linecode[len(linecode)-1], linecomm[len(linecomm)-1], operands[len(operands)-1], "operands")
    for i in range(sc):
        scoreopnd.append('*')

    pscoreopnd = []
    if len(linecode) >= 2:
        sc = esc.get_score(linecode[len(linecode)-2], linecomm[len(linecomm)-2], operands[len(operands)-2], "operands")
    for i in range(sc):
        pscoreopnd.append('*')

    if request.method == 'POST':
        if "delbutton" in request.form:
            p = request.args.get('proname')
            if len(dlist) > 1:
                current_user = g.user
                esc.delete_last_phase(p, last_input, current_user)
            time.sleep(1)
            return redirect(url_for('measures', proname=p))

        elif "addbut" in request.form:
            p = request.args.get('proname')

            t1 = request.form['codelines']
            t2 = request.form['commlines']
            t3 = request.form['operlines']
            if t1.isdigit() == False or t2.isdigit() == False or t3.isdigit() == False:
                return redirect(url_for('measures', proname=p))

            lcode = int(request.form['codelines'])
            lcome = int(request.form['commlines'])
            oper  = int(request.form['operlines'])

            current_user = g.user
            esc.add_phase(project_name, lcode, lcome, oper, current_user)

            graph_data = create_pygraph('Comments', 'Code Lines', 'Comm Lines', 'Comm Pred',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
            
            time.sleep(1)
            return redirect(url_for('measures', proname=p))
            #return render_template("measures.html", stars=score, pstars=pscore, gdata=graph_data, form=form, pname=request.args.get('proname'))
        

        if "commbut" in request.form:
            graph_data = create_pygraph('Comments', 'Code Lines', 'Comments', 'Comments Predicted',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
            p = request.args.get('proname')
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))
  
        elif "opbut" in request.form:
            graph_data = create_pygraph('Operators', 'Code Lines', 'Operators', 'Oprs Pred',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
            p = request.args.get('proname')
            return render_template("measures.html", stars=scoreopnd, pstars=pscoreopnd,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

        elif "opndbut" in request.form:
            graph_data = create_pygraph('Operands', 'Code Lines', 'Operands', 'Operands Predicted',
                                        dates,
                                        linecode,
                                        operands,
                                        operandsp)
            p = request.args.get('proname')
            return render_template("measures.html", stars=scoreopnd, pstars=pscoreopnd,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

        elif "ccbut" in request.form:
            graph_data = create_pygraph('Complexity', 'Code Lines', 'Cyclomatic C', 'CC Pred',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

        if "commbut2" in request.form:
            graph_data = create_pygraph2('Comments Difference', 'Comments Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(linecomm, linecommp)])


            p = request.args.get('proname')
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))
  
        elif "opbut2" in request.form:
            graph_data = create_pygraph2('Comments Difference', 'Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(operands, operandsp)])
            p = request.args.get('proname')
            return render_template("measures.html", stars=scoreopnd, pstars=pscoreopnd,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

        elif "opndbut2" in request.form:
            graph_data = create_pygraph2('Operands Difference', 'Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(operands, operandsp)])
            p = request.args.get('proname')
            return render_template("measures.html", stars=scoreopnd, pstars=pscoreopnd,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

        elif "arb5" in request.form:
            print ('- - - - - - * * * * * * * - - - - -  -')
            graph_data = create_pygraph2('Operands Difference', 'Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(operands, operandsp)])
            for i in range(10):
                zeros.append(0)
                
            for i in range(len(linecomm)):
                linecomm[i] = float(linecomm[i])
            print ('- - - - - - * * * * * * * - - - - -  -')
            print (linecomm)
            print ('- - - - - - * * * * * * * - - - - -  -')

            predf = ar.get_forecast(linecomm, 10)
            pred = [a[0] for a in predf]


            graph_arima = create_pygraph2('Comments Forecast', 'Comments Predicted', 'Difference Predicted',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(linecomm, linecommp)] + pred)

            p = request.args.get('proname')
            return render_template("measures.html", stars=scoreopnd, pstars=pscoreopnd,
                                gdata=graph_data, garima=graph_arima, form=form, pname=request.args.get('proname'))

        else:
            graph_data = create_pygraph2('Comments Difference', 'Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(linecomm, linecommp)])
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm,
                                gdata=graph_data, form=form, pname=request.args.get('proname'))

    else:
        graph_data = create_pygraph('Comments', 'Code Lines', 'Operands', 'Oper Pred',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
        return render_template("measures.html", stars=scorecomm, pstars=pscorecomm,
                            gdata=graph_data, form=form, pname=request.args.get('proname'))


@app.route('/projects', methods=['POST', 'GET', 'PUT', 'DELETE'])
def projects():

    if g.user:

        current_user = g.user
        plist = esc.get_projects(current_user)
        plist = sorted(plist)
        if request.method == 'POST':
            if "create" in request.form:
                text = request.form['lname']
                if re.match("^[A-Za-z0-9_-]*$", text):
                    ptext = text.lower()
                    if ptext in plist or ptext == "" or ptext == " ":
                        pass
                    else:
                        current_user = g.user
                        esc.create_new_project(ptext, current_user)
                        plist = esc.get_projects(current_user)
                        plist = sorted(plist)
                return redirect(url_for('projects', projects=plist))
                #return render_template('projects.html', projects=plist)
            else:
                for p in plist:
                    if p + "del" in request.form:
                        current_user = g.user
                        esc.delete_project(p, current_user)
                        plist = esc.get_projects(current_user)
                        plist = sorted(plist)
                        return redirect(url_for('projects', projects=plist))
                    elif p in request.form:
                        return redirect(url_for('measures', proname=p))

        return render_template('projects.html', projects=plist)
    
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/account', methods=['POST', 'GET'])
def account():

    if g.user:
        if request.method == 'POST':
            if "logoutbut" in request.form:
                session.pop('user', None)
            return render_template('account.html', usersess=None)

    if request.method == 'POST':
        if "loginbut" in request.form:
            if request.form['username'] == 'costi' and request.form['password'] == 'costi':
                session['user'] = request.form['username']
                return redirect(url_for('index'))
            elif request.form['username'] == 'paul' and request.form['password'] == 'paul':
                session['user'] = request.form['username']
                return redirect(url_for('index'))

    if 'user' in session:
        return render_template('account.html', usersess=session['user'])
    return render_template('account.html', usersess=None)

@app.route('/stracker', methods=['POST', 'GET'])
def stracker():

    return render_template('stracker.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0')