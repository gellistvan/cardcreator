import sys, json, os, requests


proxy = 'http://10.66.243.130:8080'

os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:81.0) Gecko/20100101 Firefox/81.0",
    'X-RapidAPI-Key': '38e68a53afmshda5b90ffc32ec9fp1e2949jsnb3210b6ddec5',
    'X-RapidAPI-Host': 'lexicala1.p.rapidapi.com'
}

def search(keyword) :
    filename="./search/" + keyword + ".json"
    if os.path.isfile(filename):
        with open(filename, "r", encoding='utf-8') as file:
            return file.read()

    result = requests.get('https://lexicala1.p.rapidapi.com/search', headers=headers,
                          params={'language': 'sv', 'text': keyword}).text
    with open(filename, "w", encoding='utf-8') as file:
        file.write(result)

    return result


def retrive(r_id):
    filename="./retrieve/" + r_id + ".json"
    if os.path.isfile(filename):
        with open(filename, "r", encoding='utf-8') as file:
            return file.read()

    result = requests.get('https://lexicala1.p.rapidapi.com/entries/' + r_id, headers=headers).text
    with open(filename, "w", encoding='utf-8') as file:
        file.write(result)

    return result


def read_entries(path):
    cards = []
    with open(path, "r", encoding="utf-8") as input:
        input_file = input.readlines()
        for line in input_file:
            values = line.split('\t')
            cards.append((values[0], (values[1], values[2]) ))
    return cards

def generate_pdf(cards, pages, output):
    with open(output, "w", encoding='utf-8') as output:
        output.write("<html><head> <link rel=\"stylesheet\" href=\"cards.css\"> </head><body>\n")
        for page in range(pages) :
            output.write("<table>\n")
            for line in range(4):
                output.write("<tr>\n")
                for item in range(4):
                    index = page*16 + line *4 + item
                    output.write("<td><div class=\"article\"><b>")
                    if index < len(cards):
                        output.write(cards[index][0][0])
                    output.write("</b></div>")
                    # if index < len(cards):
                    #     output.write("\n<div class=\"definition\">")
                    #
                    #     output.write(cards[index][0][1])
                    #     output.write("</div>\n")

                    output.write("</td>\n")
                output.write("</tr>\n")
            output.write("</table>\n")

            output.write("<table>\n")
            for line in range(4):
                output.write("<tr>\n")
                for item in range(4):
                    index = page*16 + line *4 + 3 - item
                    output.write("<td>")
                    if index < len(cards):
                        output.write("<div class=\"title\"><b>")
                        output.write(cards[index][1][0])
                        output.write("</b>")
                        if len(cards[index][1][1]) > 0:
                            if len(cards[index][1][0]) >7:
                                output.write("<br />")
                            output.write("<span class=\"pron\"> [")
                            output.write(cards[index][1][1])
                            output.write("]</span>")
                        output.write("</div><div class=\"definition\">")

                        output.write(cards[index][1][2])
                        output.write("</div>\n")
                    output.write("</td>\n")
                output.write("</tr>\n")
            output.write("</table>\n")
        output.write("</body> </html>\n")

def get_pronunciation(term):
    ett = term.startswith("ett ")
    verb = term.startswith("att ")
    prefix = ""
    descs = []

    if ett or verb:
        term = term[4:]
        prefix = "att " if verb else "ett "

    result = json.loads(search(term))
    num_results = int(result["n_results"])
    pron = []
    i = 1
    if num_results > 0:
        for res in result["results"]:
            id = res["id"]

            #for sense in res["senses"]:
            #    print(sense["definition"])
            pos = res["headword"]["pos"]
            if num_results > 1 and ((verb and pos!="verb") or (ett and pos != "noun")):
                print ("Skipping search result [" + res["headword"]["text"] + "] for search term [" + term +"]")
                continue

            defs = []
            for sense in res["senses"]:
                if "definition" in sense:
                    defs.append(sense["definition"])
            if num_results > 1:
                descs.append("(" + str(i) + ".) " + ", ".join(defs))
                i += 1
            else:
                descs.append(", ".join(defs))

            item = json.loads(retrive(id))
            pron.append(item["headword"]["pronunciation"]["value"])

            if not verb and not ett:
                if pos == "verb" :
                    prefix = "att "
                elif pos == "noun" :
                    infl = item["headword"]["inflections"]
                    if len (infl) > 0 and (len(infl[0]["text"]) - len(term)) >= 2 and infl[0]["text"].endswith("et"):
                        prefix = "ett "


    else:
        print("Entry [" + term + "] not found")

    if len(prefix) > 0:
        term = prefix + term

    # print (term + " [" + "; ".join(descs) + "]")
    return (term, ", ".join(pron), "; ".join(descs))

def preprocess_cards(cards):
    result = []
    for card in cards:
        terms = [x.strip().lower() for x in card[0].split(',')]
        if len(terms) == 1:
             p = get_pronunciation(terms[0])
             result.append(((card[1][0], p[2]), (p[0], p[1], card[1][1])))
        else:
            main_terms = []
            pronounciations = []
            for term in terms:
                (t, p, d) = get_pronunciation(term)
                main_terms.append(t)
                pronounciations.append(p)
            result.append(((card[1][0], d), (", ".join(main_terms), ", ".join(pronounciations), card[1][1])))

    return result

def process_list(input):
    cards = read_entries(input)
    cards = preprocess_cards(cards)
    pages = int(len(cards) / 16)  + (0 if len(cards)%16==0 else 1)
    generate_pdf(cards, pages, "./output_" + input + ".html")

process_list(sys.argv[1])




