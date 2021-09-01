import os
from time import sleep

from flask import request, jsonify
from flask.helpers import send_file, url_for
from flask_executor import Executor
from werkzeug.utils import redirect
from flask_cors import CORS
from src.models.Shopee import crawl_shopee
from src.models.aliexpress import crawl_aliexpress

from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce
from src.utils import delete_product
from src.models import init_app


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


app = init_app()
CORS(app, expose_headers=["Content-Disposition"])
executor = Executor(app)

app.config['EXECUTOR_MAX_WORKERS'] = 1
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
# redirect_limit = []


@app.route('/')
def index():
    return jsonify(
        {
            'Routes': { 
                '/amazon': 'Crawl amazon products, args: link of product', 
                '/magazinevoce': 'Crawl magazinei9bux product details, args: link of product',
                '/aliexpress': 'Crawl aliexpress product details, args: link of product',
                # '/shopee': 'Crawl shopee product details, args: link of product'
            } 
        }
    )


@app.route('/amazon')
def amazon_download():
    delete_product('Amazon.csv')
    link = request.args.get('url')

    if link == '':
        return 'Insira um link'

    test_link = link.split('/')[2]
    if not (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
        return "Insira o um link válido!"

    executor.submit(crawl_amazon, link, ROOT_DIR, "Amazon")
    return redirect(url_for('amazon_get'))


@app.route('/amazonget')
def amazon_get():
    filename = 'Amazon.csv'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, cache_timeout=-1)

    sleep(5)
    return redirect(url_for('amazon_get'))


@app.route('/magazinevoce')
def magazinei9bux_get():
    delete_product('Magalu.csv')
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "www.magazinevoce.com.br":
       return 'Insira um link válido!'

    filename = crawl_magazinevoce(link,'Magalu')

    if not isinstance(filename, str):
        return f"Um erro aconteceu: {filename}"

    return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', attachment_filename=filename ,as_attachment=True, cache_timeout=-1)


@app.route('/aliexpress')
def aliexpress_download():
    name_file = 'aliexpress.csv'
    delete_product(name_file)
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "pt.aliexpress.com.br":
       return 'Insira um link válido!'

    print('A iniciar processo...')
    # crawl_aliexpress(url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    # return "working..."
    try:
        executor.futures.pop('aliexpress_crawl')
    except Exception:
        pass
    
    executor.submit_stored('aliexpress_crawl', crawl_aliexpress, url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    return redirect(url_for('aliexpress_get'))


@app.get('/aliexpressget')
def aliexpress_get():
    filename = 'aliexpress.csv'

    if not executor.futures.done('aliexpress_crawl'):
        sleep(10)
        return redirect(url_for('aliexpress_get')) 

    future = executor.futures.pop('aliexpress_crawl')    
    if os.path.exists(filename):
        print(future.result())
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', attachment_filename=filename ,as_attachment=True, cache_timeout=-1)
    
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"


@app.get('/shopee')
def shopee_download():
    name_file = 'shopee.csv'
    delete_product(name_file)
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "www.shopee.com.br":
       return 'Insira um link válido!'

    print('A iniciar processo...')
    try:
        executor.futures.pop('shopee_crawl')
    except Exception:
        pass
    
    executor.submit_stored('shopee_crawl', crawl_shopee, url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    return redirect(url_for('shopee_get'))


@app.route('/shopeeget')
def shopee_get():
    filename = 'shopee.csv'

    if not executor.futures.done('shopee_crawl'):
        sleep(10)
        return redirect(url_for('shopee_get')) 

    future = executor.futures.pop('shopee_crawl')    
    if os.path.exists(filename):
        print(future.result())
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', attachment_filename=filename ,as_attachment=True, cache_timeout=-1)
    
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"


@app.route('/error')
def error_image():
    filename = 'error.png'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='image/png', attachment_filename=filename, as_attachment=True, cache_timeout=-1)
    
    return "Screenshot nao disponível!"


if __name__ == "__main__":
    app.debug = True
    app.run()
    # crawl_shopee('https://shopee.com.br/Teclado-Gamer-Pro-Blackfire-Semi-Mec%C3%A2nico-Iluminado-Fortrek-i.338036715.5162992400?ads_keyword=pc%20gamer&adsid=3906860&campaignid=2503549&position=1', ROOT_DIR, 'shopee.csv')    
    # crawl_shopee('https://shopee.com.br/Pc-Gamer-Completo-Amd-A6-7480-8gb-Ssd-120gb-Gpu-Radeon-R5-i.383171174.8415105837?position=6', ROOT_DIR, 'shopee.csv')    
