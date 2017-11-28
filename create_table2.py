import psycopg2
import numpy as np
import json

conn = psycopg2.connect("dbname=hubble user=craig password=dumb")
cur = conn.cursor()

##drop  table
#create_table = "drop table if exists test;"
#cur.execute(create_table)
#conn.commit()
#
##create table
#create_table = "create table test( image_id integer, fingerprint_type text, fingerprint json);"
#cur.execute(create_table)
#conn.commit()
#print(conn)
#
##Load the data
#A = np.load('../flask_gui/carina_tsne_coords.npy')
#fingerprints = np.load('/home/craig/Documents/Science/deeplearning/similarity_testing/fingerprints.npy')
#labels = np.load('/home/craig/Documents/Science/deeplearning/similarity_testing/fingerprint_labels.npy')
#
#for ii in range(fingerprints.shape[0]):
#
#    inds = np.nonzero(fingerprints[ii] > 0.01)[0]
#    print('labels {}  values {}'.format(labels[inds].tolist(), fingerprints[ii][inds].tolist()))
#
#    data = {}
#    data['labels'] = labels[inds].tolist()
#    data['values'] = fingerprints[ii][inds].tolist()
#    cur.execute("insert into test values (%s, 'fingerprints', %s)", [ii, json.dumps(data)])
#
#conn.commit()
#
#for ii in range(A.shape[0]):
#    data = {}
#    data['values'] = A[ii].tolist()
#    cur.execute("insert into test values (%s, 'tsne', %s)", [ii, json.dumps(data)])
#conn.commit()

# -----------------------------
#  Test
# -----------------------------

# Get the tsne value from the database
cur.execute("""SELECT fingerprint FROM test WHERE fingerprint_type='fingerprints' and image_id=128;""")
tt = cur.fetchone()[0]
labels = json.dumps(tt['labels'])
print(labels)

#app.curr.execute("select image_id, jaccard_dist from ( select image_id, 1.0 - (coalesce(array_length(array_intersect(array_agg(e::text), array_agg(f::text))::text[], 1),0)::float / coalesce(array_length(array_union(array_agg(e::text), array_agg(f::text))::text[],1),0)::float ) as jaccard_dist from test, json_array_elements(fingerprint->'labels') e, json_array_elements(%s) f group by 1 ) a  ORDER BY a.jaccard_dist DESC LIMIT 10;", [labels])
#cur.execute("select image_id from test, json_array_elements(fingerprint->'labels') e where fingerprint_type='fingerprints' and e::text=%s", [labels])
cur.execute("select image_id from test where fingerprint_type='fingerprints' and (fingerprint->'labels')=%s", [labels])

for row in cur:
    print(row)


cur.close()
conn.close()

# /usr/local/madlib/bin/madpack -p postgres -c postgres@localhost/hubble install

