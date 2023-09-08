import requests
from bs4 import BeautifulSoup
import csv
import datetime
import copy
from mechanize import Browser

# 'b' is a solution to get around blocked sites, found here: https://stackoverflow.com/questions/43440397/requests-using-beautiful-soup-gets-blocked
b = Browser()
b.addheaders = [('Referer', ''), ('User-agent',
                                      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
b.set_handle_robots(False)  

# ------------------------------ BELOW ARE USEFUL FUNCTIONS ---------------------
# function below (url_link) gets and parses url,
# NOTE: the uncommented code is modified code to get around blocked websites that doesn't give Beautiful Soup Access
def url_link(url):
    # response = requests.get(url)
    # html_content = response.text
    # soup = BeautifulSoup(html_content, "html.parser")

    soup = BeautifulSoup(b.response().read(), "html.parser")
    return soup

# gets prices of cryptos


def cryptoPriceUSD(cryptoName, amount):
    url = "https://www.coingecko.com"
    b.open(url + "/en/coins/" + cryptoName.lower())

    try:
        # crypto = url_link(url).find(
        #     'span', class_='tw-text-gray-900 dark:tw-text-white tw-text-3xl')
        crypto = url_link(url).find('main').find(
            'span', {'data-target': 'price.price'})
        crypto_price = crypto.text
        crypto_price_float = (
            float(crypto_price[1:len(crypto_price)].replace(",", "")))
        return (crypto_price_float * amount)
    except:
        return "ERROR: Not found. Ensure to use the crypto name as presented in coingecko's url"

# gets prices of stocks


def stockPriceUSD(tickerSymbol, amount):
    url = "https://finance.yahoo.com/quote/"
    b.open(url + tickerSymbol+"?p="+tickerSymbol+"&.tsrc=fin-srch")

    try:
        stockPrice = url_link(url).find(
            "fin-streamer", attrs={'data-symbol': tickerSymbol}).text
        return round((float(stockPrice)*amount), 2)
    except:
        return "ERROR: Not found. Ensure to use the stock's ticker symbol and it's spelled correctly."

# displays the date and time, to help time stamp the asset prices


def display_date_time():
    current_date_time = datetime.datetime.now()
    date = current_date_time.strftime("%d %B %Y")
    time = current_date_time.strftime("%H:%M:%S")

    return ("Current date and time: " + date + ", " + time)

# Displays loading Message (e.g Loading 1/2... Processing crypto data)


def loadMessage(assetClass, indicator):
    print("\nLoading "+indicator+"... Processing "+assetClass)

# Displays the output data that would be appended (e.g Bitcoin, 0.1, 16523.12 => $ 1652.312)


def printAssetData(toggle, asset_name, amount, price, value):
    if (amount or price) == '':
        print(str(asset_name) + " => $ " + str(value))
    elif toggle == True:

        print((str(asset_name) + ", " + str(amount) +
              ", " + str(price) + " => $ " + str(value)))


# function to read, write or append files
def file_action(asset_data, mode, holdings_and_data):
    if mode == "r":
        with open('input/'+asset_data+"_input.csv", mode, encoding="utf-8") as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):
                if i > 0:
                    holdings_and_data.append(row)

    elif mode == "a" or mode == "w":
        with open('output/'+asset_data+'_output.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerows(holdings_and_data)


# ---------- CODE BELOW HANDLES DATA IN THE INPUT LIST, PROCESSES THE DATA
#             AND UPLOADS THE RESULT IN THE RESPECTIVE OUTPUT FOLDER------------
# toggle to turn on(True)/off(False) printAssetData() function
display_details = True

# contains relevant tags which serve as variable as well
asset_tags = [
    ['crypto', 'cryptos_data', 'crypto_holdings', cryptoPriceUSD],
    ['stock', 'stocks_data', 'stock_holdings', stockPriceUSD],
]

# start and end of the count, enables you to decide whether you
# want to count cryptos alone or just stocks, it is set to count both as default
start = 0
stop = len(asset_tags)

# format for output data
output_data = ["\n", [display_date_time()], ["ASSET CLASS",
                                             "AMOUNT", "PRICE", "VALUE"]]


# for loop to go through all input data, calculate the values using the functions above, and print and upload the result.
for asset_tag in asset_tags[start:stop]:
    # -------------Code below downloads the data (using the file_action() function) from the input folder
    #                into the each asset data(cryptos_data,stocks_data)  in the asset_tag list -----------
    index = asset_tags.index(asset_tag)

    asset_class_tag = asset_tag[0]
    asset_data_tag = asset_tag[1]
    asset_holdings_tag = asset_tag[2]
    price_api_tag = asset_tag[3]

    # turns strings in asset_tag into variables
    exec(f"{asset_data_tag} = copy.deepcopy(output_data)")
    exec(f"{asset_data_tag}[2][0] = asset_class_tag.upper()")
    exec(f"{asset_holdings_tag} = 0")

    asset_data = eval(asset_data_tag)
    asset_holdings = eval(asset_holdings_tag)

    file_action(asset_data_tag, 'r', asset_data)
    loadMessage(asset_data_tag.replace("_", " "),
                "(" + str(index - start + 1)+"/"+str(stop - start)+")")

# -------------Code below calculates the price and value of assets data in the asset_tag
#    and uploads the result information (cryptos_data,stocks_data) into their respective output folder-----------

    for i in range(3, len(asset_data)):

        asset_name = (asset_data)[i][0]
        amount = float((asset_data)[i][1])

        try:
            price = price_api_tag(asset_name, 1)

            value = amount * price
            printAssetData(display_details, asset_name, amount, price, value)

            asset_data[i] = [asset_name, amount, price, value]

            asset_holdings += value
            exec(f"{asset_holdings_tag} += value")
        except:
            continue
    asset_data.append(['TOTAL:', '', '', round((asset_holdings), 2)])
    printAssetData(display_details, 'TOTAL:', '', '', round(asset_holdings, 2))
    file_action(asset_data_tag, 'a', asset_data)

    # calculates and upload the sum total
    if (index == len(asset_tags)-1):
        total_assets_data = [output_data[0], output_data[1], [
            output_data[2][0], output_data[2][-1]]]
        total_holdings = 0
        print(
            "----------------------------------------------------------------------------")
        for asset_tag in asset_tags[start:stop]:
            asset_holdings_tag = asset_tag[2]
            asset_holdings = asset_tag[2]
            asset_holdings = eval(asset_holdings_tag)

            asset_holdings_tag = asset_holdings_tag[0].upper(
            ) + asset_holdings_tag[1:].replace("_h", " H")
            total_assets_data.append(
                [asset_holdings_tag + " Total", asset_holdings])
            total_holdings += asset_holdings

            print(asset_holdings_tag + " ----------> $ " +
                  str(round(asset_holdings, 2)))
        total_assets_data.append(
            ['TOTAL:', '', '', round((total_holdings), 2)])
        file_action('total_assets_data', 'a', total_assets_data)
        print(
            "----------------------------------------------------------------------------")
        print("TOTAL ASSETS  ==========> ",
              '$ ' + str(round(total_holdings, 2)))
