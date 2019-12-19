#!/usr/bin/env python
from flask import render_template, flash, redirect, url_for, request
from subprocess import check_call, Popen, call
import re, os, sys

from app import app
from app.spider.spider import spider_func
from app.spider.sprank import sprank_func
from app.spider.spjson import spjson_func
from app.spider.compute_embeddings import compute_embeddings


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            web_url = request.form["webUrl"]
            num_pages = int(request.form["numPages"])
            num_iter = int(request.form["iterno"])
            node_iter = int(request.form["itno"])
            # Add URL Validation
            spider_func(web_url, num_pages)
            sprank_func(domain=web_url, num_iterations=num_iter)
            spjson_func(domain=web_url, howmany=node_iter)
            flash('Visualizing Graph!', 'success')
            return render_template('index.html', title='Home', result=True)
        except KeyError:
            web_url = None

        try:
            web_url_node = request.form["webUrlnode"]
            perpexi = int(request.form["perp"])
            embed_dimm = int(request.form["emb"])
            walk_length = int(request.form["node"])
            num_walks = int(request.form["walk"])
            # Add URL Validation
            flash('Visualizing Node Embedings!', 'success')
            compute_embeddings(
                domain=web_url_node,
                perpex=perpexi,
                embed_dimm=embed_dimm,
                walk_length=walk_length,
                num_walks=num_walks
            )
            return render_template('index.html', title='Home', result=True)
        except KeyError:
            web_url_node = None

        error = 'Please try again! Not a valid Web URL'
        return render_template('index.html', error=error, result=False)
    else:
        return render_template('index.html', result=False)
