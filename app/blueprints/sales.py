import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db_connect import get_db
from app.functions import calculate_total_sales_by_region, analyze_monthly_sales_trends, identify_top_performing_region
import pandas as pd
import matplotlib.pyplot as plt
import os
import mpld3

sales = Blueprint('sales', __name__)

@sales.route('/show_sales')
def show_sales():
    connection = get_db()
    query = """
        SELECT sd.sales_data_id, sd.monthly_amount, sd.date, r.region_id, r.region_name
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    df.columns = ['sales_data_id', 'monthly_amount', 'date', 'region_id', 'region_name']  # Adjust column names as needed
    df['Actions'] = df['sales_data_id'].apply(lambda id:
                                              f'<a href="{url_for("sales.edit_sales_data", sales_data_id=id)}" class="btn btn-sm btn-info">Edit</a> '
                                              f'<form action="{url_for("sales.delete_sales_data", sales_data_id=id)}" method="post" style="display:inline;">'
                                              f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
                                              )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=False, escape=False)
    rows_only = table_html.split('<tbody>')[1].split('</tbody>')[0]

    return render_template("sales_data.html", table=rows_only)


# Route to handle adding a new row
@sales.route('/add_sales_data', methods=['GET', 'POST'])
def add_sales_data():
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region_id = request.form['region_id']

        query = "INSERT INTO sales_data (monthly_amount, date, region_id) VALUES (%s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (monthly_amount, date, region_id))
            connection.commit()
            flash("Sales data added successfully!", "success")
        except Exception as e:
            flash("An error occurred while adding sales data.", "danger")
            print(e)
        return redirect(url_for('sales.show_sales'))

    return render_template("add_sales_data.html")


@sales.route('/get_regions', methods=['GET'])
def get_regions():
    connection = get_db()
    query = "SELECT region_id, region_name FROM regions"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            regions = cursor.fetchall()
        return jsonify(regions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to handle updating a row
@sales.route('/edit_sales_data/<int:sales_data_id>', methods=['GET', 'POST'])
def edit_sales_data(sales_data_id):
    connection = get_db()
    if request.method == 'POST':
        monthly_amount = request.form['monthly_amount']
        date = request.form['date']
        region_id = request.form['region_id']

        query = "UPDATE sales_data SET monthly_amount = %s, date = %s, region_id = %s WHERE sales_data_id = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (monthly_amount, date, region_id, sales_data_id))
            connection.commit()
            flash("Sales data updated successfully!", "success")
        except Exception as e:
            flash("An error occurred while updating sales data.", "danger")
            print(e)
        return redirect(url_for('sales.show_sales'))

    # Fetch the current data to pre-populate the form
    query = """
        SELECT sd.sales_data_id, sd.monthly_amount, sd.date, r.region_id, r.region_name
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
        WHERE sd.sales_data_id = %s
    """
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


# New route to display reports
@sales.route('/reports')
def show_reports():
    total_sales_by_region = calculate_total_sales_by_region()
    monthly_sales_trends = analyze_monthly_sales_trends()
    top_performing_region = identify_top_performing_region()

    return render_template("reports.html",
                           total_sales_by_region=total_sales_by_region.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False),
                           monthly_sales_trends=monthly_sales_trends.to_html(classes='dataframe table table-striped table-bordered', index=False, escape=False),
                           top_performing_region=top_performing_region)

@sales.route('/visualizations')
def show_visualizations():
    # Generate total sales by region chart
    total_sales_by_region = calculate_total_sales_by_region()
    print("Total Sales by Region DataFrame:")
    print(total_sales_by_region)
    if not total_sales_by_region.empty and 'total_sales' in total_sales_by_region.columns:
        fig1, ax1 = plt.subplots(figsize=(10, 6))  # Original figure size
        ax1.bar(total_sales_by_region['region_name'], total_sales_by_region['total_sales'])
        ax1.set_title('Total Sales by Region')
        ax1.set_xlabel('Region')
        ax1.set_ylabel('Total Sales')
        ax1.set_xticklabels(total_sales_by_region['region_name'], rotation=45, ha='right')
        total_sales_by_region_html = mpld3.fig_to_html(fig1)
        plt.close(fig1)
    else:
        total_sales_by_region_html = None

    # Generate monthly sales trends chart
    monthly_sales_trends = analyze_monthly_sales_trends()
    print("Monthly Sales Trends DataFrame:")
    print(monthly_sales_trends)
    if not monthly_sales_trends.empty and 'total_sales' in monthly_sales_trends.columns:
        fig2, ax2 = plt.subplots(figsize=(10, 6))  # Original figure size
        ax2.plot(monthly_sales_trends['month'], monthly_sales_trends['total_sales'])
        ax2.set_title('Monthly Sales Trends')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Total Sales')
        monthly_sales_trends_html = mpld3.fig_to_html(fig2)
        plt.close(fig2)
    else:
        monthly_sales_trends_html = None

    # Identify top performing region
    top_performing_region = identify_top_performing_region()

    return render_template("visualizations.html",
                           total_sales_by_region_html=total_sales_by_region_html,
                           monthly_sales_trends_html=monthly_sales_trends_html,
                           top_performing_region=top_performing_region)