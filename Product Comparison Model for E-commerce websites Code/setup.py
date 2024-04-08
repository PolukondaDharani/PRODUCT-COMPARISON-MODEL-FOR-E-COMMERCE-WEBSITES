from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pickle
from model import train_x
from selenium.common.exceptions import NoSuchElementException
import re

model = pickle.load(open('model.pkl','rb'))
app = Flask(__name__)
headers = {
    'User-Agent': 'Use your own user agent',
    'Accept-Language': 'en-us,en;q=0.5'
}
driver = webdriver.Chrome()

def ebay(product):
    l = []
    reviews = [] 
    driver.get('https://www.ebay.com/')
    time.sleep(4)
    search = driver.find_element("id", 'gh-ac')
    search.send_keys(product)
    search.send_keys(Keys.ENTER)
    time.sleep(5)

    try:
        xpath = '/html/body/div/div/div/div/div/ul/li/div/div/a/div/span'
        element = driver.find_element(By.XPATH, xpath)
        name = element.text
    except NoSuchElementException:
        name = "Null"

    try:
        Xpath_rate = '/html/body/div/div/div/div/div/ul/li/div/div/div/a/div/span'
        element1 = driver.find_element(By.XPATH, Xpath_rate)
        rate = element1.text
    except NoSuchElementException:
        rate = "Null"

    try:
        Xpath_price = '/html/body/div/div/div/div/div/ul/li/div/div/div/div/span'
        element2 = driver.find_element(By.XPATH, Xpath_price)
        price = element2.text
    except NoSuchElementException:
        price = "Null"
    try:
        xpath_link = '/html/body/div/div/div/div/div/ul/li/div/div/a'
        element3 = driver.find_element(By.XPATH, xpath_link)
        link = element3.get_attribute("href")
        driver.get(link)
        time.sleep(5)

        try:
            link_r = driver.find_element(By.CLASS_NAME, "fdbk-detail-list__tabbed-btn")
            review_link = link_r.get_attribute("href")
        except NoSuchElementException:
            link_r = driver.find_element(By.CLASS_NAME, "fdbk-detail-list__btn-container__btn")
            review_link = link_r.get_attribute("href")

        driver.get(review_link)
        time.sleep(5)
        review_elements = driver.find_elements(By.CLASS_NAME, "card__comment")
        reviews = [element.text.strip() for element in review_elements]

    except NoSuchElementException:
        link = "Null"
    reviews_list=str(reviews)
    import ast
    reviews_list = ast.literal_eval(reviews_list)
    r=[]
    for idx, review in enumerate(reviews_list):
        r.append(review)
    def predict_count(train_x, model, new_comment):
        new_comment = pd.Series(new_comment)
        new_comment = CountVectorizer().fit(train_x).transform(new_comment)
        result = model.predict(new_comment)
        return result
    pc = 0
    nc = 0
    for i in r:
        p = predict_count(train_x, model, new_comment=i)
        if p == 1:
            pc += 1
        else:
            nc += 1
    
    l.append(["Ebay", name, rate, price, link,pc,nc])
    return l
def flipKart(product):
    l=[]
    driver.get('https://www.flipkart.com/')
    search_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'Pke_EE'))
    )
    search_field.send_keys(product)
    search_field.submit()
    try:
        element = driver.find_element(By.CLASS_NAME, "_4rR01T")
        name = element.text
    except:
        try:
            element = driver.find_element(By.CLASS_NAME, "s1Q9rs")
            name = element.text
        except:
            name = "Name not found"

    try:
        element1 = driver.find_element(By.CLASS_NAME, "_3LWZlK")
        rate = element1.text
    except:
        rate = "Rate not found"

    try:
        element3 = driver.find_element(By.CSS_SELECTOR, '._30jeq3._1_WHN1')
        price = element3.text
    except:
        try:
            element3 = driver.find_element(By.CSS_SELECTOR, '_30jeq3')
            price = element3.text
        except:
            price = "Price not found"

    try:
        element4 = driver.find_element(By.CLASS_NAME, "_1fQZEK")
        link = element4.get_attribute("href")
    except:
        try:
            element4 = driver.find_element(By.CLASS_NAME, "_2rpwqI")
            link = element4.get_attribute("href")
        except:
            link = "Link not found"

    time.sleep(10)
    comments = []
    for i in range(1,3):
        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        cmt = soup.find_all('div', class_='t-ZTKy')
        for c in cmt:
            comment_text = c.div.div.get_text(strip=True)
            comments.append(comment_text)
    reviews_list=str(comments)
    import ast
    reviews_list = ast.literal_eval(reviews_list)
    r=[]
    for idx, review in enumerate(reviews_list):
        r.append(review)  
    def predict_count(train_x, model, new_comment):
        new_comment = pd.Series(new_comment)
        new_comment = CountVectorizer().fit(train_x).transform(new_comment)
        result = model.predict(new_comment)
        return result
    pc = 0
    nc = 0
    for i in r:
        p = predict_count(train_x, model, new_comment=i)
        if p == 1:
            pc += 1
        else:
            nc += 1
   
    l.append(["FlipKart", name, rate, price, link,pc,nc])
    return l
def amazon(product):
    l=[]
    try:
        driver.get('https://www.amazon.in/')
        
        search = driver.find_element("id", 'twotabsearchtextbox')
        search.send_keys(product)
        search.send_keys(Keys.ENTER)

        element = driver.find_element(By.CLASS_NAME, "a-size-medium.a-color-base.a-text-normal")
        name = element.text
    except NoSuchElementException:
        name = "Name not found"

    try:
        element1 = driver.find_element(By.CLASS_NAME, "a-icon-alt")
        rate = element1.get_attribute("innerText")
    except NoSuchElementException:
        rate = "Rate not found"

    try:
        outer_span = driver.find_element(By.CLASS_NAME, "a-price")
        inner_span = outer_span.find_element(By.CLASS_NAME, "a-price-whole")
        price = inner_span.text
    except NoSuchElementException:
        price = "Price not found"

    try:
        h2_element = driver.find_element(By.CLASS_NAME, "a-size-mini")
        link_element = h2_element.find_element(By.TAG_NAME, "a")
        link = link_element.get_attribute("href")
        driver.get(link)
        time.sleep(5)
        xpath = '/html/body/div/div/div/div/div/div/div/div/div/div/div/span/div/div/div/div/a'
        element = driver.find_element(By.XPATH, xpath)
        review = element.get_attribute("href")
        review_link=driver.get(review)
        review_elements = driver.find_elements(By.CLASS_NAME, "a-size-base.review-text.review-text-content")
        reviews = [element.text.strip() for element in review_elements]  
        reviews_list=str(reviews)
        import ast
        reviews_list = ast.literal_eval(reviews_list)
        r=[]
        for idx, review in enumerate(reviews_list):
            r.append(review)  
    except NoSuchElementException:
        r = []
        review_link = ""
    
    def predict_count(train_x, model, new_comment):
        new_comment = pd.Series(new_comment)
        new_comment = CountVectorizer().fit(train_x).transform(new_comment)
        result = model.predict(new_comment)
        return result

    pc = 0
    nc = 0
    for i in r:
        p = predict_count(train_x, model, new_comment=i)
        if p == 1:
            pc += 1
        else:
            nc += 1
    
    l.append(["amazon", name, rate, price, link, pc, nc])
    return l

#main function
@app.route('/')
def main():
    return render_template('index.html')


# main template for having product name 
@app.route('/getValue', methods=['POST'])
def getValue():
    product_name= request.form['proName']
    # choice=request.form['choice']
    #print(choice)
    amaz_list=amazon(product_name)
    ebay_list=ebay(product_name)
    flip_list=flipKart(product_name)   
    return render_template('pass.html', a=amaz_list,e=ebay_list,f=flip_list)

app.run() 

