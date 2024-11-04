from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

sales = Blueprint('sales', __name__)

@sales.route('/show_sales')
def show_sales():
    connection = get_db()
    query = "SELECT * FROM sales_data"
    with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
    df = pd.DataFrame(result)
    df.columns = ['sales_data_id', 'monthly_amount', 'date', 'region']  # Adjust column names as needed
    df['Actions'] = df['sales_data_id'].apply(lambda id:
                                              f'<a href="{url_for("sales.edit_sales_data", sales_data_id=id)}" class="btn btn-sm btn-info">Edit</a> '
                                              f'<form action="{url_for("sales.delete_sales_data", sales_data_id=id)}" method="post" style="display:inline;">'
                                              f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                              )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("sales_data.html", table=rows_only)


# Route to handle adding a new row
@sales.route('/', methods=['GET', 'POST'])
def add_sales_data():
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']

        connection = get_db()
        query = "INSERT INTO sales_data (monthly_amount, date, region) VALUES (%s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (monthly_amount, date, region))
            connection.commit()
            flash("New sales data added successfully!", "success")
        except Exception as e:
            flash("An error occurred while adding sales data.", "danger")
            print(e)
        return redirect(url_for('sales.show_sales'))

    return render_template("add_sales_data.html")


# Route to handle updating a row
@sales.route('/edit_sales_data/<int:sales_data_id>', methods=['GET', 'POST'])
def edit_sales_data(sales_data_id):
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region = request.form['region']


        query = "UPDATE sales_data SET monthly_amount = %s, date = %s, region = %s WHERE sales_data_id = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (monthly_amount, date, region, sales_data_id))
            connection.commit()
            flash("Sales data updated successfully!", "success")
        except Exception as e:
            flash("An error occurred while updating sales data.", "danger")
            print(e)
        return redirect(url_for('sales.show_sales'))


    # Fetch the current data to pre-populate the form
    query = "SELECT * FROM sales_data WHERE sales_data_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (sales_data_id,))
            sales_data = cursor.fetchone()
    except Exception as e:
        flash("An error occurred while accessing the sales data.", "danger")
        print(e)
        return redirect(url_for('sales.show_sales'))

    return render_template("edit_sales_data.html", sales_data=sales_data)


# Route to handle deleting a row
@sales.route('/delete_sales_data/<int:sales_data_id>', methods=['POST'])
def delete_sales_data(sales_data_id):
    connection = get_db()
    query = "DELETE FROM sales_data WHERE sales_data_id = %s"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (sales_data_id,))
        connection.commit()
        flash("Sales data deleted successfully!", "success")
    except Exception as e:
        flash("An error occurred while deleting sales data.", "danger")
        print(e)
    return redirect(url_for('sales.show_sales'))