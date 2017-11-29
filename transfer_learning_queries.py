  
queries = {  
    'tsne':
        """
SELECT image_id, dist FROM (
    SELECT image_id, madlib.dist_norm2(array_agg(e::text::float), '{{{}, {}}}')  as dist
    FROM test, json_array_elements(fingerprint->'values') e 
    WHERE fingerprint_type='tsne' 
    GROUP BY 1 
) a
ORDER BY a.dist LIMIT 9;
""",

    'tanimoto':
        """
SELECT image_id, dist FROM (
    SELECT image_id, madlib.dist_tanimoto(array_agg(e::text::float), '{{{}, {}}}')  as dist
    FROM test, json_array_elements(fingerprint->'values') e 
    WHERE fingerprint_type='tsne' 
    GROUP BY 1 
) a
ORDER BY a.dist LIMIT 9;
""",

    'norm1':
        """
SELECT image_id, dist FROM (
    SELECT image_id, madlib.dist_norm1(array_agg(e::text::float), '{{{}, {}}}')  as dist
    FROM test, json_array_elements(fingerprint->'values') e 
    WHERE fingerprint_type='tsne' 
    GROUP BY 1 
) a
ORDER BY a.dist LIMIT 9;
""",

    'inf_norm':
        """
SELECT image_id, dist FROM (
    SELECT image_id, madlib.dist_inf_norm(array_agg(e::text::float), '{{{}, {}}}')  as dist
    FROM test, json_array_elements(fingerprint->'values') e 
    WHERE fingerprint_type='tsne' 
    GROUP BY 1 
) a
ORDER BY a.dist LIMIT 9;
""",

    'cosine_similarity':
        """
SELECT image_id, dist FROM (
    SELECT image_id, madlib.cosine_similarity(array_agg(e::text::float), '{{{}, {}}}')  as dist
    FROM test, json_array_elements(fingerprint->'values') e 
    WHERE fingerprint_type='tsne' 
    GROUP BY 1 
) a
ORDER BY a.dist LIMIT 9;
""",

    'jaccard': 
        """ select a.image_id, 
                           a.jaccard_dist from ( 
                               select image_id, 
                                      ( 1.0 - ( 
                                         (select count(*) from ( select unnest(array_agg(e::text)) intersect  select unnest(array_agg(f::text)) ) a )::decimal / 
                                          array_length(array_union(array_agg(e::text), array_agg(f::text)), 1)::decimal ) )::float
                                      as jaccard_dist 
                               from test, 
                                    json_array_elements(fingerprint->'labels') e, 
                                    json_array_elements('{}') f group by 1 
                            ) a  
                        ORDER BY a.jaccard_dist ASC LIMIT 9;"""
}

