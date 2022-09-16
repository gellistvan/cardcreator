import sys, json, os, requests

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
            cards.append((values[1], (values[0], values[2]) ))
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
                    output.write("<td><div class=\"article\">")
                    if index < len(cards):
                        output.write(cards[index][0])
                    output.write("</div></td>\n")
                output.write("</tr>\n")
            output.write("</table>\n")

            output.write("<table>\n")
            for line in range(4):
                output.write("<tr>\n")
                for item in range(4):
                    index = page*16 + line *4 + 3 - item
                    output.write("<td>")
                    if index < len(cards):
                        output.write("<div class=\"title\">")
                        output.write(cards[index][1][0])
                        output.write("</div><div class=\"definition\">")
                        output.write(cards[index][1][1])
                        output.write("</div>\n")
                    output.write("</td>\n")
                output.write("</tr>\n")
            output.write("</table>\n")
        output.write("</body> </html>\n")

def process_list(input):
    cards = read_entries(input)
    pages = int(len(cards) / 16)  + (0 if len(cards)%16==0 else 1)
    generate_pdf(cards, pages, "./output_" + input + ".html")

process_list(sys.argv[1])

result = json.loads(search("fönster"))
num_results = int(result["n_results"])
for res in result["results"]:
    id = res["id"]
    for sense in res["senses"]:
        print(sense["definition"])

    term = json.loads(retrive(id))
    #print(term)
    print(term["headword"]["pronunciation"]["value"])