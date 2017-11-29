import psycopg2
import numpy as np

conn = psycopg2.connect("dbname=hubble user=craig password=dumb")
cur = conn.cursor()

create_table = "select fingerprint from fingerprints where image_id={};".format('128')
cur.execute(create_table)
row = cur.fetchone()[0]
print(row)

create_table = """select image_id, fingerprint from fingerprints order by madlib.dist_norm2(fingerprint, '{{{},{}}}');""".format(row[0], row[1])
cur.execute(create_table)
row = cur.fetchone()[0]
print(row)


cur.close()
conn.close()
