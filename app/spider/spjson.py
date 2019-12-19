import sys
from app import db

"""
if len(sys.argv) < 2:
    print("Usage: python3 -m spider.spjson http://some.doma.in")
    quit()
domain = sys.argv[1]
"""

def spjson_func(domain, howmany):
    res = db.session.execute("SELECT id FROM webs where url = :wu", {"wu": domain})
    try:
        web_id = next(res)[0]
    except StopIteration:
        print(f"No such domain found in database: {domain}")
        quit()


    print("Creating JSON output on spider.js...")

    res = db.session.execute('''SELECT COUNT(from_id) AS inbound, old_rank, new_rank, id, url
        FROM pages JOIN links ON pages.id = links.to_id
        WHERE html IS NOT NULL AND ERROR IS NULL AND web_id = :wi
        GROUP BY id ORDER BY id,inbound''', {"wi": web_id})

    fhand = open('app/static/spider.js','w')
    nodes = list()
    maxrank = None
    minrank = None
    for row in res :
        nodes.append(row)
        rank = row[2]
        if maxrank is None or maxrank < rank: maxrank = rank
        if minrank is None or minrank > rank : minrank = rank
        if len(nodes) > howmany : break

    if maxrank == minrank or maxrank is None or minrank is None:
        print("Error - please run sprank.py to compute page rank")
        quit()

    fhand.write('spiderJson = {"nodes":[\n')
    count = 0
    map = dict()
    ranks = dict()
    for row in nodes :
        if count > 0 : fhand.write(',\n')
        # print row
        rank = row[2]
        rank = 19 * ( (rank - minrank) / (maxrank - minrank) )
        fhand.write('{'+'"weight":'+str(row[0])+',"rank":'+str(rank)+',')
        fhand.write(' "id":'+str(row[3])+', "url":"'+row[4]+'"}')
        map[row[3]] = count
        ranks[row[3]] = rank
        count = count + 1
    fhand.write('],\n')

    res = db.session.execute(
        '''SELECT DISTINCT from_id, to_id FROM links, pages WHERE links.to_id = pages.id AND pages.web_id = :wi''',
        {"wi": web_id}
    )
    fhand.write('"links":[\n')

    count = 0
    for row in res:
        # print row
        if row[0] not in map or row[1] not in map : continue
        if count > 0 : fhand.write(',\n')
        rank = ranks[row[0]]
        srank = 19 * ( (rank - minrank) / (maxrank - minrank) )
        fhand.write('{"source":'+str(map[row[0]])+',"target":'+str(map[row[1]])+',"value":3}')
        count = count + 1
    fhand.write(']};')
    fhand.close()

    print("Open force.html in a browser to view the visualization")
