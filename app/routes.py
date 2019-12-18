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
        web_url = request.form["webUrl"] or None
        num_pages = request.form["numPages"] or None
        num_iter = request.form["iterno"] or None
        web_url_node = request.form["webUrlnode"] or None
        perpexi = request.form["perp"] or None
        if web_url:
            spider_func(web_url, num_pages)
            sprank_func(domain=web_url, num_iterations=num_iter)
            spjson_func(domain=web_url)
            return render_template('index.html', title='Home', result=False)
        elif web_url_node:
            spider_node_func(domain=web_url_node, perpex=perpexi)
            return render_template('index.html', title='Home', result=True)
        else:
            error = 'Please try again! Not a valid Web URL'
            return render_template('index.html', error=error)
    else:
        return render_template('index.html', result=False)
