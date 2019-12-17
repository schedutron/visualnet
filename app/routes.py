#!/usr/bin/env python
from flask import render_template, flash, redirect, url_for, request
from subprocess import check_call, Popen, call
import re, os, sys

from app import app
from app.spider.spider import spider_func
from app.spider.sprank import sprank_func
from app.spider.spjson import spjson_func
from app.spider.spider_node import spider_node_func


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            web_url = request.form["webUrl"]
            num_pages = request.form["numPages"]
            num_iter = request.form["iterno"]
            # Add URL Validation
            flash('Process started!', 'success')
            spider_func(web_url, num_pages)
            flash('Scrapped the Pages!', 'success')
            flash('Page Rank Calculation Started!', 'success')
            sprank_func(domain=web_url, num_iterations=num_iter)
            flash('Page Rank Calculation Ended!', 'success')
            flash('Visualizing Graph!', 'success')
            spjson_func(domain=web_url)
            return render_template('index.html', title='Home', result=True)
        except KeyError:
            web_url = None
        try:
            web_url_node = request.form["webUrlnode"]
            perpexi = request.form["perp"]
            # Add URL Validation
            flash('Visualizing Node Embedings!', 'success')
            spider_node_func(domain=web_url_node, perpex=perpexi)
            return render_template('index.html', title='Home', result=True)
        except KeyError:
            web_url_node = None

        error = 'Please try again! Not a valid Web URL'
        return render_template('index.html', error=error, result=False)
    else:
        return render_template('index.html', result=False)
