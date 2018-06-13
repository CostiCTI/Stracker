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
import sonar_request as son

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'secret'


class RForm(Form):
    codelines = IntegerField('Sonar Project', [validators.required()])
    delbutton = SubmitField('Delete last')
    importbutton = SubmitField('Import')
    

@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')


def create_pygraph2(title, g1, g2, xlabels, l1, l2):
    graph = pygal.Line(height=380, legend_at_bottom=True, legend_at_bottom_columns=2)
    graph.title = title
    graph.x_labels = xlabels
    graph.add(g1,  l1)
    graph.add(g2,  l2)
    graph_data = graph.render_data_uri()

    return graph_data


def create_pygraph(title, g1, g2, g3, xlabels, l1, l2, l3):
    graph = pygal.Line(height=380, legend_at_bottom=True, legend_at_bottom_columns=3)
    graph.title = title
    graph.x_labels = xlabels
    graph.add(g1,  l1)
    graph.add(g2,  l2)
    graph.add(g3,  l3)
    graph_data = graph.render_data_uri()

    return graph_data
    


@app.route('/measures', methods=['POST', 'GET', 'PUT', 'DELETE'])
def measures():

    metdict = {
        "Total Lines": 0, "Total Lines added": 0,
        "Code Lines": 0, "Code Lines added": 0,
        "Comments": 0, "Comments added": 0,
        "Classes": 0, "Classes added": 0, 
        "Functions": 0, "Functions added": 0,
        "Violations": 0, "Violations added": 0,
        "Code_smells": 0, "Code_smells added": 0,
        "Bugs": 0, "Bugs added": 0
    }

    if g.user == None:
        return redirect(url_for('index'))

    form = RForm()

    project_name = request.args.get('proname')
    current_user = g.user
    ddlist = esc.get_project_data(project_name, current_user)
    dlist = sorted(ddlist, key=itemgetter('insert_date'))

    lines = []
    linecode  = []
    linecomm  = []
    linecommp = []
    code_smells = []
    violations = []
    violationsp = []
    minviolations = []
    minviolationsp = []
    functions = []
    functionsp = []
    classes = []
    classesp = []
    dates  = []    
    zeros = []
    last_input = dlist[len(dlist) - 1]['insert_date']

    for d in dlist:
        lines.append(d['lines'])
        linecode.append(d['ncloc'])
        linecomm.append(d['comments'])
        linecommp.append(d['comments_pred'])
        code_smells.append(d['code_smells'])
        violations.append(d['violations'])
        violationsp.append(d['violations_pred'])
        functions.append(d['functions'])
        functionsp.append(d['functions_pred'])
        minviolations.append(d['minor_violations'])
        minviolationsp.append(d['minor_violations_pred'])
        classes.append(d['classes'])
        classesp.append(d['classes_pred'])
        #bugs.append(d['bugs'])
        #classes.append(d['classes'])
        #dates.append(d['insert_date'])
        zeros.append(0)
        dates.append(time.strftime("%a %d %b %Y %H:%M:%S GMT", time.gmtime(d['insert_date'] / 1000.0)))

    metdict["Total Lines"] = dlist[len(dlist) - 1]['lines']
    metdict["Total Lines added"] = dlist[len(dlist) - 1]['lines'] - dlist[len(dlist) - 2]['lines']
    metdict["Code Lines"] = dlist[len(dlist) - 1]['ncloc']
    metdict["Code Lines added"] = dlist[len(dlist) - 1]['ncloc'] - dlist[len(dlist) - 2]['ncloc']
    metdict["Comments"] = dlist[len(dlist) - 1]['comments']
    metdict["Comments added"] = dlist[len(dlist) - 1]['comments'] - dlist[len(dlist) - 2]['comments']
    metdict["Classes"] = dlist[len(dlist) - 1]['classes']
    metdict["Classes added"] = dlist[len(dlist) - 1]['classes'] - dlist[len(dlist) - 2]['classes']
    metdict["Functions"] = dlist[len(dlist) - 1]['functions']
    metdict["Functions added"] = dlist[len(dlist) - 1]['functions'] - dlist[len(dlist) - 2]['functions']
    metdict["Violations"] = dlist[len(dlist) - 1]['violations']
    metdict["Violations added"] = dlist[len(dlist) - 1]['violations'] - dlist[len(dlist) - 2]['violations']
    metdict["Code_smells"] = dlist[len(dlist) - 1]['code_smells']
    metdict["Code_smells added"] = dlist[len(dlist) - 1]['code_smells'] - dlist[len(dlist) - 2]['code_smells']
    metdict["Bugs"] = dlist[len(dlist) - 1]['bugs']
    metdict["Bugs added"] = dlist[len(dlist) - 1]['bugs'] - dlist[len(dlist) - 2]['bugs']

    for k, v in metdict.items():
        v = int(v)

    scorecomm = []
    sc = esc.get_score(dlist[len(dlist) - 1], "comments")
    for i in range(sc):
        scorecomm.append('*')

    pscorecomm = []
    if len(linecode) >= 2:
        sc = esc.get_score(dlist[len(dlist) - 2], "comments")
    for i in range(sc):
        pscorecomm.append('*')

    scoreviola = []
    sc = esc.get_score(dlist[len(dlist) - 1], "violations")
    for i in range(sc):
        scoreviola.append('*')

    pscoreviola= []
    if len(linecode) >= 2:
        sc = esc.get_score(dlist[len(dlist) - 2], "violations")
    for i in range(sc):
        pscoreviola.append('*')

    scorecc = []
    sc = esc.get_score(dlist[len(dlist) - 1], "classes")
    for i in range(sc):
        scorecc.append('*')

    pscorecc = []
    if len(linecode) >= 2:
        sc = esc.get_score(dlist[len(dlist) - 2], "classes")
    for i in range(sc):
        pscorecc.append('*')

    scorecsv = []
    sc = esc.get_score(dlist[len(dlist) - 1], "classes")
    for i in range(sc):
        scorecsv.append('*')

    pscorecsv= []
    if len(linecode) >= 2:
        sc = esc.get_score(dlist[len(dlist) - 2], "classes")
    for i in range(sc):
        pscorecsv.append('*')

    scorefun= []
    sc = esc.get_score(dlist[len(dlist) - 1], "functions")
    for i in range(sc):
        scorefun.append('*')

    pscorefun= []
    if len(linecode) >= 2:
        sc = esc.get_score(dlist[len(dlist) - 2], "functions")
    for i in range(sc):
        pscorefun.append('*')

    if request.method == 'POST':
        if "delbutton" in request.form:
            p = request.args.get('proname')
            if len(dlist) > 1:
                current_user = g.user
                esc.delete_last_phase(p, last_input, current_user)
            time.sleep(1)
            return redirect(url_for('measures', metd=metdict, proname=p))

        elif "importbutton" in request.form:
            sonar_project = str(request.form['codelines'])

            p = request.args.get('proname')
            data = son.get_sonar_data(sonar_project)
            if data == None:
                time.sleep(1);
                return redirect(url_for('measures', metd=metdict, proname=p))

            current_user = g.user
            esc.add_phase(p, data, current_user)
            graph_data = create_pygraph('Comments', 'Code Lines', 'Comm Lines', 'Comm Pred',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)
            
            time.sleep(1)
            return redirect(url_for('measures', metd=metdict, proname=p))
        

        elif "grafbut" in request.form:

            if 'options' not in request.form:
                option = "opComments"
            else:
                option = request.form['options']
            if option == "opComments":
                graph_data1 = create_pygraph('Lines of code / Comments', 'Lines of code', 'Comments', 'Comments Predicted',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)

                graph_data2 = create_pygraph2('Comments Difference', 'Comments Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(linecomm, linecommp)])

                p = request.args.get('proname')
                return render_template("measures.html", stars=scorecomm, pstars=pscorecomm, gdata1=graph_data1,
                                    gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))
  
            elif option == "opViolations":
                graph_data1 = create_pygraph('Violations / Minor Violations', 
                                        'Violations', 'Minor Violations', 'Minor Violaions Predicted',
                                        dates,
                                        violations,
                                        minviolations,
                                        minviolationsp)

                graph_data2 = create_pygraph2('Minor Violations', 'Minor Violations Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(minviolations, minviolationsp)])

                p = request.args.get('proname')
                return render_template("measures.html", stars=scoreviola, pstars=pscoreviola, gdata1=graph_data1,
                                    gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))

            elif option == "opCode_smells":
                graph_data1 = create_pygraph('Code_smells / Violations', 
                                        'Code_smells', 'Violations', 'Violaions Predicted',
                                        dates,
                                        code_smells,
                                        violations,
                                        violationsp)

                graph_data2 = create_pygraph2('Violations', 'Violations Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(violations, violationsp)])

                p = request.args.get('proname')
                return render_template("measures.html", stars=scoreviola, pstars=pscoreviola, gdata1=graph_data1,
                                    gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))

            elif option == "opFunctions":
                graph_data1 = create_pygraph('Lines / Functions', 
                                        'Lines of code', 'Functions', 'Functions Predicted',
                                        dates,
                                        linecode,
                                        functions,
                                        functionsp)

                graph_data2 = create_pygraph2('Functions', 'Functions Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(functions, functionsp)])

                p = request.args.get('proname')
                return render_template("measures.html", stars=scoreviola, pstars=pscoreviola, gdata1=graph_data1,
                                    gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))
                
            else: #option == "opclasses":
                graph_data1 = create_pygraph('Lines / Classes', 
                                        'Total Lines', 'Classes', 'Classes Predicted',
                                        dates,
                                        lines,
                                        classes,
                                        classesp)

                graph_data2 = create_pygraph2('classes', 'classes Predicted', 'Difference',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(classes, classesp)])

                p = request.args.get('proname')
                return render_template("measures.html", stars=scorecc, pstars=pscorecc, gdata1=graph_data1,
                                    gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))




        elif "arb5" in request.form:
            graph_data1 = create_pygraph('Lines of code / Comments', 'Lines of code', 'Comments', 'Comments Predicted',
                                        dates,
                                        linecode,
                                        linecomm,
                                        linecommp)

            graph_data2 = create_pygraph2('Comments Difference', 'Comments Predicted', 'Difference',
                                    dates,
                                    zeros,
                                    [a - b for a, b in zip(linecomm, linecommp)])

            for i in range(10):
                zeros.append(0)
                
            for i in range(len(linecomm)):
                linecomm[i] = float(linecomm[i])

            predf = ar.get_forecast(linecomm, 10)
            #pred = predf
            pred = [int(a[0] - predf[0][0]) for a in predf]
            del pred[0]

            graph_arima = create_pygraph2('Comments Forecast', 'Comments Predicted', 'Difference Predicted',
                                        dates,
                                        zeros,
                                        [a - b for a, b in zip(linecomm, linecommp)] + pred)
                                        
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm, gdata1=graph_data1,
                                gdata2=graph_data2, garima=graph_arima, metd=metdict, form=form, pname=request.args.get('proname'))

        else:
            graph_data1 = create_pygraph('Lines of code / Comments', 'Lines of code', 'Comments', 'Comments Predicted',
                                    dates,
                                    linecode,
                                    linecomm,
                                    linecommp)

            graph_data2 = create_pygraph2('Comments Difference', 'Comments Predicted', 'Difference',
                                    dates,
                                    zeros,
                                    [a - b for a, b in zip(linecomm, linecommp)])

            p = request.args.get('proname')
            return render_template("measures.html", stars=scorecomm, pstars=pscorecomm, gdata1=graph_data1,
                                gdata2=graph_data2, garima=graph_data2, form=form,  metd=metdict, pname=request.args.get('proname'))

    else:
        graph_data1 = create_pygraph('Lines of code / Comments', 'Lines of code', 'Comments', 'Comments Predicted',
                                dates,
                                linecode,
                                linecomm,
                                linecommp)

        graph_data2 = create_pygraph2('Comments Difference', 'Comments Predicted', 'Difference',
                                dates,
                                zeros,
                                [a - b for a, b in zip(linecomm, linecommp)])

        p = request.args.get('proname')
        return render_template("measures.html", stars=scorecomm, pstars=pscorecomm, gdata1=graph_data1,
                            gdata2=graph_data2, garima=graph_data2, form=form, metd=metdict, pname=request.args.get('proname'))


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
                #return redirect(url_for('projects', projects=plist))
                return render_template('projects.html', projects=plist)
            else:
                for p in plist:
                    if p + "del" in request.form:
                        current_user = g.user
                        esc.delete_project(p, current_user)
                        plist = esc.get_projects(current_user)
                        plist = sorted(plist)
                        #return redirect(url_for('projects', projects=plist))
                        return render_template('projects.html', projects=plist)
                    elif p in request.form:
                        metdict = {
                            "Total Lines": 0, "Total Lines added": 0,
                            "Code Lines": 0, "Code Lines added": 0,
                            "Comments": 0, "Comments added": 0,
                            "Classes": 0, "Classes added": 0, 
                            "Functions": 0, "Functions added": 0,
                            "Violations": 0, "Violations added": 0,
                            "Code_smells": 0, "Code_smells added": 0,
                            "Bugs": 0, "Bugs added": 0
                        }
                        return redirect(url_for('measures', metd=metdict, proname=p))


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
                return redirect(url_for('projects'))
            elif request.form['username'] == 'paul' and request.form['password'] == 'paul':
                session['user'] = request.form['username']
                return redirect(url_for('projects'))

    if 'user' in session:
        return render_template('account.html', usersess=session['user'])
    return render_template('account.html', usersess=None)

@app.route('/stracker', methods=['POST', 'GET'])
def stracker():

    return render_template('stracker.html')




if __name__ == '__main__':
    app.run()