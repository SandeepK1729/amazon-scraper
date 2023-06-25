from flask import Flask, render_template, request, make_response
from bs4 import BeautifulSoup
import requests
import pandas as pd
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        data = scrape_amazon(url)

        if data is not None:
            return render_template('index.html', data=data.to_html(), link=url)
        else:
            return render_template('index.html', error='Error scraping data')
    return render_template('index.html')

@app.route('/export', methods=['GET'])
def download():
    url = request.args['link']
    data = scrape_amazon(url)
    
    if data is not None:
        # Create a response object
        response = make_response(render_template('index.html', data=data.to_html()))
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        response.headers['Content-type'] = 'text/csv'

        # Convert DataFrame to CSV format
        csv_data = data.to_csv(index=False, encoding='utf-8')
        response.set_data(io.BytesIO(csv_data.encode('utf-8')).getvalue())

        return response

    return None

def scrape_amazon(url):
    # try:
    response = requests.get(url, headers={'Accept' : '*/*', 'User-Agent': 'Thunder Client (https://www.thunderclient.com)'})
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('div', {'data-component-type': 's-search-result'})

    products = []
    prices = []
    delivery_dates = []
    images = []

    for item in items:
        data = item.find('div').find('div').find('div')
        # print(data.prettify())
        delivery_date = data.find('span', {'class' : 'a-color-base a-text-bold'})
        if delivery_date:
            delivery_date = delivery_date.text

        price         = data.find('span', {'class' : 'a-price-whole'})
        product_name  = data.find('span', {'class' : 'a-size-medium a-color-base a-text-normal'})
        image_url     = data.find('div', {'class' : 'a-section aok-relative s-image-fixed-height'}).find('img').get('src')
        
        if product_name is not None and price is not None:
            products.append(product_name.text)
            prices.append(price.text)
            images.append(image_url)
            delivery_dates.append(delivery_date)

    data = pd.DataFrame({'Product': products, 'Price': prices, 'Image' : images, 'Delivery' : delivery_dates})
    return data
    # except Exception as e:
    #     print('Error scraping data:', str(e))
    #     return None

if __name__ == '__main__':
    app.run(debug=True)
