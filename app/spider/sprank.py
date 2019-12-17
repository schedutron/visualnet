import sys
from app import db

"""
if len(sys.argv) < 3:
    print("Usage: python3 -m spider.sprank http://some.doma.in num_iterations")
    quit()
domain, num_iterations = sys.argv[1], int(sys.argv[2])
"""
def sprank_func(domain, num_iterations):
    res = db.session.execute("SELECT id FROM webs where url = :wu", {"wu": domain})
    try:
        web_id = next(res)[0]
    except StopIteration:
        print("No such domain found in database")
        quit()


    # Find the ids that send out page rank - we only are interested
    # in pages that have in and out links
    res = db.session.execute(
        '''SELECT DISTINCT from_id FROM links, pages WHERE from_id = pages.id AND pages.web_id = :wi''',
        {"wi": web_id}
    )
    from_ids = [row[0] for row in res]

    # Find the ids that receive page rank
    to_ids = list()
    links = list()
    res = db.session.execute(
        '''SELECT DISTINCT from_id, to_id FROM links, pages WHERE from_id = pages.id AND pages.web_id = :wi''',
        {"wi": web_id}
    )
    for row in res:
        from_id = row[0]
        to_id = row[1]
        if from_id == to_id : continue
        if from_id not in from_ids : continue
        if to_id not in from_ids : continue
        links.append(row)
        if to_id not in to_ids : to_ids.append(to_id)

    # Get latest page ranks for strongly connected component
    res = db.session.execute(
            '''SELECT id, new_rank FROM pages WHERE id IN :nodes AND web_id = :wi''',
            {"nodes": tuple(from_ids), "wi": web_id}
        )
    prev_ranks = {row[0]: row[1] for row in res}


    if num_iterations < 1: num_iterations = 1

    # Sanity check
    if len(prev_ranks) < 1 :
        print("Nothing to page rank. Check data.")
        quit()

    # Lets do Page Rank in memory so it is really fast
    for i in range(num_iterations):
        # print prev_ranks.items()[:5]
        next_ranks = dict();
        total = 0.0
        for (node, old_rank) in list(prev_ranks.items()):
            total = total + old_rank
            next_ranks[node] = 0.0
        # print total

        # Find the number of outbound links and sent the page rank down each
        for (node, old_rank) in list(prev_ranks.items()):
            # print node, old_rank
            give_ids = list()
            for (from_id, to_id) in links:
                if from_id != node : continue
            #  print '   ',from_id,to_id

                if to_id not in to_ids: continue
                give_ids.append(to_id)
            if ( len(give_ids) < 1 ) : continue
            amount = old_rank / len(give_ids)
            # print node, old_rank,amount, give_ids

            for id in give_ids:
                next_ranks[id] = next_ranks[id] + amount

        newtot = 0
        for (node, next_rank) in list(next_ranks.items()):
            newtot = newtot + next_rank
        evap = (total - newtot) / len(next_ranks)

        # print newtot, evap
        for node in next_ranks:
            next_ranks[node] = next_ranks[node] + evap

        newtot = 0
        for (node, next_rank) in list(next_ranks.items()):
            newtot = newtot + next_rank

        # Compute the per-page average change from old rank to new rank
        # As indication of convergence of the algorithm
        totdiff = 0
        for (node, old_rank) in list(prev_ranks.items()):
            new_rank = next_ranks[node]
            diff = abs(old_rank-new_rank)
            totdiff = totdiff + diff

        avediff = totdiff / len(prev_ranks)
        print((i+1, avediff))

        # rotate
        prev_ranks = next_ranks

    # Put the final ranks back into the database
    print(list(next_ranks.items())[:5])
    db.session.execute(
        '''UPDATE pages SET old_rank=new_rank WHERE web_id = :wi''',
        {"wi": web_id}
        )
    for (id, new_rank) in list(next_ranks.items()) :
        db.session.execute(
            '''UPDATE pages SET new_rank=:nr WHERE id=:id''',
            {"nr": new_rank, "id": id}
        )
    db.session.commit()
