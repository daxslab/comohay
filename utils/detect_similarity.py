# our model class used to store articles
from ads.models import Ad
# utility to get connection to the database.
from django.db import connection

def detect_similarity(similarity_limit=0.7, chars_limit=1000, days_limit=3):
    # internal function to process query results and return doublons IDs.
    # this is mandatory because you'll end up with a list like below that need
    # to be purged from duplicated results (again :D)
    #
    # Origin ID | Target ID | Similarity (%)
    # --------- | --------- | --------------
    #        18 |     19    | 0.8
    #        19 |     18    | 0.8
    #        18 |     20    | 0.9
    #        20 |     18    | 0.9

    def get_doublons_ids(data):
        nodes = {}
        good_ids = []
        for n in data:
            if not nodes.get(n[0]):
                nodes[n[0]] = { 'to': n[2], 'date': n[1] }

        for node_id in nodes:
            node = nodes[node_id]
            node_to_id = node['to']
            node_to = nodes[node_to_id]

            if node_to['date'] > node['date']:
                if node_to_id not in good_ids: good_ids.append(node_to_id)
                if node_id in good_ids: good_ids.remove(node_id)
            else:
                if node_to['date'] == node['date']:
                    node_id = max(node_to_id, node_id)
                if not (node_id in good_ids): good_ids.append(node_id)
                if node_to_id in good_ids: good_ids.remove(node_to_id)
        return map(lambda k: k, filter(lambda k: k not in good_ids, nodes))

    # Initialize connection to DB.
    cursor = connection.cursor()

    # Our first query. It's here to:
    # - Use the set_limit function from pg_trgrm to limit similarity results to
    #   a similarity greater than the given `similarity_limit`, by default 0.7
    # - Create the homogenize function to remove punctation, ignore case and
    #   limit the given `t` to the first `c` given characters
    cursor.execute("""
    SELECT set_limit({similarity_limit});
    CREATE OR REPLACE FUNCTION homogenize (t text, c integer)
    RETURNS text as $$
        BEGIN
            RETURN substring(lower(regexp_replace(t, '\W', '', 'g')) for c);
        END;
    $$ language plpgsql;
    """.format(similarity_limit=similarity_limit))

    # the proper similarity detection query
    cursor.execute("""
        SELECT
            -- basic information needed for comparison and result processing
            A.id, A.created_at,
            B.id, B.created_at,
            -- similarity computation useful to debug our query
            similarity(
                homogenize(A.description,{chars_limit}), homogenize(B.description, {chars_limit})
            ) as sim
        FROM ads_ad A
        JOIN ads_ad B
        -- similarity JOIN, notice homogenize usage to ease computation.
        ON  homogenize(A.description, {chars_limit}) <> homogenize(B.description, {chars_limit})
        AND homogenize(A.description, {chars_limit}) %  homogenize(B.description, {chars_limit})
        -- JOIN date limitation
        AND B.created_at <= A.created_at + interval '{days_limit}' day
        AND B.created_at >= A.created_at - interval '{days_limit}' day
        ORDER BY sim DESC;
        """.format(
            days_limit=days_limit,
            chars_limit=chars_limit
        )
    )

    # retrieve results
    results = cursor.fetchall()

    # process them to only have a list of ids
    doublons_ids = get_doublons_ids(results)

    # we then convert those id to models objects and return the result
    return map(lambda pk: Ad.objects.get(pk=pk), doublons_ids)