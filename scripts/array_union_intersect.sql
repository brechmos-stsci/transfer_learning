CREATE OR REPLACE FUNCTION array_intersect(anyarray, anyarray) 
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT unnest($1) 
               INTERSECT 
               SELECT unnest($2))
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION array_union(anyarray, anyarray) 
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT unnest($1) 
               UNION 
               SELECT unnest($2))
$$ LANGUAGE sql;

select image_id, jaccard_dist from ( select image_id, array_length(array_intersect(array_agg(e::text), '{"\"promontory\"", "c"}'::text[]), 1)::float / array_length(array_union(array_agg(e::text), '{"\"promontory\"", "c"}'::text[]),1)::float as jaccard_dist from test, json_array_elements(fingerprint->'labels') e group by 1 ) a  ORDER BY jaccard_dist DESC LIMIT 10;
