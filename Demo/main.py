from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# Income Form
@app.route('/income', methods=['GET', 'POST'])
def income():
    if request.method == 'POST':
        name = request.form['name']
        service_type = request.form['service_type']
        amount = request.form['amount']
        transaction_type = request.form['transaction_type']
        reference_no = request.form['reference_no']

        with open('income.csv', 'a') as f:
            f.write(f"{name},{service_type},{amount},{transaction_type},{reference_no}\n")
        
        return redirect(url_for('index'))
    
    return render_template('income_form.html')

# Expenditure Form
@app.route('/expenditure', methods=['GET', 'POST'])
def expenditure():
    if request.method == 'POST':
        name = request.form['name']
        purpose = request.form['purpose']
        amount = request.form['amount']

        with open('expenditure.csv', 'a') as f:
            f.write(f"{name},{purpose},{amount}\n")

        return redirect(url_for('index'))
    
    return render_template('expenditureform.html')

# Report Page
@app.route('/report')
def report():
    # Read CSV files
    income_df = pd.read_csv('income.csv', names=['Name', 'Service Type', 'Amount', 'Transaction Type', 'Reference No.'])
    expenditure_df = pd.read_csv('expenditure.csv', names=['Name', 'Purpose', 'Amount'])

    # Calculate total income and expenditure
    total_income = income_df['Amount'].astype(float).sum()
    total_expenditure = expenditure_df['Amount'].astype(float).sum()
    profit_loss = total_income - total_expenditure

    # Bar chart for income and expenditure
    fig, ax = plt.subplots(figsize=(10, 6))

    income_df.groupby('Service Type')['Amount'].sum().plot(kind='bar', ax=ax, color='blue', alpha=0.7, label='Income')
    expenditure_df.groupby('Purpose')['Amount'].sum().plot(kind='bar', ax=ax, color='red', alpha=0.7, label='Expenditure')

    ax.set_title('Income vs Expenditure')
    ax.set_xlabel('Categories')
    ax.set_ylabel('Amount')
    ax.legend()

    # Save plot to a bytes object
    plt_bytes = io.BytesIO()
    plt.savefig(plt_bytes, format='png')
    plt_bytes.seek(0)
    plot_base64 = base64.b64encode(plt_bytes.getvalue()).decode()

    # Pie chart for profit and loss
    labels = ['Total Income', 'Total Expenditure']
    sizes = [total_income, total_expenditure]
    colors = ['#ff9999', '#66b3ff']
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt_bytes_pie = io.BytesIO()
    fig1.savefig(plt_bytes_pie, format='png')
    plt_bytes_pie.seek(0)
    pie_base64 = base64.b64encode(plt_bytes_pie.getvalue()).decode()

    # Render the report template with the tables and charts
    return render_template('reports.html', 
                           income_table=income_df.to_html(index=False), 
                           expenditure_table=expenditure_df.to_html(index=False),
                           total_income=total_income,
                           total_expenditure=total_expenditure,
                           profit_loss=profit_loss,
                           plot_base64=plot_base64,
                           pie_base64=pie_base64)

if __name__ == '__main__':
    app.run(debug=True)
