from src.utils import find_magalu_images, get_magazine_specs, get_specs
from utils.parser_handler import init_crawler, remove_whitespaces
from utils.file_handler import dataToExcel
from bs4 import NavigableString


def crawl_magazinevoce(url, nameOfFile="Magazinevocê", verbose=False):
    print('> iniciando magazinei9bux crawler...')
    soap = init_crawler(url)

    print('> extraíndo informações...')
    try:
        store = url.split('/')[3]
        title = [element for element in soap.find('h3') if isinstance(element, NavigableString)][0].strip()
        raw_sku = soap.select_one('h3.hide-desktop span.product-sku').text
        sku = raw_sku.split(' ')[-1].replace(')','').strip()
        category = soap.find('a', class_="category").text
        price = str(soap.find('div', class_="p-price").find('strong').text).replace("por", '')
        try:
            raw_tecnical_details = soap.find('table', class_="tab ficha-tecnica")
            tecnical_details = get_specs(raw_tecnical_details)
        
        except Exception:
            tecnical_details = ""

        specs = get_magazine_specs(soap)
        description = soap.find('table', class_="tab descricao").text
        galery = find_magalu_images(soap) # soap.find('div', class_="pgallery").find('img')['src'] 

    except Exception: 
        print('> Falha ao extrair dados! contate do administrador do sistema...')
        # return

    details = dict()
    details['Sku'] = [remove_whitespaces(sku)]
    details['Type'] = ["external"]
    details['Nome'] = [title]
    details['Categorias'] = [f"{store} > {category}"]
    details['Preço'] = [f"{remove_whitespaces(price)} (Valor aproximado)"]
    details['Url Externa'] = [url]
    details['Texto do botão'] = ["Ver produto"]
    details['Short description'] = [specs]
    details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição\n\n{tecnical_details}"]
    details['Imagens'] = [galery]

    if verbose:
        [print(f"{title}: {detail[0]}") for title, detail in details.items()]
    
    print('> Salvando resultados...')
    dataToExcel(details, f'{nameOfFile}.csv')
    return f'{nameOfFile}.csv'