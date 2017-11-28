import psycopg2
import numpy as np

conn = psycopg2.connect("dbname=hubble user=craig password=dumb")
cur = conn.cursor()

##drop  table
#create_table = "drop table if exists fingerprints;"
#cur.execute(create_table)
#conn.commit()

#create table
#create_table = "create table fingerprints( image_id integer, fingerprint_type text, fingerprint float8[]);"
#cur.execute(create_table)
#conn.commit()
#print(conn)

#Load the data
#A = np.load('../flask_gui/carina_tsne_coords.npy')
#images = np.load('../flask_gui/carina_224.npy')
fingerprints = np.load('/home/craig/Documents/Science/deeplearning/similarity_testing/fingerprints.npy')

for ii in range(fingerprints.shape[0]):
    create_table = "insert into fingerprints values ({}, 'fingerprints', 'U {} V');".format(ii, ','.join(['{}'.format(x) for x in fingerprints[ii]]))
    create_table = create_table.replace('U', '{').replace('V', '}')
    cur.execute(create_table)
    conn.commit()

#for ii in range(A.shape[0]):
#    create_table = "insert into fingerprints values ({}, 'tsne', 'U {}, {} V');".format(ii, A[ii,0], A[ii,1])
#    create_table = create_table.replace('U', '{').replace('V', '}')
#    cur.execute(create_table)
#    conn.commit()
#
#    np.save('data/image_{}.npy'.format(ii), images[:,:,:,ii])    

cur.close()
conn.close()

# /usr/local/madlib/bin/madpack -p postgres -c postgres@localhost/hubble install

